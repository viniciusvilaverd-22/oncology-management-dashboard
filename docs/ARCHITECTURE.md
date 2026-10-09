# Architecture

## System boundary

The public repository contains the analytical application and a generic integration contract. The operational ERP remains the system of record, but its concrete adapter, SQL, schema mappings and environment configuration are intentionally private.

```text
Browser
  │
  ▼
React / Vite
  │ JSON over HTTP(S)
  ▼
FastAPI
  ├── Authentication / RBAC
  ├── Service orchestration
  ├── Bounded cache
  ├── Export services
  └── Audit logging
  │
  ▼
Generic integration contract
  │
  └── Private operational adapter (not included)
        │ read-only
        ▼
     Operational ERP
```

## Backend

The backend separates responsibilities into:

- `api/` — HTTP routes and request validation;
- `auth/` — users, roles, sessions and CSRF;
- `integrations/` — public adapter protocol, registry and safe unavailable default;
- `services/` — business orchestration, caching and response semantics;
- `exports/` — PDF, CSV and XML generation.

The public code does not contain operational SQL or ERP table/view mappings. A private package can implement the adapter contract and be loaded through `DATA_ADAPTER=package.module:factory`.

## Frontend

The frontend uses React for the application shell, drill-down flows and analytical views. Expensive datasets are loaded lazily so opening the application does not trigger every available operational read.

The portfolio demo uses deterministic synthetic data and does not require the private adapter.

## Time semantics

Three dates are intentionally treated as separate business dimensions:

1. production date;
2. billing competence;
3. financial receipt date.

The architecture avoids subtracting values merely because they appear inside the same calendar filter. A receipt in a given month may belong to an earlier billing competence.

## Caching

The application uses bounded in-memory caching with TTLs appropriate to each analytical dataset. Single-flight loading prevents equivalent concurrent requests from executing the same expensive operational read simultaneously.

The cache is an optimization layer, not a system of record.

## Security boundary

The web application manages its own users and permissions. The operational integration is read-only and lives outside the public repository. State-changing application endpoints use session authentication and CSRF validation.

Production deployments should use TLS, secure cookies and standard reverse-proxy hardening.
