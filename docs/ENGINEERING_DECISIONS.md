# Engineering Decisions

This document records the main architectural decisions behind the portfolio edition.

## 1. Keep the source ERP read-only and private

**Decision:** operational data access is provided by a private read-only adapter that is not shipped in this repository.

**Reasoning:** the application is an analytical and reconciliation layer. Publishing schema mappings or write-capable integration code would increase operational and disclosure risk.

**Consequence:** the public backend depends on a small adapter contract. Without a private implementation, operational endpoints fail safely while the synthetic demo remains usable.

## 2. Preserve independent business dates

**Decision:** production date, billing competence and receipt date are modeled independently.

**Reasoning:** a receipt recorded in one month can settle an account billed in a previous competence. Comparing only calendar-aligned totals can therefore produce misleading financial conclusions.

**Consequence:** APIs and UI labels state which date drives each period filter.

## 3. Accumulate receipt events by account

**Decision:** account status uses accumulated receipt events rather than a single paid/unpaid flag.

**Reasoning:** partial and delayed payments are normal revenue-cycle events.

**Consequence:** the application can distinguish received value, adjustment value and open financial balance without treating every difference as an adjustment.

## 4. Load expensive detail on demand

**Decision:** detailed accounts, patients and receipt-event compositions are lazy-loaded.

**Reasoning:** executive dashboards do not need every analytical row at startup.

**Consequence:** initial pressure on the operational source is reduced and users only pay the cost of detailed reads when they open those views.

## 5. Use bounded application caching

**Decision:** repeated analytical reads use an in-memory cache with TTL, a maximum entry count and single-flight loading.

**Reasoning:** repeated operational reads for the same period are expensive, while the dashboard does not require millisecond-level source freshness.

**Consequence:** the cache improves responsiveness without becoming a system of record.

## 6. Separate authorization from integration identity

**Decision:** application users and roles are managed by the application rather than exposing technical integration credentials to end users.

**Reasoning:** operational access needs role-based controls that are independent from the private adapter identity.

**Consequence:** the application implements local users, sessions, RBAC and CSRF validation.

## 7. Make public-repository hygiene testable

**Decision:** CI checks both build correctness and repository hygiene.

**Reasoning:** a public portfolio should fail fast if private environment files, personal names, operational identifiers or known integration artifacts are accidentally committed.

**Consequence:** repository-quality checks run beside backend tests and the frontend production build.
