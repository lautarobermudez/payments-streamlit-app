# payments-streamlit-app

[![CI](https://github.com/lautarobermudez/payments-streamlit-app/actions/workflows/ci.yml/badge.svg)](https://github.com/lautarobermudez/payments-streamlit-app/actions/workflows/ci.yml)

A small, **read-only** Streamlit app to explore payment orders: search by supplier, see a supplier's statement with its running pending balance, and track what is overdue or due soon. It runs on the PostgreSQL database of [payments-data-platform](https://github.com/lautarobermudez/payments-data-platform), loaded with **synthetic data**.

I built the first version as a quick internal tool for a real team and rebuilt it here as a clean, tested example of how I structure a data app.

## What it shows

- **Three pages:** *Orders* (filters, KPIs, monthly amount, top suppliers), *Supplier statement* (orders with a running pending balance) and *Due dates* (overdue, due in the next N days, no due date loaded).
- **Layers kept apart:** SQL in `app/queries.py`, calculations in `app/metrics.py` (pure functions, no Streamlit), and screens in `app/views/`. Moving the data access behind an API later would only touch `queries.py`.
- **Read-only by construction:** every connection is opened as a read-only transaction, so PostgreSQL itself rejects any write. A test proves it.
- **Reads the views, not the tables:** it queries the ERP-style views (`pagos.v_orden_pago`, `v_estado_cuenta_proveedor`, `v_cuentas_a_pagar`) of the data platform.
- **Tested end to end:** unit tests for the calculations, and tests that run the whole app and compare every KPI with plain SQL. CI runs them on GitHub against a fresh database.

## Run it

1. Create the database with the data platform (needs Docker, `psql` and Python 3.10+):

   ```bash
   git clone https://github.com/lautarobermudez/payments-data-platform
   cd payments-data-platform
   python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
   make up init load        # PostgreSQL in Docker, schema, synthetic data
   cd ..
   ```

2. Start the app:

   ```bash
   git clone https://github.com/lautarobermudez/payments-streamlit-app
   cd payments-streamlit-app
   pip install -r requirements.txt
   make run                  # http://localhost:8501
   ```

   The default connection is `postgresql://payments:payments@localhost:5432/payments`. Set `DATABASE_URL` to use another one.

3. Test: `make test` (the end-to-end tests are skipped when `DATABASE_URL` is not set).

## Project layout

```
streamlit_app.py     entry point: page config and navigation
pages/               one thin script per page (draw the sidebar, call a view)
app/db.py            read-only connection and cached queries
app/queries.py       all SQL, one function per question
app/metrics.py       pure calculations and display labels
app/filters.py       sidebar filters shared by every page
app/views/           the screens
tests/               unit tests and end-to-end checks against the database
```

## Notes

- **Language of the data:** the database keeps its Spanish domain vocabulary (`pendiente`, `pagada`, CUIT, CBU); the app shows English labels.
- **Scope:** this is a viewer. Writing (for example attaching a payment proof and marking an order as paid) would need users, roles and an audit trail, which belong in an API layer; they are not part of this repository.
- **How it was built:** I defined the screens, the metrics and the structure, and used Claude Code to speed up the drafting. I reviewed the result, and the tests compare every figure with SQL.

## License

MIT, see [LICENSE](LICENSE).
