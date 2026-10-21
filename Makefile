# Usage: make run   (needs the payments database from the payments-data-platform repository, see README)
export DATABASE_URL ?= postgresql://payments:payments@localhost:5432/payments
PY ?= python3

run:           ## start the app on http://localhost:8501
	$(PY) -m streamlit run streamlit_app.py

test:          ## unit tests (no database) + end-to-end checks against the database
	$(PY) -m unittest discover -s tests -t . -v

.PHONY: run test
