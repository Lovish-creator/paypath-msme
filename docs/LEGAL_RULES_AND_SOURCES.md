# PayPath MSME — Legal Rules, Citations & Mathematical Sources

## 1. Statutory Authorities & Primary Sources

PayPath MSME is engineered as an evidence-backed calculation, workflow, and pre-litigation document preparation system. All statutory rules and interest compounding calculations are strictly grounded in authoritative Indian statutes:

| Authority / Statute | Relevant Provisions | Source Reference | Verification Date |
|---|---|---|---|
| **Micro, Small and Medium Enterprises Development (MSMED) Act, 2006** | Section 15: Liability of buyer to make payment<br/>Section 16: Rate and compounding of interest<br/>Section 17: Recovery of amount due<br/>Section 18: Reference to MSEFC Council | [India Code - MSMED Act 2006 (Act No. 27 of 2006)](https://www.indiacode.nic.in/handle/123456789/2012) | 2026-10-12 |
| **Reserve Bank of India (RBI) Bank Rate Notifications** | Section 49, Reserve Bank of India Act, 1934 | [Reserve Bank of India - Current Policy Rates](https://www.rbi.org.in/) | 2026-10-12 |
| **Income Tax Act, 1961 (as amended by Finance Act, 2023)** | Section 43B(h): Disallowance of delayed payments to Micro and Small Enterprises | [Income Tax Department - Section 43B](https://incometaxindia.gov.in/) | 2026-10-12 |
| **Ministry of MSME — Samadhaan Guidance** | Facilitation Council Conciliation & Arbitration Rules | [MSME Samadhaan Portal](https://samadhaan.msme.gov.in/) | 2026-10-12 |

---

## 2. Section 15: Payment Timeline & The 45-Day Statutory Cap

### Statutory Language
Section 15 provides:
> *"Where any supplier supplies any goods or renders any services to any buyer, the buyer shall make payment therefor on or before the date agreed upon between him and the supplier in writing or, where there is no agreement, before the appointed day:*
> 
> *Provided that in no case the period agreed upon between the supplier and the buyer in writing shall exceed forty-five days from the day of acceptance or the day of deemed acceptance."*

### Key Definitions:
1. **"Appointed Day" (Section 2(b))**: The day following immediately after the expiry of the period of **fifteen days** from the day of acceptance or deemed acceptance.
2. **"Day of Acceptance" (Section 2(a)(i))**:
   - The day of the actual delivery of goods or rendering of services; or
   - Where an objection is made in writing by the buyer regarding acceptance within 15 days from delivery, the day on which such objection is removed by the supplier.
3. **"Day of Deemed Acceptance" (Section 2(a)(ii))**: Where no objection is made in writing within 15 days from delivery, the day of actual delivery.

### Deterministic Implementation in PayPath Engine:
1. **With Written Agreement**:
   - If agreed credit days $N \le 45$: Term is $N$ days from Reference Date.
   - If agreed credit days $N > 45$: Contractual term is overridden by the Section 15 Proviso; statutory term is capped at **45 days**.
2. **Without Written Agreement**:
   - Term strictly defaults to **15 days** from delivery / deemed acceptance.
3. **Active Objection Recorded**:
   - If a buyer objection is recorded as pending, the timeline is flagged as suspended under Section 2(a)(ii) until objection removal is substantiated.

---

## 3. Section 16: Compound Interest with Monthly Rests

### Statutory Language
Section 16 provides:
> *"Where any buyer fails to make payment of the amount to the supplier as required under section 15, the buyer shall, notwithstanding anything contained in any agreement between the buyer and the supplier or in any law for the time being in force, be liable to pay compound interest with monthly rests to the supplier on that amount from the appointed day or, as the case may be, from the date immediately following the date agreed upon, at three times of the bank rate notified by the Reserve Bank."*

### Mathematical Formula & Assumptions
1. **Applicable Benchmark Rate**:
   - Reserve Bank of India Bank Rate: **6.75% per annum** (configurable baseline).
   - Statutory Multiplier: **3.0x**.
   - Effective Annual Compound Rate: $R = 3 \times 6.75\% = \mathbf{20.25\%\text{ per annum}}$.
2. **Compounding Frequency**:
   - Compounded with **monthly rests** (monthly rate $r_m = \frac{20.25\%}{12} = \mathbf{1.6875\%\text{ per month}}$).
3. **Period Breakdown**:
   - For total overdue days $D$:
     - Full completed months: $m = \lfloor D / 30 \rfloor$
     - Residual ongoing days: $d = D \pmod{30}$
4. **Calculated Claimable Sum**:
   $$A = P \times (1 + r_m)^m \times \left(1 + r_m \times \frac{d}{30}\right)$$
   $$\text{Estimated Compound Interest} = A - P$$
5. **Transparency & Disclaimer**:
   - The UI and generated reports explicitly label this amount as an **estimate requiring verification during Facilitation Council proceedings**, distinguishing principal debt from accrued interest.

---

## 4. Section 43B(h) Income Tax Assessment

1. **Scope**: Applies to payments owed to **Micro and Small Enterprises** (Medium Enterprises are excluded under Finance Act 2023).
2. **Tax Consequence**: If payment is not cleared within Section 15 limits (within 15 days or up to 45 days per written contract), the debtor cannot claim the expense as a tax-deductible expense in the relevant fiscal year until actual payment is made.
3. **Incentive Mechanism**: PayPath highlights this to provide MSMEs significant commercial negotiation leverage before formal litigation.

---

## 5. Scope Boundaries and Ethical Rules

1. **Information Tool, Not Legal Opinion**: PayPath organizes facts, computes deterministic statutory estimates, and formats formal drafts. It does not provide legal representation.
2. **Evidence-Gated Escalation**: No case can claim readiness for formal MSEFC filing unless core documentary evidence (Invoice, PO, Delivery Proof, Udyam) is verified.
3. **Zero Financial Distress Targeting**: Unpaid invoices or debt records are strictly isolated from advertising and supplier matching algorithms.
