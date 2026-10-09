# Public / Private Documentation Boundary

This repository is a public portfolio artifact. Its documentation must explain the engineering problem, architecture and design decisions without becoming an operational runbook for a real healthcare environment.

## Public portfolio content

Public material may describe:

- business problem and analytical goals;
- system architecture and data-flow design;
- separation of production, billing competence, remittance and receipt;
- financial traceability and drill-down design;
- authentication, RBAC and CSRF protections;
- caching and performance controls;
- CI, Docker and deployment patterns;
- automated tests and engineering lessons;
- limitations and unresolved design questions.

Public documentation must use generic domain concepts instead of ERP-specific object names.

Recommended domain vocabulary:

```text
OncologySchedule
PatientEncounter
AmbulatoryAccount
BillingBatch
InvoiceItem
ReceiptEvent
ReceiptAdjustment
AppealEvent
PaymentReconciliation
```

Example public flow:

```text
PatientEncounter
    ↓
AmbulatoryAccount
    ↓
BillingBatch
    ↓
ReceiptEvent
    ├── ReceiptAdjustment
    └── AppealEvent
```

## Business-time separation

Production and cash receipt are different business clocks.

```text
Production / competence
PatientEncounter → AmbulatoryAccount → Billing → BillingBatch

Financial / cash
BillingBatch → Settlement → ReceiptEvent → Adjustments → Net amount
```

A billing or remittance date must never be presented as the receipt date unless that relationship is explicitly supported by the financial event model.

## Traceability

Important financial indicators should be explainable through drill-down:

```text
Received amount
    ↓
Billing batches
    ↓
Accounts
    ↓
Patients
    ↓
Encounters
```

Public examples must use synthetic or anonymized data only.

## Billing value is not cost

A billed amount must not be described as hospital cost. Cost terminology is allowed only when a validated cost source exists for the relevant materials, medicines, inventory or acquisition model.

## Content prohibited from public documentation

Do not publish:

- real table or view names from the operational ERP;
- real schema, column, key or internal code mappings;
- homologated production SQL;
- production hosts, DNS names, internal paths or network details;
- credentials, tokens, connection strings or certificates;
- production troubleshooting procedures;
- patient-identifying information;
- names of people;
- screenshots containing operational identifiers or personal information.

When a screenshot is needed, recreate it with synthetic data rather than partially obscuring production data.

## Private runbook

The private operational runbook may contain what is required to operate and audit the real environment, including:

- actual ERP table and view names;
- primary and foreign keys;
- validated source fields and internal codes;
- homologated queries;
- complete financial mappings;
- receipt-source validation;
- denial and appeal rules;
- environment configuration;
- troubleshooting, rollback and recovery procedures;
- incident history and operational limitations.

The private runbook must not be copied into this public repository.

## Architectural boundary

Public application and domain documentation should depend on generic concepts:

```text
Application
    ↓
Domain
    ↓
Integration Interface
    ↓
Private ERP Adapter
    ↓
Operational ERP
```

The mapping between a generic domain object and an operational ERP object belongs to the private adapter/runbook boundary, not to the public domain contract.

## Publication checklist

Before publishing documentation, examples, logs, screenshots or exported reports, verify that they contain no:

- personal names;
- patient data;
- account or encounter identifiers from production;
- ERP table/view/column names;
- SQL from the operational environment;
- hosts, URLs, paths or infrastructure identifiers;
- credentials, tokens or secrets.

The public artifact should explain **what problem was solved and how the engineering works**. The private runbook should explain **how the real environment is mapped, operated and recovered**.
