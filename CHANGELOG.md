# Changelog

All notable changes to the public portfolio edition are documented here.

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
