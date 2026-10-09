# Engineering Decisions

This document records the main architectural decisions behind the portfolio edition.

## 1. Keep the source ERP read-only

**Decision:** Oracle access is read-only.

**Reasoning:** The application is an analytical and reconciliation layer. Write access would increase operational risk and blur the boundary between the dashboard and the system of record.

**Consequence:** Administrative state such as users, sessions and audit events is stored separately from the ERP data source.

## 2. Preserve independent business dates

**Decision:** Production date, billing competence and receipt date are modeled independently.

**Reasoning:** A receipt recorded in one month can settle an account billed in a previous competence. Comparing only calendar-aligned totals can therefore produce misleading financial conclusions.

**Consequence:** APIs and UI labels state which date drives each period filter.

## 3. Accumulate receipt events by account

**Decision:** Account status uses accumulated non-reversed receipt events rather than only receipts inside the selected production period.

**Reasoning:** Partial and delayed payments are normal revenue-cycle events.

**Consequence:** The application can distinguish received value, denial value and open financial balance without treating every difference as a denial.

## 4. Load expensive detail on demand

**Decision:** Detailed accounts, patients and receipt-event compositions are lazy-loaded.

**Reasoning:** Executive dashboards do not need every analytical row at startup.

**Consequence:** Initial database pressure is reduced and users only pay the cost of detailed queries when they open those views.

## 5. Use bounded application caching

**Decision:** Repeated analytical reads use an in-memory cache with TTL, a maximum entry count and single-flight loading.

**Reasoning:** Repeated Oracle queries for the same period are expensive, while the dashboard does not require millisecond-level source freshness.

**Consequence:** The cache improves responsiveness without becoming a system of record.

## 6. Separate authorization from database identity

**Decision:** Application users and roles are managed by the application rather than exposing Oracle credentials to end users.

**Reasoning:** Operational access needs role-based controls that are independent from the technical database account.

**Consequence:** The application implements local users, sessions, RBAC and CSRF validation.

## 7. Make public-repository hygiene testable

**Decision:** CI checks both build correctness and repository hygiene.

**Reasoning:** A public portfolio should fail fast if private environment files, key material or known internal identifiers are accidentally committed.

**Consequence:** Repository-quality checks run beside backend tests and the frontend production build.
