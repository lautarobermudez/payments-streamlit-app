# Contributing

- Work on a feature branch and open a pull request into `main`; CI must be green.
- Keep the layers apart: SQL in `app/queries.py`, calculations in `app/metrics.py`, screens in `app/views/`. A new screen should not contain SQL, and a calculation should not import Streamlit.
- Add a unit test for every calculation (`tests/test_metrics.py`) and, for a new page, a check against plain SQL (`tests/test_app.py`).
- Never commit real data. The app only works with the synthetic database of the payments-data-platform repository.
