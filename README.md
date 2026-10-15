# PayPath MSME
### *From overdue invoice to an organised, evidence-backed next step.*
**Independent B2B Receivables Platform | Production-Hardened Startup Prototype**

---

## 1. Product Overview

**PayPath MSME** is a purpose-built pre-litigation receivables management, statutory interest calculation, and contextual B2B supplier discovery platform designed for India's Micro and Small Enterprises (MSMEs).

When business customers delay payments beyond statutory timelines, PayPath guides the supplier through a deterministic, evidence-backed workflow:
1. **Determines Applicable Reference Dates**: Evaluates delivery, acceptance, and deemed acceptance under Section 2(a) and 2(b) of the MSMED Act, 2006.
2. **Enforces Statutory Credit Limits**: Applies Section 15's mandatory 15-day default (where no agreement exists) and enforces the statutory 45-day cap against excessive contractual credit terms.
3. **Calculates Traceable Compound Interest**: Computes statutory penal compound interest with monthly rests at 3x the RBI Bank Rate (20.25% p.a.) under Section 16 of the MSMED Act.
4. **Assesses Section 43B(h) Tax Disallowance Leverage**: Identifies tax deduction forfeiture risks faced by corporate debtors under Section 43B(h) of the Income Tax Act, 1961.
5. **Audits MSEFC Evidence Admissibility**: Verifies 7 critical documentary artifacts to ensure Facilitation Council petition readiness.
6. **Drafts Pre-Litigation Demands & Dossiers**: Generates customizable demand notices and publication-grade PDF Case-Preparation Reports using ReportLab.
7. **Monetizes via Contextual B2B Supplier Matching**: Connects verified manufacturers with relevant raw material vendors based purely on voluntary industry categories, strictly excluding debt or insolvency data from targeting.

---

## 2. Technical Stack

- **Backend**: Python 3.14+, FastAPI, SQLAlchemy 2.0, Pydantic v2, ReportLab, Pytest
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, React Router v6
- **Database**: SQLite (local Tier 1 prototype) with documented migration path to PostgreSQL (Tier 2)
- **Architecture**: Modular Monolith with strict separation of domain services, legal formulas, and persistence

---

## 3. Prerequisites

- Python 3.10+ (tested on Python 3.14.6)
- Node.js 18+ (tested on Node.js v24.18.0)
- npm 9+ (tested on npm 11.16.0)

---

## 4. Setup & Installation

### Step 1: Clone or Navigate to the Repository
```bash
git clone <repo-url> paypath-msme
cd paypath-msme
```

### Step 2: Configure Environment Variables
Copy the example environment configuration:
```bash
cp .env.example .env
```
Default configuration values:
```ini
PORT=8000
HOST=127.0.0.1
ENVIRONMENT=development
DATABASE_URL=sqlite:///./paypath.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
RBI_BANK_RATE_PERCENT=6.75
MSME_INTEREST_MULTIPLIER=3.0
STORAGE_LOCAL_DIR=./backend/data
```

### Step 3: Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 5. Seed Demonstration Dataset

PayPath MSME includes a deterministic seed dataset modeling 5 realistic commercial scenarios:
1. **Case 1 (Primary Star)**: Overdue invoice with complete documentary evidence (Apex Uniforms → Metro Retail Stores).
2. **Case 2**: Overdue invoice with missing delivery evidence requiring audit (Skyline Retailers).
3. **Case 3**: Invoice with recorded partial payments and ongoing balance recovery (Bharat Garment Hub).
4. **Case 4**: Case with active written payment promise due within 3 days (Orbit Retail Ventures).
5. **Case 5**: Case with active quality dispute pausing the deemed acceptance timeline under Section 2(a)(ii) (Delta Fashion House).

To seed or reset the database:
```bash
python -m backend.app.demo.seed_data
```
*(Alternatively, click the **Reset Demo Data** button in the application navbar at any time during a live pitch.)*

---

## 6. Running the Application

### Start the Backend API Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI backend will start at:
- **API Base**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/api/health`

### Start the Frontend Client
In a separate terminal:
```bash
cd frontend
npm run dev
```
The React application will launch at:
- **Web App**: `http://localhost:5173`

---

## 7. Running Automated Tests

### Backend Test Suite
Run the comprehensive pytest test suite covering legal calculations, balance invariants, payments, stage escalation, PDF generation, supplier matching, and consent requirements:
```bash
python -m pytest backend/tests -v
```
*Current result: 19 passed tests in 1.67 seconds.*

### Frontend Type Check & Production Build
Validate TypeScript typings and build the production bundle:
```bash
cd frontend
npm run build
```
*Current result: 0 errors, production bundle compiled cleanly.*

---

## 8. Documentation Index

Detailed architectural and legal documentation is available in the `docs/` folder:
- [Architecture & System Design](file:///C:/Users/Ni/.gemini/antigravity/scratch/paypath-msme/docs/ARCHITECTURE.md)
- [Legal Rules & Mathematical Citations](file:///C:/Users/Ni/.gemini/antigravity/scratch/paypath-msme/docs/LEGAL_RULES_AND_SOURCES.md)
- [Privacy & Data Safeguards](file:///C:/Users/Ni/.gemini/antigravity/scratch/paypath-msme/docs/PRIVACY_AND_SECURITY.md)
- [Live Pitch Demonstration Script](file:///C:/Users/Ni/.gemini/antigravity/scratch/paypath-msme/docs/DEMO_SCRIPT.md)
- [Implementation Status & Audit Log](file:///C:/Users/Ni/.gemini/antigravity/scratch/paypath-msme/docs/IMPLEMENTATION_STATUS.md)
- [Data Model & Entity Specifications](file:///C:/Users/Ni/.gemini/antigravity/scratch/paypath-msme/docs/DATA_MODEL.md)
- [Architectural Decision Records (ADRs)](file:///C:/Users/Ni/.gemini/antigravity/scratch/paypath-msme/docs/DECISIONS.md)
- [Product Scope & Boundaries](file:///C:/Users/Ni/.gemini/antigravity/scratch/paypath-msme/docs/PRODUCT_SCOPE.md)

---

## 9. Known Prototype Boundaries

- **Local Storage**: Evidence document metadata is tracked; binary storage in Tier 1 runs locally rather than on S3.
- **Authentication**: Operates in single-enterprise demonstration mode (`Apex Uniforms & Apparel`). Tier 2 introduces multi-tenant OAuth2/JWT.
- **Statutory Estimates**: Interest calculations are deterministic estimates under Section 16; final decrees are issued by the Micro and Small Enterprises Facilitation Council (MSEFC).
