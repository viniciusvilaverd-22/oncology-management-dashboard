# Oncology Management Dashboard

Portfolio version of a healthcare oncology management dashboard built with **FastAPI**, **Oracle**, **React**, **Vite** and **Recharts**.

This public repository is a sanitized demonstration copy. It contains no production credentials, patient data, institutional branding or internal network addresses.

## What it demonstrates

- oncology production and competency tracking;
- financial reconciliation by actual receipt date;
- account, remittance, patient and attendance drill-down;
- denial/glosa analysis and estimated open balance;
- receipt aging indicators;
- role-based access control and session handling;
- CSV, PDF and XML exports;
- backend tests and GitHub Actions CI.

## Architecture

**Backend:** FastAPI + Python + Oracle (read-only)  
**Frontend:** React + Vite + Recharts  
**Authentication:** local application users, session cookies and CSRF protection  
**Deployment examples:** Apache reverse proxy + systemd

The financial flow modeled by the demo follows:

`billing item -> receipt adjustment -> receipt event`

with an invoice/account bridge used to connect receipt events back to accounts, remittances and attendances.

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example ../.env
pytest -q
```

Fill the demo Oracle settings in `.env` only if you want to connect the application to a compatible environment.

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

## Validation

Backend:

```bash
cd backend
pytest -q
```

Frontend:

```bash
cd frontend
npm ci
npm run build
```

CI is defined in `.github/workflows/ci.yml`.

## Security

See [SECURITY.md](SECURITY.md). This repository intentionally excludes `.env`, databases, private keys, exports, production data, caches and build artifacts.

## Portfolio note

Database object names and application logic are kept only to demonstrate the engineering approach. Environment-specific values are placeholders and must be configured separately.
