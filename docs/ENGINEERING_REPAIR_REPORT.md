# PayPath MSME — Engineering Repair & Audit Report
## Security Hardening, Product Cleanup, and Startup-Ready Architecture

---

## 1. Executive Summary

This report documents the architectural audit, security vulnerabilities, legal-calculation defects, and brand identity fixes identified and repaired in **PayPath MSME**.

PayPath MSME is an independent startup product designed for Indian micro and small enterprises (MSMEs) facing delayed commercial payments under the Micro, Small and Medium Enterprises Development (MSMED) Act, 2006.

---

## 2. Identified Vulnerabilities & Technical Deficiencies

### 2.1 Critical Security Vulnerabilities (P0)

1. **Unprotected Destructive Endpoint (`POST /api/demo/reset`)**:
   - **File:** `backend/app/api/routes_demo.py`
   - **Vulnerability:** Unauthenticated public endpoint executing `seed_database(db, force_reset=True)` which deleted all users, business profiles, invoices, payments, cases, evidence, and enquiries across the entire database.
   - **Risk:** Complete data erasure by any unauthenticated web request.
   - **Remediation:** Disable demo reset in production environments; fail server startup if misconfigured; restrict development use to explicit environment flags (`ALLOW_DEMO_RESET=true`).

2. **Unauthenticated Advertiser Lead Disclosure (`GET /api/suppliers/{supplier_id}/advertiser-leads`)**:
   - **File:** `backend/app/api/routes_suppliers.py`
   - **Vulnerability:** Unauthenticated endpoint returning customer names, email addresses, phone numbers, and enquiry messages without verification.
   - **Risk:** Data privacy breach and harvesting of MSME contact information.
   - **Remediation:** Restrict to authenticated and authorized listing owners; disable public lead browsing.

3. **Insecure Secret Key & Permissive CORS Configuration**:
   - **Files:** `backend/app/core/config.py`, `backend/app/main.py`
   - **Vulnerability:** Hardcoded secret key default containing competition reference (`paypath-msme-production-secure-key-2026-sliet`) and wildcard CORS (`allow_origins=["*"]`) combined with `allow_credentials=True`.
   - **Risk:** Insecure token forgery if deployed with default configuration; CORS credential leakage.
   - **Remediation:** Require mandatory, high-entropy `SECRET_KEY` in production; fail startup if missing or weak (< 32 chars); enforce strict CORS origin allowlist without wildcards.

4. **Missing Invoice Deletion Endpoint**:
   - **Files:** `backend/app/api/routes_invoices.py`, `backend/app/services/invoice_service.py`
   - **Deficiency:** Inability for users to delete erroneously recorded draft or unpaid invoices within their workspace.

### 2.2 Document Extraction & Upload Flaws (Section 4)

1. **Fabricated Fallback Data on Missing Extraction Fields**:
   - **File:** `backend/app/services/document_extractor.py`
   - **Deficiency:** When fields were absent from uploaded documents, the extractor generated fake values (e.g. random `INV-XXXXXX`, `"Verified Debtor Name"`, current date fallback, 30 days credit default).
   - **Remediation:** Remove all synthetic generation. Missing fields must remain `None`, with unambiguous uncertainty indicators in the UI requiring explicit user review and confirmation.

2. **Missing File Signature / Content Validation**:
   - **Files:** `backend/app/api/routes_invoices.py`, `backend/app/services/document_extractor.py`
   - **Deficiency:** Trusted filename extension without checking file signatures (magic bytes like `%PDF-`).
   - **Remediation:** Check `%PDF-` binary magic bytes; enforce 10MB file-size limit; reject malformed or non-PDF files safely with clear error feedback.

### 2.3 Legal & Financial Calculation Assumptions (Section 5)

1. **Silent Legal Assumptions**:
   - **File:** `backend/app/services/legal_engine.py`
   - **Deficiency:** Defaulted `has_written_agreement=True` and `agreed_credit_days=30` in method signatures, silently assuming contractual terms when users had not specified them.
   - **Remediation:** Default to statutory 15-day timeline under Section 15 unless a written contract is explicitly recorded.

2. **Floating-Point Arithmetic in Financial Calculations**:
   - **File:** `backend/app/services/legal_engine.py`
   - **Deficiency:** Used standard Python floats for compounding interest and balance subtractions.
   - **Remediation:** Implement `Decimal` arithmetic with `ROUND_HALF_UP` rounding for currency precision.

### 2.4 Brand Identity & Product Cleanup (Section 1)

1. **Removal of Competition / Academic References**:
   - **Files:** `Navbar.tsx`, `AuthModal.tsx`, `SupplierDiscoveryView.tsx`, `routes_demo.py`, `config.py`, `main.py`, `README.md`.
   - **Action:** Removed all customer-facing mentions of "SLIET", "PitchVerse", "Competition", and "Hackathon".
   - **Brand Alignment:** Consistently established **PayPath MSME: From overdue invoice to an organised, evidence-backed next step.**

---

## 4. Verification & Audit Results

### 4.1 Automated Test Suite (100% Pass Rate)
- **Total Backend Tests:** 31 tests across 7 test modules
- **Status:** 31 passed in 5.97s
- **Test Modules Covered:**
  - `backend/tests/test_auth_and_isolation.py`: Unauthenticated 401 rejection, user registration, JWT generation, cross-tenant isolation.
  - `backend/tests/test_cases_and_escalation.py`: Stage transitions (1 to 8), evidence item status updates, reminder draft generation with statutory citations.
  - `backend/tests/test_invoices_and_payments.py`: Invoice lifecycle, partial payments, balance reconciliation, overdue status transitions.
  - `backend/tests/test_legal_engine.py`: Statutory 15-day defaults, 45-day caps, Section 2(a)(ii) objection suspension, Section 16 monthly compound interest math, Section 43B(h) applicability.
  - `backend/tests/test_pdf_and_demo.py`: Case preparation report generation with valid binary signature (`%PDF-`), dynamic RBI interest disclaimers, protected demo reset behavior.
  - `backend/tests/test_security_hardening.py`: Startup fatal crash on weak/default `SECRET_KEY` in production, rejection of demo reset in production, wildcard CORS prohibition, PDF magic bytes validation (`%PDF-`), oversized upload rejection (413), extraction honesty without synthetic fallbacks, and cross-tenant invoice deletion protection.
  - `backend/tests/test_supplier_discovery.py`: Industry category and product tag matching, mandatory consent enforcement on quote enquiries, restriction of advertiser leads (403).

### 4.2 Brand & Identity Verification
- Zero occurrences of "SLIET", "PitchVerse", "Competition", or "Hackathon" across customer-facing UI, generated PDFs, or application code.
- Unified brand identity: **PayPath MSME — From overdue invoice to an organised, evidence-backed next step.**
- Honest empty states and realistic demo accounts without fabricated enterprise claims.

### 4.3 Production Readiness
- **Configuration Assertion:** `Settings.validate_production_configuration()` rigorously prevents running in production with default secrets, wildcard CORS, or demo endpoints enabled.
- **Tenant Isolation:** All CRUD operations enforce authenticated tenant ID matching.
- **Database Safety:** Payments lock invoices against accidental deletion; all financial calculations use `Decimal` with `ROUND_HALF_UP`.
