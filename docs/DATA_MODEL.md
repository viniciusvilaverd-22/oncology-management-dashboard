# Analytical Data Model

## Purpose

The application connects operational oncology activity to billing and financial receipt events while keeping each source date semantically distinct.

## Core entities

```text
Patient
  └─ Attendance
      └─ Ambulatory Account
          ├─ Account Items
          ├─ Billing / Invoice Items
          ├─ Remittance
          ├─ Denials
          └─ Receipt Adjustments
              └─ Receipt Events
```

## Operational cohort

The production-oriented views start from oncology attendances and ambulatory account items.

The selected period is applied to the production date. This defines the operational cohort that subsequent account-level analysis follows.

## Billing competence

Billing competence is obtained from the financial/billing layer and is not assumed to be equal to the production month.

This dimension is used to answer which billing competence originated values that were later received.

## Receipt events

Receipt views use the financial receipt date as their native time dimension.

A single account or invoice item can participate in more than one receipt event. Reversed events are excluded from accumulated current-state calculations.

## Balance semantics

The implementation keeps these concepts separate:

- **billed value** — amount associated with the account in the billing layer;
- **financial receipt** — amount registered by the receipt event;
- **base receipt** — receipt value excluding additions when applicable;
- **denial value** — denial/adjustment value represented by the financial source;
- **open financial balance** — remaining amount after accumulated base receipts and applicable denial values.

A simplified account-level expression used by the analytical layer is:

```text
estimated balance = max(billed - accumulated base receipts, 0)

denial-associated balance =
  min(estimated balance, accumulated denial value)

open financial balance =
  max(billed - accumulated base receipts - accumulated denial value, 0)
```

The system does not assume that every difference between billed and received values is a denial.

## Traceability

The API supports drill-down from aggregate metrics to:

1. patient;
2. attendance;
3. account;
4. remittance;
5. receipt event;
6. account items and denial details.

This is intended to make financial indicators auditable rather than purely descriptive.
