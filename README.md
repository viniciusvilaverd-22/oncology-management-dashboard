# Oncology Management Dashboard

> Full-stack healthcare operations platform focused on oncology production, billing traceability, financial reconciliation, denials management and account-level auditability.

This repository is a **sanitized portfolio edition** of a production-oriented healthcare analytics system. It preserves the architecture, data-flow design and engineering decisions while excluding credentials, patient data, institutional identifiers, internal network information and environment-specific secrets.

## Overview

Healthcare revenue-cycle data is rarely aligned to a single date or source.

An oncology account may be:

1. produced in one period;
2. billed in another competence;
3. partially received months later;
4. affected by denials;
5. adjusted through multiple financial events.

The core objective of this project is to make that lifecycle **traceable from operational production to financial outcome** without collapsing different business clocks into a misleading single-period view.

The platform therefore treats production, billing competence and receipt date as distinct dimensions and provides drill-down from executive indicators to account-level detail.

## Engineering Goals

The project was designed around six engineering priorities:

- **Financial correctness** — preserve the semantic difference between production date, billing competence and actual receipt date.
- **Traceability** — allow navigation from aggregated indicators to patient, attendance, account, remittance and receipt-event detail.
- **Read-only integration** — consume healthcare ERP data through a private read-only adapter without introducing write risk into the source system.
- **Operational performance** — reduce unnecessary database load through bounded caching, lazy data loading and reusable query layers.
- **Security by design** — local application authentication, role-based access control, session management and CSRF protection.
- **Deployability** — support a conventional Linux deployment model with reverse proxy, application service supervision and CI validation.

## Run the Demo

A deterministic synthetic-data mode is included for portfolio review.

```bash
cd frontend
npm ci
npm run demo
```

Open `http://localhost:4173`.

Docker:

```bash
docker compose -f docker-compose.demo.yml up --build
```

Open `http://localhost:8080`.

See [Portfolio demo guide](docs/DEMO.md).

## Technical Documentation

- [System guide](docs/SYSTEM_GUIDE.md) — public-safe architecture, domain semantics, security, performance, testing and deployment reference.
- [Public/private documentation boundary](docs/PUBLIC_PRIVATE_BOUNDARY.md) — rules for portfolio content, operational runbooks, generic domain naming and publication hygiene.
- [Architecture](docs/ARCHITECTURE.md)
- [Engineering decisions](docs/ENGINEERING_DECISIONS.md)
- [Analytical data model](docs/DATA_MODEL.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## Architecture

```mermaid
flowchart LR
    Browser --> React
    React --> FastAPI
    FastAPI --> Auth[Authentication and RBAC]
    FastAPI --> Cache[Bounded cache]
    FastAPI --> Services
    Services --> Queries
    Queries --> operational data source[(operational data source read-only)]
    FastAPI --> Exports[CSV / PDF / XML]
```

```text
┌───────────────────────────────────────────────┐
│                  React UI                     │
│  dashboards · drill-down · charts · exports  │
└───────────────────────┬───────────────────────┘
                        │ HTTPS / JSON
┌───────────────────────▼───────────────────────┐
│                 FastAPI API                   │
│ auth · RBAC · CSRF · cache · orchestration   │
└───────────────────────┬───────────────────────┘
                        │ read-only
┌───────────────────────▼───────────────────────┐
│                 Operational ERP               │
│ production · billing · receipts · denials    │
└───────────────────────────────────────────────┘
```

### Technology stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Integration | Generic adapter contract; private operational implementation omitted |
| Frontend | React, Vite |
| Visualization | Recharts |
| Authentication | Local application users, secure sessions, CSRF |
| Deployment model | Apache reverse proxy, systemd |
| Testing | Pytest |
| CI | GitHub Actions |

## Financial Data Model

A central challenge was avoiding an incorrect comparison between values that belong to different time dimensions.

The application explicitly separates:

- **Production period** — when oncology activity was produced.
- **Billing competence** — when the account entered the billing cycle.
- **Receipt date** — when the financial system registered a receipt event.
- **Denial value** — the value identified as a denial/adjustment within the financial flow.
- **Open balance** — the remaining amount after accumulated receipts and applicable denial values.

The modeled receipt path follows the equivalent of:

```text
Billing Item
    ↓
Invoice / Account Bridge
    ↓
Receipt Adjustment
    ↓
Receipt Event
```

This allows the interface to answer questions such as:

- Which competence originated a payment?
- In which month was it actually received?
- Was the account paid in one or multiple events?
- How much remains open?
- How much is associated with a denial?
- Which account, remittance and attendance generated the financial event?

## Core Capabilities

### Executive and operational dashboards

- oncology production indicators;
- billing competence analysis;
- receipt metrics;
- aging indicators;
- denial monitoring;
- account status summaries;
- production-to-financial traceability.

### Receipt reconciliation

- receipt-event aggregation;
- competence × receipt-month analysis;
- multiple-payment detection;
- account-level accumulated receipts;
- receipt aging and percentile indicators;
- drill-down into the composition of each receipt event.

### Account and patient traceability

The operational navigation model follows:

```text
Patient
  → Attendance
    → Account
      → Remittance
        → Receipt Event
          → Denial
            → Current Balance
```

This enables analysts to move from a high-level KPI to the exact financial and operational records that compose it.

### Denials

The application supports:

- denial totals by reason;
- account-level denial detail;
- denial status classification;
- current open-balance analysis;
- historical comparison against received values.

### Exports

Supported reporting workflows include:

- CSV exports;
- PDF reports;
- XML exports.

## Key Engineering Challenges

### 1. Different business clocks

The largest modeling risk was treating production, billing and receipt as if they belonged to the same accounting period.

**Approach:** each metric retains its native reference date and is only compared when the business relationship is valid.

### 2. Partial and delayed payments

A single account may be paid across several receipt events and several months.

**Approach:** receipt events are accumulated by account while preserving the individual event history.

### 3. operational data query cost

Operational healthcare schemas can produce expensive joins and repeated reads.

**Approach:**

- lazy loading for heavy drill-downs;
- bounded in-memory cache;
- cache TTLs by query type;
- single-flight protection to avoid duplicate concurrent loads;
- explicit row limits for analytical detail endpoints.

### 4. Safe ERP integration

The application consumes production ERP data but must not become a write path into the hospital database.

**Approach:** the private operational adapter is designed as **read-only**.

### 5. Access control

Financial and patient-related operational views require controlled access.

**Approach:**

- authenticated sessions;
- role-based access control;
- CSRF validation for state-changing application operations;
- password hashing with `scrypt`;
- audit events for authentication and administrative actions.

## Security Model

The public portfolio repository intentionally excludes:

- `.env` files;
- operational adapter credentials;
- database files;
- session databases;
- private keys and certificates;
- production exports;
- patient data;
- internal IP addresses and DNS names;
- production logs and backups.

Environment-specific configuration must be supplied locally.

## Performance Strategy

The backend uses a lightweight application-level performance strategy suitable for an internal analytical system:

- bounded cache entries;
- TTL-based invalidation;
- single-flight loading;
- lazy frontend queries;
- explicit limits on large detail endpoints;
- client-side filtering for already-loaded analytical datasets.

The frontend avoids loading every expensive dataset at startup. Heavy account, patient and event details are requested only when the corresponding view or drill-down is opened.

## Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── db/
│   │   ├── exports/
│   │   ├── queries/
│   │   └── services/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── public/
│   └── src/
├── deploy/
├── .github/
│   └── workflows/
├── .env.example
├── SECURITY.md
└── README.md
```

## Local Development

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

The public repository does not include the operational adapter. Private deployments provide it separately through `DATA_ADAPTER=package.module:factory`.

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

### Production build

```bash
cd frontend
npm ci
npm run build
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

The CI pipeline validates backend tests and the frontend production build on repository changes.

## Design Principles

- Preserve business semantics before optimizing presentation.
- Never infer a bank-credit date from a billing date.
- Do not label billed value as operational cost.
- Keep denial and outstanding balance as separate concepts.
- Prefer auditable account-level drill-down over opaque aggregate KPIs.
- Keep the operational adapter read-only.
- Expose technical assumptions in code and documentation.

## Portfolio Context

This project demonstrates practical software engineering applied to a complex healthcare revenue-cycle problem: integrating operational and financial data, preserving date semantics, securing access, optimizing repeated queries and presenting the result through an auditable analytical interface.

The public version is intentionally decoupled from any specific healthcare institution and contains no production data.

## License

This project is licensed under the [MIT License](LICENSE).
