# Changelog

All notable changes to the public portfolio edition are documented here.

## 0.7.0 — Public adapter boundary

### Architecture

- removed the executable operational database driver and embedded operational SQL implementation from the public repository;
- introduced a generic integration contract under `backend/app/integrations/`;
- made the private operational adapter an external dependency loaded through `DATA_ADAPTER=package.module:factory`;
- kept operational reads explicitly unavailable when no private adapter is installed;
- preserved the deterministic synthetic demo as an independent public review path.

### Public contract

- replaced operational aliases in the public API/demo contract with generic identifiers such as `account_id`, `patient_id`, `encounter_id`, `billing_batch_id`, `receipt_event_id` and `invoice_item_id`;
- documented the public/private boundary for ERP mappings, SQL, credentials, environment details and runbooks;
- aligned the README and system guide with the adapter-based architecture.

### Repository hygiene

- removed personal attribution from versioned public content;
- removed empty legacy `db/`, `queries/` and `models/` packages;
- added CI guards for personal-name references, known private-adapter identifiers, sensitive files and common secret patterns;
- unified the public application version at `0.7.0`.

### Validation

The release candidate is required to pass repository hygiene, backend lint/tests, frontend demo tests, production build, synthetic demo build and demo-container build.

## 2026-10-09 — Portfolio hardening

### Added

- deterministic synthetic-data demo mode;
- one-command local demo through `npm run demo`;
- containerized demo through Docker Compose;
- backend authentication, cache and domain-logic tests;
- conservative Python linting with Ruff;
- CI checks for repository hygiene, backend quality, production build, demo build and demo container;
- architecture, data-model, engineering-decision and demo documentation;
- automated dependency update policy.

### Improved

- frontend vendor bundle splitting;
- README architecture and runnable-demo guidance;
- security checks for accidental publication of credentials, private key material and internal environment references.

### Safety

The public demo uses fictional people, accounts, financial events and values. Environment-specific credentials and operational data are not part of the repository.
