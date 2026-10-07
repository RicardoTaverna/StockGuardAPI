# StockGuard API

Small inventory service used by an internal operations team to register SKUs and control stock withdrawals.

## Stack

Python 3.12, FastAPI, Pydantic, SQLAlchemy and SQLite. API documentation is exposed by FastAPI when the application is running.

## Local setup

1. Create and activate a virtual environment.
2. Install `requirements.txt`.
3. Create the local environment file using `.env.example` as reference.
4. Obtain the local credentials/secrets from the project maintainer.
5. Start the API with Uvicorn.

```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The local database is created automatically on application startup.

## Quality checks

```bash
pytest
flake8 app tests
pylint app
mypy app
```

## Authentication

Protected routes use a bearer token. Local credentials are intentionally not stored in the repository. Ask the project maintainer for the development values required by `.env`.

## Notes

This repository represents a small production-style service. Changes should be reviewed considering behavior, business rules, tests and impact outside the modified lines.
