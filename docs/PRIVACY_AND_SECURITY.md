# PayPath MSME — Privacy, Data Protection & Commercial Safeguards

## 1. Core Data Ethics Principles

As an application handling commercial receivables, buyer records, and pre-litigation documentation, PayPath MSME adheres to strict data ethics and privacy boundaries:

1. **Zero Exploitation of Financial Distress**:
   Under no circumstances are unpaid invoice amounts, delinquency durations, buyer identities, or dispute records used to target advertisements, score credit, or enrich external parties.
2. **Voluntary Contextual Advertising**:
   B2B supplier recommendations are matched solely on voluntary company profile attributes:
   - Primary Manufacturing Industry Category (e.g., `garment_manufacturing`, `packaging`).
   - Declared Material Purchasing Interests (e.g., `polyester thread`, `cotton twill`, `corrugated boxes`).
3. **Explicit Consent-Gated Lead Sharing**:
   No commercial enquiry or contact detail is transmitted to a supplier without explicit, deliberate user action and confirmation of the consent checkbox.
4. **Segregation of Advertising & Debt Recovery**:
   The B2B supplier discovery service operates with zero read access to the invoice or escalation case tables.

---

## 2. Information Handled & Classification

| Data Category | Examples | Sensitivity | Permitted Use |
|---|---|---|---|
| **Enterprise Identity** | Legal Name, Udyam Number, GSTIN, State | Public / Commercial | Case reports, statutory legal calculations, MSEFC documentation |
| **Debtor Records** | Buyer Company, Contact Email, Agreed Terms | Confidential Commercial | Private case escalation, notice dispatch, report generation |
| **Ledger Transactions** | Invoice Total, Payments Received, Balance | Confidential Commercial | Accounting reconciliation, interest computation |
| **Evidence Artifacts** | Tax Invoices, Delivery Challans, POs | Confidential Commercial | MSEFC readiness audit, pre-litigation package compilation |
| **Contextual Discovery** | Industry Type, Material Tags | Public Commercial | Recommending relevant wholesale suppliers |
| **Supplier Enquiries** | Product Quantity, Contact Person, Message | Consented Commercial | Direct transmission to the chosen supplier upon user consent |

---

## 3. Prototype Security Controls & Safeguards

- **Input Sanitization & Type Validation**: Enforced via Pydantic v2 schemas and SQLAlchemy parameterized queries to prevent SQL injection and malformed inputs.
- **In-Memory & Streaming File Processing**: ReportLab generates PDF streams directly in memory without writing unencrypted temporary files to public web roots.
- **Explicit Invariant Enforcement**: Database layer and domain services prevent invalid business states (negative balances, payments exceeding outstanding balances, duplicate invoice numbers).
- **Graceful Legal Engine States**: Incomplete transaction evidence produces explicit "Needs verification" or "Additional information required" warnings rather than misleading definitive legal conclusions.

---

## 4. Known Prototype Limitations (Tier 1 vs Production)

- **Authentication**: The Tier 1 local prototype does not implement multi-tenant JWT or session authentication; it operates in demonstration mode with the canonical sample enterprise. Production deployment requires OAuth2 / OIDC with role-based access control.
- **File Storage**: Uploaded evidence metadata is tracked in the database; binary storage in production should migrate from local paths to encrypted S3-compatible object stores with pre-signed URLs.
- **Transport Security**: In local pitch demonstrations, HTTP is used; production deployment requires TLS 1.3 encryption in transit.
