"""End-to-end checks against a loaded database: the app must not fail and its figures must match plain SQL.

    DATABASE_URL="postgresql://payments:payments@localhost:5432/payments" python -m unittest tests.test_app
Skipped when no database is configured (the database comes from the payments-data-platform repository).
"""
import os
import pathlib
import unittest

import psycopg
from streamlit.testing.v1 import AppTest

URL = os.environ.get('DATABASE_URL')
ENTRY = str(pathlib.Path(__file__).resolve().parents[1] / 'streamlit_app.py')


def money(x):
    return f'$ {x:,.0f}'


def kpis(at):
    return [(m.label, m.value) for m in at.metric]


@unittest.skipUnless(URL, 'DATABASE_URL not set')
class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con = psycopg.connect(URL)

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def run_app(self):
        at = AppTest.from_file(ENTRY, default_timeout=60).run()
        self.assertFalse(at.exception, at.exception)
        return at

    def test_orders_page_matches_sql(self):
        at = self.run_app()
        n, total = self.con.execute("SELECT count(*), sum(importe_total) FROM pagos.v_orden_pago "
                                    "WHERE estado IN ('pendiente','pagada')").fetchone()
        pending = self.con.execute("SELECT sum(importe_total) FROM pagos.v_orden_pago WHERE estado='pendiente'").fetchone()[0]
        shown = dict(kpis(at))
        self.assertEqual(shown['Orders'], f'{n:,}')
        self.assertEqual(shown['Total'], money(total))
        self.assertEqual(shown['Pending'], money(pending))

    def test_statement_page_matches_sql(self):
        supplier, pending, total, n = self.con.execute(
            "SELECT proveedor, sum(pendiente), sum(importe_total), count(*) FROM pagos.v_estado_cuenta_proveedor "
            "GROUP BY proveedor HAVING sum(pendiente) > 0 ORDER BY sum(pendiente) DESC LIMIT 1").fetchone()
        at = self.run_app().switch_page('pages/statement.py').run()
        self.assertFalse(at.exception, at.exception)
        at.main.selectbox[0].select(supplier).run()           # the supplier picker (the company filter lives in the sidebar)
        shown = dict(kpis(at))
        self.assertEqual(shown['Orders'], str(n))
        self.assertEqual(shown['Pending'], money(pending))
        self.assertEqual(shown['Total (without cancelled)'], money(total))

    def test_due_page_matches_sql(self):
        overdue, n_overdue = self.con.execute("SELECT coalesce(sum(importe_total), 0), count(*) FROM pagos.v_cuentas_a_pagar "
                                              "WHERE situacion = 'vencida'").fetchone()
        soon, n_soon = self.con.execute("SELECT coalesce(sum(importe_total), 0), count(*) FROM pagos.v_cuentas_a_pagar "
                                        "WHERE fecha_vencimiento BETWEEN current_date AND current_date + 15").fetchone()
        at = self.run_app().switch_page('pages/due.py').run()
        self.assertFalse(at.exception, at.exception)
        shown = dict(kpis(at))
        self.assertEqual(shown[f'Overdue ({n_overdue})'], money(overdue))
        self.assertEqual(shown[f'Due in the next 15 days ({n_soon})'], money(soon))

    def test_supplier_filter_never_breaks_the_page(self):
        at = self.run_app()
        at.sidebar.text_input[0].set_value('a').run()
        self.assertFalse(at.exception, at.exception)

    def test_connections_are_read_only(self):
        from app import db
        with db.connect() as con:
            with self.assertRaises(psycopg.errors.ReadOnlySqlTransaction):
                con.execute('CREATE TABLE pagos.should_not_exist (a int)')


if __name__ == '__main__':
    unittest.main()
