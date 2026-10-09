# Architecture

## System boundary

The application is an analytical layer over a healthcare ERP. Oracle remains the system of record and is accessed in read-only mode.

```text
Browser
  │
  ▼
React / Vite
  │ JSON over HTTP(S)
  ▼
FastAPI
  ├── Authentication / RBAC
  ├── Query orchestration
  ├── Bounded cache
  ├── Export services
  └── Audit logging
  │
  ▼
Oracle (read-only)
```

## Backend

The backend separates responsibilities into:

- `api/` — HTTP routes and request validation;
- `auth/` — users, roles, sessions and CSRF;
- `db/` — Oracle access;
- `queries/` — SQL grouped by business domain;
- `services/` — orchestration, caching and response semantics;
- `exports/` — PDF, CSV and XML generation.

## Frontend

The frontend uses React for the application shell, drill-down flows and analytical views. Expensive datasets are loaded lazily so opening the application does not trigger every available Oracle query.

## Time semantics

Three dates are intentionally treated as separate business dimensions:

1. production date;
2. billing competence;
3. financial receipt date.

The architecture avoids subtracting values merely because they appear inside the same calendar filter. A receipt in a given month may belong to an earlier billing competence.

## Caching

The application uses bounded in-memory caching with TTLs appropriate to each analytical query. Single-flight loading prevents equivalent concurrent requests from executing the same expensive database read simultaneously.

The cache is an optimization layer, not a system of record.

## Security boundary

The web application manages its own users and permissions while the source ERP integration remains read-only. State-changing application endpoints use session authentication and CSRF validation.

Production deployments should use TLS, secure cookies and standard reverse-proxy hardening.
