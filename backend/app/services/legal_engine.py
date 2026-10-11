from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import math
from backend.app.core.config import settings


class LegalEngine:
    """
    Deterministic Legal Timeline and Calculation Engine based on:
    - Micro, Small and Medium Enterprises Development (MSMED) Act, 2006 (Sections 15, 16, 17, 18)
    - Section 43B(h) of the Income Tax Act, 1961
    - Reserve Bank of India (RBI) Bank Rate notifications
    """

    DEFAULT_BANK_RATE = settings.RBI_BANK_RATE_PERCENT  # 6.75% per annum
    STATUTORY_MULTIPLIER = settings.MSME_INTEREST_MULTIPLIER  # 3x bank rate

    @classmethod
    def calculate_timeline_and_interest(
        cls,
        invoice_date: date,
        delivery_date: Optional[date] = None,
        acceptance_date: Optional[date] = None,
        has_objection: bool = False,
        objection_date: Optional[date] = None,
        objection_resolved_date: Optional[date] = None,
        has_written_agreement: bool = True,
        agreed_credit_days: Optional[int] = 30,
        outstanding_principal: float = 0.0,
        enterprise_type: str = "micro",  # micro, small, medium
        udyam_registered: bool = True,
        as_of_date: Optional[date] = None,
        custom_bank_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        evaluation_date = as_of_date or date.today()
        calculation_trace: List[str] = []
        warnings: List[str] = []

        # 1. Determine Reference Date (Section 2(a) & 2(b) MSMED Act)
        reference_date: date = invoice_date
        reference_type: str = "invoice_date_provisional"

        if has_objection:
            if objection_resolved_date:
                reference_date = objection_resolved_date
                reference_type = "objection_resolved_date"
                calculation_trace.append(
                    f"Buyer objection lodged and resolved on {objection_resolved_date}. "
                    f"Under Section 2(a)(ii) MSMED Act, reference date is the date of objection resolution."
                )
            else:
                reference_type = "objection_pending"
                warnings.append(
                    "Buyer objection is recorded as unresolved. Under Section 2(a)(ii) MSMED Act, "
                    "the statutory timeline is paused until the objection is resolved."
                )
                calculation_trace.append("Objection pending; calculation marked as provisional.")
        elif acceptance_date:
            reference_date = acceptance_date
            reference_type = "acceptance_date"
            calculation_trace.append(
                f"Formal acceptance confirmed on {acceptance_date} (Section 2(a)(i) MSMED Act)."
            )
        elif delivery_date:
            reference_date = delivery_date
            reference_type = "deemed_acceptance_date"
            calculation_trace.append(
                f"Goods/Services delivered on {delivery_date}. No objection communicated within 15 days, "
                f"qualifying as Day of Deemed Acceptance under Section 2(b) MSMED Act."
            )
        else:
            reference_date = invoice_date
            reference_type = "invoice_date_provisional"
            warnings.append(
                "Neither delivery proof nor acceptance date provided. Using invoice date as provisional fallback. "
                "Official MSME Samadhaan proceedings require documentary proof of delivery/acceptance."
            )
            calculation_trace.append(
                f"Provisional fallback: invoice date {invoice_date} used due to missing delivery/acceptance records."
            )

        # 2. Determine Statutory Term (Section 15 MSMED Act)
        statutory_term_capped = False
        statutory_term_days = 15

        if has_written_agreement:
            credit_days = agreed_credit_days if agreed_credit_days is not None else 30
            if credit_days <= 45:
                statutory_term_days = credit_days
                statutory_rule_citation = (
                    f"Section 15 MSMED Act, 2006: Agreed contractual credit period ({credit_days} days) "
                    f"is within the statutory maximum limit of 45 days."
                )
                calculation_trace.append(
                    f"Contractual agreement allows {credit_days} credit days, compliant with Section 15."
                )
            else:
                statutory_term_days = 45
                statutory_term_capped = True
                statutory_rule_citation = (
                    f"Section 15 Proviso MSMED Act, 2006: Agreed contractual period was {credit_days} days, "
                    f"but statute strictly mandates that agreed period shall not exceed 45 days from acceptance. "
                    f"Term legally capped at 45 days."
                )
                calculation_trace.append(
                    f"Agreed credit period of {credit_days} days exceeds statutory maximum; capped at 45 days."
                )
        else:
            statutory_term_days = 15
            statutory_rule_citation = (
                "Section 15 & Section 2(b) MSMED Act, 2006: In the absence of a written agreement, "
                "payment must be made before the 'appointed day' (15 days from day of acceptance/deemed acceptance)."
            )
            calculation_trace.append(
                "No written agreement recorded. Statutory 15-day timeline applied per Section 15 MSMED Act."
            )

        # 3. Calculate Due Date
        calculated_due_date = reference_date + timedelta(days=statutory_term_days)
        calculation_trace.append(
            f"Reference Date ({reference_date}) + {statutory_term_days} days = Statutory Due Date ({calculated_due_date})."
        )

        # 4. Overdue and Days Evaluation
        is_overdue = False
        days_overdue = 0
        days_remaining = 0

        if evaluation_date > calculated_due_date:
            is_overdue = True
            days_overdue = (evaluation_date - calculated_due_date).days
            days_remaining = 0
            calculation_trace.append(
                f"As of evaluation date ({evaluation_date}), invoice is {days_overdue} days overdue beyond due date ({calculated_due_date})."
            )
        else:
            is_overdue = False
            days_overdue = 0
            days_remaining = (calculated_due_date - evaluation_date).days
            calculation_trace.append(
                f"Invoice is currently within credit period. {days_remaining} days remaining until due date ({calculated_due_date})."
            )

        # 5. Compound Interest Calculation (Section 16 MSMED Act)
        # Section 16 mandates compound interest with monthly rests at 3x the RBI Bank Rate
        bank_rate = custom_bank_rate if custom_bank_rate is not None else cls.DEFAULT_BANK_RATE
        annual_statutory_rate = round(bank_rate * cls.STATUTORY_MULTIPLIER, 4)
        monthly_rate = annual_statutory_rate / 100.0 / 12.0

        estimated_interest = 0.0
        interest_breakdown: Dict[str, Any] = {}

        if is_overdue and outstanding_principal > 0:
            # Compound interest with monthly rests
            full_months = days_overdue // 30
            residual_days = days_overdue % 30
            
            # Compounding over full months
            compounded_principal = outstanding_principal * ((1.0 + monthly_rate) ** full_months)
            
            # Simple pro-rata interest for the residual days within the ongoing month
            pro_rata_factor = 1.0 + (monthly_rate * (residual_days / 30.0))
            total_due_with_interest = compounded_principal * pro_rata_factor
            
            estimated_interest = round(total_due_with_interest - outstanding_principal, 2)
            
            calculation_trace.append(
                f"Section 16 statutory interest applied: RBI Bank Rate {bank_rate}% x 3 = {annual_statutory_rate}% p.a. "
                f"Compounded monthly for {full_months} full months and {residual_days} residual days: "
                f"Estimated Interest = ₹{estimated_interest:,.2f} on Principal ₹{outstanding_principal:,.2f}."
            )
            interest_breakdown = {
                "principal": outstanding_principal,
                "full_months": full_months,
                "residual_days": residual_days,
                "monthly_interest_rate_pct": round(monthly_rate * 100, 4),
                "annual_interest_rate_pct": annual_statutory_rate,
                "compounded_amount": round(total_due_with_interest, 2),
                "estimated_interest": estimated_interest,
            }
        else:
            interest_breakdown = {
                "principal": outstanding_principal,
                "full_months": 0,
                "residual_days": 0,
                "monthly_interest_rate_pct": round(monthly_rate * 100, 4),
                "annual_interest_rate_pct": annual_statutory_rate,
                "compounded_amount": outstanding_principal,
                "estimated_interest": 0.0,
            }

        total_claimable = round(outstanding_principal + estimated_interest, 2)

        # 6. Section 43B(h) Income Tax Assessment
        sec_43b_h_applicable = enterprise_type.lower() in ("micro", "small")
        sec_43b_h_impact = ""
        if sec_43b_h_applicable:
            if is_overdue and outstanding_principal > 0:
                sec_43b_h_impact = (
                    "CRITICAL TAX DISALLOWANCE RISK: Under Section 43B(h) of the Income Tax Act, 1961, "
                    "the buyer cannot claim this outstanding amount as a deductible tax expense for the financial year "
                    "unless paid before year-end. This creates severe tax liability for delinquent buyers."
                )
            else:
                sec_43b_h_impact = (
                    f"Section 43B(h) Monitoring Active: Payment must be cleared on or before {calculated_due_date} "
                    f"to ensure buyer qualifies for allowable income tax deduction."
                )
        else:
            sec_43b_h_impact = (
                "Not applicable: Section 43B(h) deduction rules specifically cover Micro and Small enterprises. "
                "Medium enterprises do not fall under Section 43B(h) disallowance provisions."
            )

        # 7. Eligibility Status Review
        eligibility_status = "eligible"
        if not udyam_registered:
            eligibility_status = "additional_information_required"
            warnings.append("Valid Udyam Registration is required to initiate formal Samadhaan facilitation council claims.")
        elif reference_type == "objection_pending":
            eligibility_status = "needs_professional_review"
            warnings.append("Active dispute/objection must be resolved before filing under Section 18.")
        elif reference_type == "invoice_date_provisional":
            eligibility_status = "additional_information_required"
            warnings.append("Delivery challan or client acceptance signature needed to substantiate deemed acceptance date.")

        return {
            "reference_date": reference_date.isoformat(),
            "reference_type": reference_type,
            "statutory_term_days": statutory_term_days,
            "statutory_term_capped": statutory_term_capped,
            "statutory_rule_citation": statutory_rule_citation,
            "calculated_due_date": calculated_due_date.isoformat(),
            "evaluation_date": evaluation_date.isoformat(),
            "is_overdue": is_overdue,
            "days_overdue": days_overdue,
            "days_remaining": days_remaining,
            "outstanding_principal": outstanding_principal,
            "rbi_bank_rate_pct": bank_rate,
            "annual_statutory_interest_rate_pct": annual_statutory_rate,
            "estimated_interest": estimated_interest,
            "total_claimable_amount": total_claimable,
            "interest_breakdown": interest_breakdown,
            "section_43b_h_applicable": sec_43b_h_applicable,
            "section_43b_h_impact": sec_43b_h_impact,
            "eligibility_status": eligibility_status,
            "warnings": warnings,
            "calculation_trace": calculation_trace,
            "disclaimer": (
                "Statutory calculation estimate based on MSMED Act 2006 Sections 15–16. "
                "Interest and eligibility estimates are provided for pre-litigation and negotiation guidance. "
                "Final determinations are subject to Micro and Small Enterprises Facilitation Council (MSEFC) rulings."
            ),
        }
