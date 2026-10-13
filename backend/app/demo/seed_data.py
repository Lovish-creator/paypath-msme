from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta, timezone

from backend.app.db.database import Base, engine, SessionLocal
from backend.app.models.user import User
from backend.app.models.business import BusinessProfile
from backend.app.models.buyer import Buyer
from backend.app.models.invoice import Invoice, Payment
from backend.app.models.case import Case, EvidenceItem, FollowUpEvent
from backend.app.models.supplier import SupplierListing, SupplierEnquiry
from backend.app.core.security import hash_password
from backend.app.services.invoice_service import STAGE_LABELS, DEFAULT_EVIDENCE_TEMPLATES


def seed_database(db: Session, force_reset: bool = True):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    if force_reset:
        # Clear tables cleanly
        db.query(SupplierEnquiry).delete()
        db.query(SupplierListing).delete()
        db.query(FollowUpEvent).delete()
        db.query(EvidenceItem).delete()
        db.query(Case).delete()
        db.query(Payment).delete()
        db.query(Invoice).delete()
        db.query(Buyer).delete()
        db.query(User).delete()
        db.query(BusinessProfile).delete()
        db.commit()
    else:
        # If records already exist, return early without re-inserting
        if db.query(BusinessProfile).count() > 0:
            return

    # 1. Create Sample Business Profile
    profile = BusinessProfile(
        id=1,
        name="Apex Uniforms & Apparel (Sample MSME)",
        enterprise_type="micro",
        udyam_number="UDYAM-PB-12-0048291",
        pan="AABCA1234F",
        gstin="03AABCA1234F1Z5",
        state="Punjab",
        district="Sangrur",
        industry_category="garment_manufacturing",
        purchasing_interests="thread,fabric,buttons,zippers,packaging,machinery",
        contact_email="finance@apexuniforms.in",
        contact_phone="+91 98765 43210",
    )
    db.add(profile)
    db.flush()

    # Create canonical demo user for login
    demo_user = User(
        email="demo@apexuniforms.in",
        hashed_password=hash_password("Password123!"),
        full_name="Apex Demo Admin",
        phone="+91 98765 43210",
        business_profile_id=profile.id,
    )
    db.add(demo_user)
    db.flush()

    profile.owner_user_id = demo_user.id
    db.commit()


    today = date.today()

    # 2. Case 1: Overdue Invoice with Complete Evidence (Primary Demo Star)
    # 60 days ago invoice, 30 days credit term => 30 days overdue!
    inv1_date = today - timedelta(days=60)
    del1_date = today - timedelta(days=58)
    acc1_date = today - timedelta(days=57)
    
    inv1 = Invoice(
        invoice_number="INV-2026-0891",
        business_profile_id=1,
        buyer_name="Metro Retail Stores Pvt Ltd",
        buyer_gstin="07AAACM9981E1Z8",
        buyer_contact_email="accounts.payable@metroretail.com",
        buyer_contact_phone="+91 98111 22334",
        invoice_date=inv1_date,
        delivery_date=del1_date,
        acceptance_date=acc1_date,
        has_objection=False,
        has_written_agreement=True,
        agreed_credit_days=30,
        total_amount=485000.00,
        paid_amount=0.00,
        outstanding_balance=485000.00,
        status="overdue",
        goods_services_description="Batch supply of 2,500 Sets Premium Corporate Uniforms with Embroidered Badges",
        notes="High-priority case. Buyer acknowledged receipt but delayed release citing financial year-end reviews.",
    )
    db.add(inv1)
    db.flush()

    case1 = Case(
        invoice_id=inv1.id,
        reference_code="CASE-INV-2026-0891",
        current_stage=5,
        stage_label=STAGE_LABELS[5],  # Formal Notice Draft Prepared
        priority="high",
        notes="Complete documentary evidence assembled. Pre-litigation formal demand notice prepared under Section 15 & 16 MSMED Act.",
    )
    db.add(case1)
    db.flush()

    # Evidence items for Case 1 (All provided!)
    ev_items_1 = [
        ("invoice", "Original Tax Invoice with GSTIN & HSN Details", "provided", "tax_inv_0891.pdf", "Signed invoice copy verified"),
        ("purchase_order", "Purchase Order (PO) / Written Commercial Agreement", "provided", "po_metro_2026_094.pdf", "Formal PO PO-MTR-881 signed by VP Operations"),
        ("delivery_proof", "Proof of Delivery / Transporter LR / Delivery Challan", "provided", "delivery_challan_0891.pdf", "Signed receiving stamp with date 58 days ago"),
        ("acceptance_record", "Goods Acceptance / Inspection Memo (or Deemed Acceptance Record)", "provided", "inspection_memo.pdf", "Goods QC passed without discrepancy"),
        ("buyer_comm", "Buyer Correspondence (WhatsApp, Email Acknowledgements, Follow-ups)", "provided", "email_threads_metro.pdf", "Multiple emails from AP confirming bill in processing"),
        ("payment_receipt", "Bank Account Statement / Partial Payment Records", "not_applicable", None, "No payments made yet"),
        ("udyam_certificate", "Udyam Registration Certificate of Supplier Enterprise", "provided", "udyam_apex_cert.pdf", "Verified active Micro Enterprise status"),
    ]
    for cat, title, status, fname, note in ev_items_1:
        db.add(EvidenceItem(
            case_id=case1.id, category=cat, title=title, status=status,
            file_name=fname, file_size_bytes=245000 if fname else None,
            uploaded_at=datetime.utcnow() - timedelta(days=50) if fname else None,
            notes=note
        ))

    # Follow-ups for Case 1
    db.add(FollowUpEvent(
        case_id=case1.id,
        event_type="invoice_created",
        summary="Invoice recorded in PayPath MSME ledger",
        detail="Supply of corporate uniforms delivered to Metro Retail regional warehouse.",
        performed_at=datetime.utcnow() - timedelta(days=60),
        recorded_by="System",
    ))
    db.add(FollowUpEvent(
        case_id=case1.id,
        event_type="friendly_reminder",
        summary="Friendly payment reminder email sent to Accounts Payable",
        detail="Dispatched courtesy reminder ahead of invoice maturity.",
        performed_at=datetime.utcnow() - timedelta(days=32),
        recorded_by="Finance Officer",
    ))
    db.add(FollowUpEvent(
        case_id=case1.id,
        event_type="phone_call",
        summary="Telephonic follow-up with Head of Accounts (Mr. R. Sharma)",
        detail="Debtor acknowledged dues; promised payment within 7 working days citing internal audit.",
        performed_at=datetime.utcnow() - timedelta(days=18),
        recorded_by="Senior Manager",
    ))
    db.add(FollowUpEvent(
        case_id=case1.id,
        event_type="formal_notice_drafted",
        summary="Formal Demand Notice under Section 15 & 16 MSMED Act generated",
        detail="Overdue exceeded 25 days beyond agreed credit window. Pre-litigation claim calculation verified.",
        performed_at=datetime.utcnow() - timedelta(days=3),
        recorded_by="Legal & Finance Desk",
    ))

    # 3. Case 2: Invoice with Missing Delivery Evidence (Needs Audit)
    inv2_date = today - timedelta(days=45)
    inv2 = Invoice(
        invoice_number="INV-2026-0922",
        business_profile_id=1,
        buyer_name="Skyline Retailers & Departmental Store",
        buyer_gstin="03BBBCS5421M1Z1",
        buyer_contact_email="finance@skylinestores.in",
        buyer_contact_phone="+91 98222 33445",
        invoice_date=inv2_date,
        delivery_date=None,  # Missing delivery date!
        acceptance_date=None,
        has_objection=False,
        has_written_agreement=True,
        agreed_credit_days=30,
        total_amount=215000.00,
        paid_amount=0.00,
        outstanding_balance=215000.00,
        status="overdue",
        goods_services_description="Supply of 1,200 cotton worker aprons and caps",
        notes="Transporter consignment note copy is pending from regional courier hub.",
    )
    db.add(inv2)
    db.flush()

    case2 = Case(
        invoice_id=inv2.id,
        reference_code="CASE-INV-2026-0922",
        current_stage=6,
        stage_label=STAGE_LABELS[6],  # Evidence Completeness Reviewed
        priority="medium",
        notes="Missing delivery receipt must be retrieved before filing MSME Samadhaan claim.",
    )
    db.add(case2)
    db.flush()

    for cat, title in DEFAULT_EVIDENCE_TEMPLATES:
        status = "provided" if cat in ("invoice", "udyam_certificate") else ("missing" if cat in ("delivery_proof", "acceptance_record") else "needs_review")
        db.add(EvidenceItem(
            case_id=case2.id,
            category=cat,
            title=title,
            status=status,
            notes="Pending driver signed receipt" if status == "missing" else None,
        ))

    db.add(FollowUpEvent(
        case_id=case2.id,
        event_type="evidence_reviewed",
        summary="Evidence Completeness Audit Flagged Missing Delivery Proof",
        detail="Auditor flagged that without proof of delivery or deemed acceptance receipt, MSEFC conciliation may face buyer objection.",
        performed_at=datetime.utcnow() - timedelta(days=5),
        recorded_by="Audit Specialist",
    ))

    # 4. Case 3: Invoice with Recorded Partial Payment
    inv3_date = today - timedelta(days=50)
    inv3 = Invoice(
        invoice_number="INV-2026-0740",
        business_profile_id=1,
        buyer_name="Bharat Garment Hub & Wholesale",
        buyer_gstin="06AAAFB1234K1Z0",
        buyer_contact_email="accounts@bharatgarmenthub.com",
        buyer_contact_phone="+91 98333 44556",
        invoice_date=inv3_date,
        delivery_date=inv3_date + timedelta(days=2),
        acceptance_date=inv3_date + timedelta(days=3),
        has_objection=False,
        has_written_agreement=True,
        agreed_credit_days=30,
        total_amount=350000.00,
        paid_amount=150000.00,
        outstanding_balance=200000.00,
        status="partially_paid",
        goods_services_description="Supply of 3,000 meters specialized school uniform blazer fabric",
        notes="Buyer remitted partial payment of ₹1,50,000; remaining balance of ₹2,00,000 delayed.",
    )
    db.add(inv3)
    db.flush()

    # Add Payment record
    p3 = Payment(
        invoice_id=inv3.id,
        payment_date=today - timedelta(days=15),
        amount=150000.00,
        reference_number="UTR-HDFC-994821038",
        payment_mode="Bank Transfer (RTGS)",
        notes="Part payment released towards Invoice #INV-2026-0740.",
    )
    db.add(p3)

    case3 = Case(
        invoice_id=inv3.id,
        reference_code="CASE-INV-2026-0740",
        current_stage=4,
        stage_label=STAGE_LABELS[4],  # Follow-up Recorded
        priority="medium",
        notes="Partial settlement received. Remainder requires structured follow-up.",
    )
    db.add(case3)
    db.flush()

    for cat, title in DEFAULT_EVIDENCE_TEMPLATES:
        status = "provided" if cat in ("invoice", "delivery_proof", "payment_receipt", "udyam_certificate") else "needs_review"
        db.add(EvidenceItem(
            case_id=case3.id,
            category=cat,
            title=title,
            status=status,
            notes="Bank UTR statement verified" if cat == "payment_receipt" else None,
        ))

    db.add(FollowUpEvent(
        case_id=case3.id,
        event_type="payment_recorded",
        summary="Part payment of ₹1,50,000.00 received via RTGS",
        detail="Ref: UTR-HDFC-994821038. Outstanding balance reduced to ₹2,00,000.00.",
        performed_at=datetime.utcnow() - timedelta(days=15),
        recorded_by="Finance Team",
    ))

    # 5. Case 4: Awaiting Promised Payment (Due Soon / Active Tracking)
    inv4_date = today - timedelta(days=35)
    inv4 = Invoice(
        invoice_number="INV-2026-1015",
        business_profile_id=1,
        buyer_name="Orbit Retail Ventures Ltd",
        buyer_gstin="27AAACZ8901L1ZA",
        buyer_contact_email="cfo@orbitretail.in",
        buyer_contact_phone="+91 98444 55667",
        invoice_date=inv4_date,
        delivery_date=inv4_date + timedelta(days=1),
        acceptance_date=inv4_date + timedelta(days=2),
        has_objection=False,
        has_written_agreement=True,
        agreed_credit_days=30,
        total_amount=175000.00,
        paid_amount=0.00,
        outstanding_balance=175000.00,
        status="overdue",
        goods_services_description="Winter fleece vests and custom staff jackets",
        notes="Debtor CFO confirmed full clearance scheduled for this Friday.",
    )
    db.add(inv4)
    db.flush()

    case4 = Case(
        invoice_id=inv4.id,
        reference_code="CASE-INV-2026-1015",
        current_stage=4,
        stage_label=STAGE_LABELS[4],
        priority="high",
        promised_payment_date=today + timedelta(days=3),  # Promised in 3 days!
        promised_payment_amount=175000.00,
        notes="Clearance promised on or before coming Friday by debtor CFO.",
    )
    db.add(case4)
    db.flush()

    for cat, title in DEFAULT_EVIDENCE_TEMPLATES:
        db.add(EvidenceItem(
            case_id=case4.id,
            category=cat,
            title=title,
            status="provided" if cat in ("invoice", "purchase_order", "delivery_proof", "udyam_certificate") else "needs_review",
        ))

    db.add(FollowUpEvent(
        case_id=case4.id,
        event_type="payment_promised",
        summary="Written promise to pay entire ₹1,75,000 balance received from CFO",
        detail="Debtor finance team confirmed clearance batch slated for coming Friday.",
        next_action_date=today + timedelta(days=3),
        performed_at=datetime.utcnow() - timedelta(days=2),
        recorded_by="Managing Director",
    ))

    # 6. Case 5: Requiring Legal / Eligibility Review (Active Dispute / Objection)
    inv5_date = today - timedelta(days=40)
    inv5 = Invoice(
        invoice_number="INV-2026-0955",
        business_profile_id=1,
        buyer_name="Delta Fashion House Pvt Ltd",
        buyer_gstin="08AABCD7722R1Z3",
        buyer_contact_email="disputes@deltafashion.com",
        buyer_contact_phone="+91 98555 66778",
        invoice_date=inv5_date,
        delivery_date=inv5_date + timedelta(days=1),
        has_objection=True,
        objection_date=inv5_date + timedelta(days=10),
        objection_resolved_date=None,  # Unresolved objection!
        has_written_agreement=True,
        agreed_credit_days=30,
        total_amount=310000.00,
        paid_amount=0.00,
        outstanding_balance=310000.00,
        status="escalated",
        goods_services_description="Designer uniform aprons and bespoke chef coats",
        notes="Buyer raised quality objection regarding fabric shade variance. Replacement samples submitted.",
    )
    db.add(inv5)
    db.flush()

    case5 = Case(
        invoice_id=inv5.id,
        reference_code="CASE-INV-2026-0955",
        current_stage=6,
        stage_label=STAGE_LABELS[6],
        priority="critical",
        notes="Active quality objection recorded. Statutory timeline paused until formal resolution under Section 2(a)(ii).",
    )
    db.add(case5)
    db.flush()

    for cat, title in DEFAULT_EVIDENCE_TEMPLATES:
        db.add(EvidenceItem(
            case_id=case5.id,
            category=cat,
            title=title,
            status="needs_review" if cat == "acceptance_record" else ("provided" if cat in ("invoice", "delivery_proof", "udyam_certificate") else "missing"),
            notes="Pending mutual sign-off on replacement swatch" if cat == "acceptance_record" else None,
        ))

    db.add(FollowUpEvent(
        case_id=case5.id,
        event_type="evidence_reviewed",
        summary="Legal Review: Quality objection pauses deemed acceptance window",
        detail="Section 2(a)(ii) MSMED Act requires objection removal before statutory clock resumes. Conciliation recommended.",
        performed_at=datetime.utcnow() - timedelta(days=4),
        recorded_by="Legal Counsel",
    ))

    # 7. Seed Fictional Contextual B2B Sponsored-Supplier Listings
    suppliers = [
        SupplierListing(
            company_name="Vardhman Industrial Threads Ltd",
            industry_category="garment_manufacturing",
            product_tags="polyester thread,cotton sewing thread,embroidery thread,high-tenacity yarn",
            contact_person="Sunil Malhotra (National Sales Head)",
            contact_email="b2b.sales@vardhman-threads.demo",
            contact_phone="+91 161 245 8890",
            city="Ludhiana",
            state="Punjab",
            is_sponsored=True,
            sponsorship_tier="featured",
            verified=True,
            description="Leading manufacturer of high-tenacity industrial sewing threads, polyester spun yarns, and specialized embroidery filaments for garment manufacturers across India.",
            min_order_quantity="100 Cones / 50 kg",
        ),
        SupplierListing(
            company_name="Surat TextFab Mills Pvt Ltd",
            industry_category="garment_manufacturing",
            product_tags="uniform fabric,cotton twill,polyester viscose,poly-cotton fabric,suiting",
            contact_person="Rajesh Singhal (Director Marketing)",
            contact_email="sales@surattextfab.demo",
            contact_phone="+91 261 289 1122",
            city="Surat",
            state="Gujarat",
            is_sponsored=True,
            sponsorship_tier="featured",
            verified=True,
            description="Specialized fabric mill weaving heavy-duty uniform fabrics, institutional suiting, anti-bacterial healthcare textiles, and cotton twills with mill-direct MSME pricing.",
            min_order_quantity="500 Meters",
        ),
        SupplierListing(
            company_name="TrimCraft Accessories & Buttons",
            industry_category="garment_manufacturing",
            product_tags="resin buttons,brass metal zippers,woven labels,elastic tapes,velcro",
            contact_person="Pooja Aggarwal (Key Accounts)",
            contact_email="enquiries@trimcraft.demo",
            contact_phone="+91 11 4522 9900",
            city="Okhla, New Delhi",
            state="Delhi NCR",
            is_sponsored=True,
            sponsorship_tier="standard",
            verified=True,
            description="Complete garment trims and accessories distributor. Oeko-Tex certified resin buttons, durable brass zippers, heat-transfer logos, and woven branding tapes.",
            min_order_quantity="1,000 Pieces",
        ),
        SupplierListing(
            company_name="PackWell Corrugated Cartons",
            industry_category="packaging",
            product_tags="corrugated boxes,shipping cartons,garment polybags,adhesive tape,packaging",
            contact_person="Harish Bhasin",
            contact_email="orders@packwellcartons.demo",
            contact_phone="+91 1795 244 511",
            city="Baddi",
            state="Himachal Pradesh",
            is_sponsored=True,
            sponsorship_tier="standard",
            verified=True,
            description="Heavy 3-ply and 5-ply export-grade shipping cartons, garment display polybags, and moisture-resistant packaging supplies for micro and small manufacturing units.",
            min_order_quantity="250 Boxes",
        ),
        SupplierListing(
            company_name="Juki & Singer Industrial Sewing Systems",
            industry_category="industrial_components",
            product_tags="industrial sewing machines,automatic buttonhole machines,cutting machines,machinery",
            contact_person="Vikram Mehra",
            contact_email="machinery@jukisystems.demo",
            contact_phone="+91 124 498 7766",
            city="Gurgaon",
            state="Haryana",
            is_sponsored=True,
            sponsorship_tier="featured",
            verified=True,
            description="Authorized machinery distributor offering direct-drive lockstitch sewing machines, computerized pattern stitchers, and fabric roll spreading equipment with MSME financing options.",
            min_order_quantity="1 Unit",
        ),
        SupplierListing(
            company_name="Apex Logistics & Freight Forwarders",
            industry_category="business_services",
            product_tags="freight forwarding,surface transport,transporter LR,warehouse storage",
            contact_person="Karanjit Singh",
            contact_email="cargo@apexlogistics.demo",
            contact_phone="+91 172 267 8901",
            city="Chandigarh",
            state="Chandigarh",
            is_sponsored=False,
            sponsorship_tier="standard",
            verified=True,
            description="Dedicated B2B pan-India surface logistics provider with digital proof of delivery (e-POD) tracking specifically designed to safeguard MSME invoice acceptance timelines.",
            min_order_quantity="Part Load / Full Truck Load",
        ),
    ]
    for s in suppliers:
        db.add(s)

    db.commit()
    print("Database successfully seeded with deterministic demonstration records.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db, force_reset=True)
    finally:
        db.close()
