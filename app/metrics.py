"""Pure calculations on DataFrames: no Streamlit, no database, easy to test."""
import datetime as dt

import pandas as pd

STATUS_LABELS = {'pendiente': 'Pending', 'pagada': 'Paid', 'anulada': 'Cancelled'}
SITUATION_LABELS = {'vencida': 'Overdue', 'vence hoy': 'Due today', 'a vencer': 'Upcoming', 'sin vencimiento': 'No due date'}
COLUMN_LABELS = {
    'empresa': 'Company', 'nro_op': 'OP no.', 'fecha_op': 'Date', 'proveedor': 'Supplier',
    'forma_pago': 'Payment method', 'estado': 'Status', 'fecha_vencimiento': 'Due date',
    'fecha_pago': 'Payment date', 'importe_total': 'Amount', 'pendiente': 'Pending',
    'pendiente_acumulado': 'Running pending', 'dias_al_vencimiento': 'Days to due date', 'situacion': 'Situation',
}


def money(x: float) -> str:
    return f'$ {x:,.0f}'


def label_columns(df: pd.DataFrame) -> pd.DataFrame:
    """English headers and status/situation labels for display (the database keeps its own vocabulary)."""
    out = df.rename(columns=COLUMN_LABELS)
    if 'Status' in out:
        out['Status'] = out['Status'].map(STATUS_LABELS).fillna(out['Status'])
    if 'Situation' in out:
        out['Situation'] = out['Situation'].map(SITUATION_LABELS).fillna(out['Situation'])
    return out


def order_kpis(df: pd.DataFrame, today: dt.date) -> dict:
    """Count, total, pending and overdue amounts of a set of orders (overdue = pending with due date before today)."""
    pending = df[df.estado == 'pendiente']
    overdue = pending[pending.fecha_vencimiento.notna() & (pending.fecha_vencimiento < today)]
    return {'orders': len(df), 'total': df.importe_total.sum(),
            'pending': pending.importe_total.sum(), 'overdue': overdue.importe_total.sum()}


def monthly_totals(df: pd.DataFrame) -> pd.Series:
    month = pd.to_datetime(df.fecha_op).dt.to_period('M').dt.to_timestamp()
    return df.groupby(month)['importe_total'].sum()


def top_suppliers(df: pd.DataFrame, n: int = 8) -> pd.Series:
    return df.groupby('proveedor')['importe_total'].sum().sort_values(ascending=False).head(n)


def statement_kpis(df: pd.DataFrame) -> dict:
    return {'orders': len(df), 'total': df.importe_total.sum(),
            'paid': df[df.estado == 'pagada'].importe_total.sum(), 'pending': df.pendiente.sum()}


def due_buckets(df: pd.DataFrame, days: int) -> dict[str, pd.DataFrame]:
    """Split the payables into overdue, due within `days` days, and without a due date."""
    has_date = df.fecha_vencimiento.notna()
    return {
        'overdue': df[df.situacion == 'vencida'],
        'soon': df[has_date & (df.dias_al_vencimiento >= 0) & (df.dias_al_vencimiento <= days)],
        'no_date': df[df.situacion == 'sin vencimiento'],
    }
