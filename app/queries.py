"""All SQL lives here, one function per question. Amounts are cast to float for charts.

The app only reads the ERP-style views of the data platform (schema `pagos`), never raw tables.
"""
import pandas as pd

from app.db import query

ALL = 'All'


def companies() -> list[str]:
    return query('SELECT nombre FROM pagos.empresa ORDER BY nombre')['nombre'].tolist()


def orders(company: str, statuses: list[str], text: str) -> pd.DataFrame:
    return query('''
        SELECT empresa, nro_op, fecha_op, proveedor, forma_pago, estado, fecha_vencimiento,
               importe_total::float8 AS importe_total
        FROM pagos.v_orden_pago
        WHERE (%(c)s = 'All' OR empresa = %(c)s)
          AND estado = ANY(%(s)s)
          AND proveedor ILIKE %(t)s
        ORDER BY fecha_op DESC, nro_op DESC''', {'c': company, 's': statuses, 't': f'%{text}%'})


def suppliers(company: str, text: str) -> list[str]:
    return query('''
        SELECT DISTINCT proveedor FROM pagos.v_estado_cuenta_proveedor
        WHERE (%(c)s = 'All' OR empresa = %(c)s) AND proveedor ILIKE %(t)s
        ORDER BY proveedor''', {'c': company, 't': f'%{text}%'})['proveedor'].tolist()


def statement(supplier: str, company: str) -> pd.DataFrame:
    return query('''
        SELECT empresa, fecha_op, nro_op, estado, forma_pago, fecha_pago, fecha_vencimiento,
               importe_total::float8 AS importe_total, pendiente::float8 AS pendiente,
               pendiente_acumulado::float8 AS pendiente_acumulado
        FROM pagos.v_estado_cuenta_proveedor
        WHERE proveedor = %(p)s AND (%(c)s = 'All' OR empresa = %(c)s)
        ORDER BY fecha_op, nro_op''', {'p': supplier, 'c': company})


def payables(company: str, text: str) -> pd.DataFrame:
    return query('''
        SELECT empresa, proveedor, nro_op, fecha_op, forma_pago, fecha_vencimiento,
               (fecha_vencimiento - current_date) AS dias_al_vencimiento, situacion,
               importe_total::float8 AS importe_total
        FROM pagos.v_cuentas_a_pagar
        WHERE (%(c)s = 'All' OR empresa = %(c)s) AND proveedor ILIKE %(t)s
        ORDER BY fecha_vencimiento NULLS LAST, nro_op''', {'c': company, 't': f'%{text}%'})
