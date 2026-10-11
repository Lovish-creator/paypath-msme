import pytest
from datetime import date, timedelta
from backend.app.services.legal_engine import LegalEngine


def test_standard_contractual_term():
    """Test standard agreement with 30 days credit term"""
    inv_date = date(2026, 7, 1)
    del_date = date(2026, 7, 2)
    as_of = date(2026, 8, 15)  # 44 days after delivery => 14 days overdue

    result = LegalEngine.calculate_timeline_and_interest(
        invoice_date=inv_date,
        delivery_date=del_date,
        has_written_agreement=True,
        agreed_credit_days=30,
        outstanding_principal=100000.0,
        as_of_date=as_of,
    )

    assert result["reference_date"] == del_date.isoformat()
    assert result["reference_type"] == "deemed_acceptance_date"
    assert result["statutory_term_days"] == 30
    assert result["statutory_term_capped"] is False
    assert result["calculated_due_date"] == (del_date + timedelta(days=30)).isoformat()
    assert result["is_overdue"] is True
    assert result["days_overdue"] == 14
    assert result["estimated_interest"] > 0


def test_statutory_45_day_cap():
    """Test Section 15 proviso: agreed term > 45 days is strictly capped at 45 days"""
    inv_date = date(2026, 7, 1)
    del_date = date(2026, 7, 1)

    result = LegalEngine.calculate_timeline_and_interest(
        invoice_date=inv_date,
        delivery_date=del_date,
        has_written_agreement=True,
        agreed_credit_days=90,  # 90 days requested
        outstanding_principal=50000.0,
        as_of_date=date(2026, 8, 20),
    )

    assert result["statutory_term_days"] == 45
    assert result["statutory_term_capped"] is True
    assert "Section 15 Proviso" in result["statutory_rule_citation"]
    assert result["calculated_due_date"] == (del_date + timedelta(days=45)).isoformat()


def test_no_written_agreement_defaults_to_15_days():
    """Test Section 15 & 2(b): absence of written agreement defaults to 15 days from deemed acceptance"""
    inv_date = date(2026, 7, 1)
    del_date = date(2026, 7, 5)

    result = LegalEngine.calculate_timeline_and_interest(
        invoice_date=inv_date,
        delivery_date=del_date,
        has_written_agreement=False,
        agreed_credit_days=None,
        outstanding_principal=20000.0,
        as_of_date=date(2026, 7, 10),
    )

    assert result["statutory_term_days"] == 15
    assert result["calculated_due_date"] == (del_date + timedelta(days=15)).isoformat()
    assert result["is_overdue"] is False
    assert result["days_remaining"] == 10
    assert result["estimated_interest"] == 0.0


def test_objection_pauses_timeline():
    """Test Section 2(a)(ii): unresolved objection flags pause in statutory deemed acceptance"""
    inv_date = date(2026, 7, 1)
    del_date = date(2026, 7, 2)

    result = LegalEngine.calculate_timeline_and_interest(
        invoice_date=inv_date,
        delivery_date=del_date,
        has_objection=True,
        objection_date=date(2026, 7, 8),
        objection_resolved_date=None,  # Unresolved
        outstanding_principal=75000.0,
    )

    assert result["reference_type"] == "objection_pending"
    assert result["eligibility_status"] == "needs_professional_review"
    assert any("objection is recorded as unresolved" in w for w in result["warnings"])


def test_section_16_compound_interest_math():
    """Test exact mathematical formula: 3x RBI Bank Rate (20.25% p.a.) compounded monthly"""
    # Exactly 30 days overdue (1 month) on 100,000 principal
    inv_date = date(2026, 1, 1)
    due_date = date(2026, 1, 31)
    eval_date = date(2026, 3, 2)  # 30 days overdue

    result = LegalEngine.calculate_timeline_and_interest(
        invoice_date=inv_date,
        delivery_date=inv_date,
        has_written_agreement=True,
        agreed_credit_days=30,
        outstanding_principal=100000.0,
        as_of_date=eval_date,
        custom_bank_rate=6.75,
    )

    # 100000 * (1 + 0.2025/12) = 101687.50 => interest = 1687.50
    assert result["days_overdue"] == 30
    assert result["estimated_interest"] == 1687.50
    assert result["total_claimable_amount"] == 101687.50


def test_section_43b_h_applicability():
    """Test Section 43B(h) applicability distinction between Micro/Small and Medium enterprises"""
    res_micro = LegalEngine.calculate_timeline_and_interest(
        invoice_date=date(2026, 1, 1),
        enterprise_type="micro",
        outstanding_principal=50000.0,
    )
    assert res_micro["section_43b_h_applicable"] is True

    res_medium = LegalEngine.calculate_timeline_and_interest(
        invoice_date=date(2026, 1, 1),
        enterprise_type="medium",
        outstanding_principal=50000.0,
    )
    assert res_medium["section_43b_h_applicable"] is False
    assert "Medium enterprises do not fall under Section 43B(h)" in res_medium["section_43b_h_impact"]
