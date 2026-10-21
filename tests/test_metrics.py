"""Unit tests for the pure calculations (no database, no Streamlit)."""
import datetime as dt
import unittest

import pandas as pd

from app import metrics

TODAY = dt.date(2026, 10, 21)


def orders_frame():
    return pd.DataFrame({
        'proveedor': ['A', 'A', 'B', 'C'],
        'estado': ['pendiente', 'pagada', 'pendiente', 'pendiente'],
        'fecha_op': [dt.date(2026, 9, 1), dt.date(2026, 9, 15), dt.date(2026, 10, 2), dt.date(2026, 10, 3)],
        'fecha_vencimiento': [dt.date(2026, 10, 1), None, dt.date(2026, 11, 1), None],
        'importe_total': [100.0, 50.0, 200.0, 25.0],
    })


class KpiTests(unittest.TestCase):
    def test_order_kpis(self):
        k = metrics.order_kpis(orders_frame(), TODAY)
        self.assertEqual(k, {'orders': 4, 'total': 375.0, 'pending': 325.0, 'overdue': 100.0})

    def test_orders_without_due_date_are_never_overdue(self):
        k = metrics.order_kpis(orders_frame().iloc[[3]], TODAY)
        self.assertEqual(k['overdue'], 0)

    def test_money_format(self):
        self.assertEqual(metrics.money(1234567.4), '$ 1,234,567')

    def test_monthly_totals_group_by_month(self):
        m = metrics.monthly_totals(orders_frame())
        self.assertEqual(m.tolist(), [150.0, 225.0])
        self.assertEqual(list(m.index), ['2026-09', '2026-10'])

    def test_top_suppliers_sorted_and_limited(self):
        top = metrics.top_suppliers(orders_frame(), n=2)
        self.assertEqual(list(top.index), ['B', 'A'])


class LabelTests(unittest.TestCase):
    def test_headers_and_status_are_translated_but_data_is_not_changed(self):
        original = orders_frame()
        shown = metrics.label_columns(original)
        self.assertIn('Supplier', shown.columns)
        self.assertEqual(shown['Status'].tolist(), ['Pending', 'Paid', 'Pending', 'Pending'])
        self.assertEqual(original['estado'].tolist()[0], 'pendiente')   # input untouched


class MissingValueTests(unittest.TestCase):
    def test_missing_op_number_and_dates_are_real_nulls_not_the_text_none(self):
        df = pd.DataFrame({'nro_op': [5, None], 'fecha_op': [dt.date(2026, 1, 2), dt.date(2026, 1, 3)],
                           'fecha_vencimiento': [None, dt.date(2026, 2, 1)]})
        shown = metrics.label_columns(df)
        self.assertTrue(pd.isna(shown['OP no.'].iloc[1]))
        self.assertEqual(str(shown['OP no.'].dtype), 'Int64')
        self.assertTrue(pd.isna(shown['Due date'].iloc[0]))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(shown['Due date']))


class DueTests(unittest.TestCase):
    def frame(self):
        return pd.DataFrame({
            'situacion': ['vencida', 'a vencer', 'a vencer', 'sin vencimiento'],
            'fecha_vencimiento': [dt.date(2026, 10, 1), dt.date(2026, 10, 25), dt.date(2026, 12, 1), None],
            'dias_al_vencimiento': [-20, 4, 41, None],
            'importe_total': [10.0, 20.0, 30.0, 40.0],
        })

    def test_buckets(self):
        b = metrics.due_buckets(self.frame(), days=15)
        self.assertEqual(b['overdue'].importe_total.sum(), 10.0)
        self.assertEqual(b['soon'].importe_total.sum(), 20.0)      # only the one within 15 days
        self.assertEqual(b['no_date'].importe_total.sum(), 40.0)

    def test_wider_window_includes_more(self):
        self.assertEqual(metrics.due_buckets(self.frame(), days=60)['soon'].importe_total.sum(), 50.0)


class StatementTests(unittest.TestCase):
    def test_statement_kpis(self):
        df = pd.DataFrame({'estado': ['pagada', 'pendiente'], 'importe_total': [70.0, 30.0], 'pendiente': [0.0, 30.0]})
        self.assertEqual(metrics.statement_kpis(df), {'orders': 2, 'total': 100.0, 'paid': 70.0, 'pending': 30.0})


if __name__ == '__main__':
    unittest.main()
