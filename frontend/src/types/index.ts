export interface Payment {
  id: number;
  invoice_id: number;
  payment_date: string;
  amount: number;
  reference_number?: string;
  payment_mode?: string;
  notes?: string;
  created_at: string;
}

export interface CaseSummary {
  id: number;
  reference_code: string;
  current_stage: number;
  stage_label: string;
  priority: string;
  promised_payment_date?: string;
  promised_payment_amount?: number;
}

export interface TimelineData {
  reference_date: string;
  reference_type: string;
  statutory_term_days: number;
  statutory_term_capped: boolean;
  statutory_rule_citation: string;
  calculated_due_date: string;
  evaluation_date: string;
  is_overdue: boolean;
  days_overdue: number;
  days_remaining: number;
  outstanding_principal: number;
  rbi_bank_rate_pct: number;
  annual_statutory_interest_rate_pct: number;
  estimated_interest: number;
  total_claimable_amount: number;
  interest_breakdown: {
    principal: number;
    full_months: number;
    residual_days: number;
    monthly_interest_rate_pct: number;
    annual_interest_rate_pct: number;
    compounded_amount: number;
    estimated_interest: number;
  };
  section_43b_h_applicable: boolean;
  section_43b_h_impact: string;
  eligibility_status: string;
  warnings: string[];
  calculation_trace: string[];
  disclaimer: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  business_profile_id: number;
  buyer_id?: number;
  buyer_name: string;
  buyer_gstin?: string;
  buyer_contact_email?: string;
  buyer_contact_phone?: string;
  invoice_date: string;
  delivery_date?: string;
  acceptance_date?: string;
  has_objection: boolean;
  objection_date?: string;
  objection_resolved_date?: string;
  has_written_agreement: boolean;
  agreed_credit_days?: number;
  total_amount: number;
  paid_amount: number;
  outstanding_balance: number;
  status: 'draft' | 'issued' | 'partially_paid' | 'paid' | 'overdue' | 'escalated';
  goods_services_description?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  payments: Payment[];
  case?: CaseSummary;
  timeline?: TimelineData;
}

export interface EvidenceItem {
  id: number;
  case_id: number;
  category: string;
  title: string;
  status: 'provided' | 'missing' | 'not_applicable' | 'needs_review';
  file_name?: string;
  file_size_bytes?: number;
  uploaded_at?: string;
  notes?: string;
}

export interface FollowUpEvent {
  id: number;
  case_id: number;
  event_type: string;
  performed_at: string;
  summary: string;
  detail?: string;
  next_action_date?: string;
  recorded_by: string;
}

export interface CompletenessSummary {
  total_items: number;
  provided_count: number;
  missing_count: number;
  needs_review_count: number;
  not_applicable_count: number;
  completeness_percentage: number;
  is_fileable: boolean;
}

export interface CaseDetail {
  id: number;
  invoice_id: number;
  reference_code: string;
  current_stage: number;
  stage_label: string;
  priority: string;
  promised_payment_date?: string;
  promised_payment_amount?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  invoice: Invoice;
  evidence_items: EvidenceItem[];
  follow_up_events: FollowUpEvent[];
  timeline: TimelineData;
  completeness_summary: CompletenessSummary;
}

export interface ReminderDraft {
  tone: string;
  subject: string;
  body_markdown: string;
  notice_title: string;
  has_statutory_citations: boolean;
  review_disclaimer: string;
  created_at: string;
}

export interface ApproachingInvoice {
  invoice_id: number;
  invoice_number: string;
  buyer_name: string;
  outstanding_balance: number;
  due_date: string;
  days_remaining: number;
}

export interface PromisedPaymentAlert {
  case_id: number;
  case_reference: string;
  buyer_name: string;
  promised_amount: number;
  promised_date: string;
  is_overdue: boolean;
}

export interface DashboardData {
  total_outstanding_amount: number;
  total_overdue_amount: number;
  total_invoices_count: number;
  overdue_invoices_count: number;
  approaching_due_count: number;
  cases_awaiting_followup_count: number;
  promised_payments_count: number;
  formatted_total_outstanding: string;
  formatted_total_overdue: string;
  stage_breakdown: Record<string, number>;
  approaching_invoices: ApproachingInvoice[];
  promised_payment_alerts: PromisedPaymentAlert[];
  recent_followups: Array<{
    id: number;
    case_reference: string;
    buyer_name: string;
    event_type: string;
    summary: string;
    performed_at: string;
    recorded_by: string;
  }>;
}

export interface SupplierListing {
  id: number;
  company_name: string;
  industry_category: string;
  product_tags: string;
  contact_person: string;
  contact_email: string;
  contact_phone: string;
  city: string;
  state: string;
  is_sponsored: boolean;
  sponsorship_tier: string;
  verified: boolean;
  description: string;
  min_order_quantity?: string;
  created_at: string;
}

export interface SupplierEnquiry {
  id: number;
  supplier_id: number;
  business_profile_id?: number;
  requester_company_name: string;
  requester_name: string;
  requester_email: string;
  requester_phone: string;
  product_interest: string;
  message: string;
  consent_given: boolean;
  consent_timestamp: string;
  created_at: string;
}

export interface BusinessProfile {
  id: number;
  name: string;
  enterprise_type: string;
  udyam_number: string;
  pan?: string;
  gstin?: string;
  state: string;
  district: string;
  industry_category: string;
  purchasing_interests: string;
  contact_email: string;
  contact_phone: string;
  created_at: string;
}
