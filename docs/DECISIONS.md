# PayPath MSME — Architectural & Technical Decision Records (ADR)

## ADR 01: Modular Monolith vs Microservices for Tier 1
- **Decision**: Build a modular monolith using FastAPI (Python) and React (TypeScript) rather than microservices.
- **Rationale**: The SLIET PitchVerse 2026 prototype required rapid, deterministic, and reliable local execution. Microservices introduce network fragility, orchestration overhead, and distributed transaction complexity without adding value for a two-day startup prototype.
- **Status**: Accepted and implemented.

---

## ADR 02: SQLite Persistence Layer with SQLAlchemy 2.0
- **Decision**: Use SQLite with a thread-safe connection pool for Tier 1 local demonstration, while designing domain models with SQLAlchemy 2.0 declarative mappings for seamless migration to PostgreSQL in Tier 2.
- **Rationale**: Zero external database dependency ensures anyone evaluating the prototype (judges, examiners, CI) can run it immediately without Docker or PostgreSQL setup.
- **Status**: Accepted and implemented.

---

## ADR 03: ReportLab for Programmatic PDF Generation
- **Decision**: Use ReportLab in Python rather than headless Chrome / Puppeteer.
- **Rationale**: Headless browsers add hundreds of megabytes of binary dependencies, memory overhead, and flaky rendering in constrained environments. ReportLab produces deterministic, vector-grade PDFs directly from persisted models in milliseconds.
- **Status**: Accepted and implemented.

---

## ADR 04: Legal Calculation Engine Isolation
- **Decision**: Isolate all statutory formulas (Sections 15, 16, 17, 18 MSMED Act and Section 43B(h) Income Tax Act) into a dedicated, stateless service (`legal_engine.py`) with 100% automated pytest coverage.
- **Rationale**: Prevents accidental legal calculation drift, eliminates floating-point rounding errors, and ensures identical figures across the dashboard, invoice view, case view, and generated PDF reports.
- **Status**: Accepted and implemented.

---

## ADR 05: Strict Boundary for Contextual B2B Sponsored Discovery
- **Decision**: Completely isolate supplier matching algorithms from invoice amounts, debt status, or debtor names.
- **Rationale**: Ethics and compliance. Selling or targeting based on commercial insolvency or financial distress is predatory. Contextual matching based solely on declared industry category (`garment_manufacturing`) and voluntary purchasing interests (`thread, fabric, packaging`) provides a clean, sustainable monetization path.
- **Status**: Accepted and implemented.
