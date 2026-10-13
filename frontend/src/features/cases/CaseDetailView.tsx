import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  AlertTriangle,
  Scale,
  FileCheck2,
  Download,
  Copy,
  Check,
  Send,
  Plus,
  ArrowRight,
  ShieldAlert,
  Calendar,
  Building,
  Clock,
  IndianRupee,
  ChevronDown,
  ChevronUp,
  FileText,
  BadgeAlert,
  Loader2,
  CheckCircle,
} from 'lucide-react';
import { api } from '../../services/api';
import { CaseDetail, ReminderDraft } from '../../types';

export const CaseDetailView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const caseId = id ? parseInt(id, 10) : 1;

  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Notice Studio State
  const [activeTone, setActiveTone] = useState<'friendly' | 'firm' | 'formal_notice'>('formal_notice');
  const [reminderDraft, setReminderDraft] = useState<ReminderDraft | null>(null);
  const [generatingDraft, setGeneratingDraft] = useState(false);
  const [copied, setCopied] = useState(false);

  // Trace Accordion
  const [showTrace, setShowTrace] = useState(false);

  // New Event Modal
  const [showEventModal, setShowEventModal] = useState(false);
  const [eventType, setEventType] = useState('phone_call');
  const [eventSummary, setEventSummary] = useState('');
  const [eventDetail, setEventDetail] = useState('');
  const [nextActionDate, setNextActionDate] = useState('');
  const [savingEvent, setSavingEvent] = useState(false);

  // Stage Advancement State
  const [advancingStage, setAdvancingStage] = useState(false);

  const fetchCase = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getCase(caseId);
      setCaseData(data);
      // Generate draft
      loadReminderDraft('formal_notice');
    } catch (err: any) {
      setError(err.message || 'Failed to load case detail');
    } finally {
      setLoading(false);
    }
  };

  const loadReminderDraft = async (tone: 'friendly' | 'firm' | 'formal_notice') => {
    try {
      setGeneratingDraft(true);
      setActiveTone(tone);
      const draft = await api.generateReminderDraft(caseId, tone);
      setReminderDraft(draft);
    } catch (err: any) {
      console.error(err);
    } finally {
      setGeneratingDraft(false);
    }
  };

  useEffect(() => {
    fetchCase();
  }, [caseId]);

  const handleCopyDraft = () => {
    if (!reminderDraft) return;
    navigator.clipboard.writeText(reminderDraft.body_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleAdvanceStage = async (targetStage: number) => {
    if (!caseData) return;
    try {
      setAdvancingStage(true);
      const updated = await api.updateCaseStage(caseId, targetStage);
      setCaseData(updated);
    } catch (err: any) {
      alert('Failed to update stage: ' + err.message);
    } finally {
      setAdvancingStage(false);
    }
  };

  const handleToggleEvidenceStatus = async (itemId: number, currentStatus: string) => {
    const nextStatusMap: Record<string, 'provided' | 'missing' | 'needs_review' | 'not_applicable'> = {
      missing: 'provided',
      provided: 'needs_review',
      needs_review: 'missing',
      not_applicable: 'missing',
    };
    const nextStatus = nextStatusMap[currentStatus] || 'provided';
    try {
      await api.updateEvidenceItem(caseId, itemId, { status: nextStatus });
      // Refresh case data
      const updated = await api.getCase(caseId);
      setCaseData(updated);
    } catch (err: any) {
      alert('Failed to update evidence item: ' + err.message);
    }
  };

  const handleAddEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!eventSummary) return;
    try {
      setSavingEvent(true);
      await api.addFollowUpEvent(caseId, {
        event_type: eventType,
        summary: eventSummary,
        detail: eventDetail || undefined,
        next_action_date: nextActionDate || undefined,
      });
      setShowEventModal(false);
      setEventSummary('');
      setEventDetail('');
      setNextActionDate('');
      const updated = await api.getCase(caseId);
      setCaseData(updated);
    } catch (err: any) {
      alert('Failed to record follow-up event: ' + err.message);
    } finally {
      setSavingEvent(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] space-y-3">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <p className="text-sm text-slate-500 font-medium">Assembling legal timeline and evidence matrix...</p>
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center max-w-lg mx-auto mt-12 shadow-sm space-y-3">
        <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto">
          <Scale className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-slate-800">No Escalation Case Selected</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto leading-relaxed">
          {error?.includes('404') || error?.includes('Not found')
            ? 'This case record is not available in your current MSME workspace. To track statutory escalation, review evidence completeness, and prepare Section 16 notices, choose an invoice from your ledger.'
            : error || 'Unable to retrieve case information.'}
        </p>
        <Link
          to="/invoices"
          className="mt-3 inline-flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
        >
          <span>View Invoices & Escalate</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    );
  }

  const inv = caseData.invoice;
  const timeline = caseData.timeline;
  const comp = caseData.completeness_summary;

  const stagesList = [
    { num: 1, label: 'Invoice Recorded' },
    { num: 2, label: 'Payment Due Approaching' },
    { num: 3, label: 'Friendly Reminder' },
    { num: 4, label: 'Follow-up Logged' },
    { num: 5, label: 'Formal Notice Draft' },
    { num: 6, label: 'Evidence Audit' },
    { num: 7, label: 'Report Generated' },
    { num: 8, label: 'MSEFC Filing Identified' },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-mono text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-bold">
              {caseData.reference_code}
            </span>
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                caseData.priority === 'critical' || caseData.priority === 'high'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-blue-100 text-blue-800'
              }`}
            >
              {caseData.priority} Priority
            </span>
            <span className="bg-emerald-100 text-emerald-800 text-xs px-2.5 py-0.5 rounded-full font-bold">
              {caseData.stage_label} (Stage {caseData.current_stage}/8)
            </span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 mt-2">
            Commercial Debt Escalation: {inv.buyer_name}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Invoice #{inv.invoice_number} • Issued: {inv.invoice_date} • Statutory Maturity: {timeline.calculated_due_date}
          </p>
        </div>

        {/* Primary Action: Download PDF Report */}
        <div className="flex items-center space-x-3 shrink-0">
          <a
            href={api.downloadReportPdfUrl(caseData.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2.5 rounded-lg shadow-sm transition-colors flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download Case-Prep Report (PDF)</span>
          </a>
        </div>
      </div>

      {/* 8-Stage Interactive Stepper */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Escalation Progression Stepper
            </h2>
            <p className="text-[11px] text-slate-400">
              Click any stage to transition case status, or use quick advance.
            </p>
          </div>
          {caseData.current_stage < 8 && (
            <button
              onClick={() => handleAdvanceStage(caseData.current_stage + 1)}
              disabled={advancingStage}
              className="bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 px-3 py-1.5 rounded-md text-xs font-semibold flex items-center space-x-1.5 transition-colors"
            >
              {advancingStage ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ArrowRight className="w-3.5 h-3.5" />}
              <span>Advance to Stage {caseData.current_stage + 1}</span>
            </button>
          )}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {stagesList.map((st) => {
            const isCurrent = st.num === caseData.current_stage;
            const isCompleted = st.num < caseData.current_stage;
            return (
              <button
                key={st.num}
                onClick={() => handleAdvanceStage(st.num)}
                className={`p-2.5 rounded-xl border text-left transition-all ${
                  isCurrent
                    ? 'bg-blue-600 text-white border-blue-600 shadow-sm ring-2 ring-blue-600/20'
                    : isCompleted
                    ? 'bg-blue-50/80 border-blue-200 text-blue-900 hover:bg-blue-100'
                    : 'bg-slate-50 border-slate-200 text-slate-400 hover:bg-slate-100 hover:text-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-[10px] font-bold uppercase ${isCurrent ? 'text-blue-100' : 'text-slate-400'}`}>
                    Stage {st.num}
                  </span>
                  {isCompleted && <CheckCircle className="w-3 h-3 text-blue-600" />}
                </div>
                <div className="text-xs font-semibold line-clamp-2 leading-tight">
                  {st.label}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Ledger, Legal Engine, Evidence Matrix (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Invoice Summary Card */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-600" />
                <span>Invoice & Commercial Ledger</span>
              </h3>
              <span className="font-mono text-xs text-slate-500 font-semibold">
                #{inv.invoice_number}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-[10px] text-slate-500 uppercase font-semibold">Invoice Total</span>
                <div className="text-base font-bold text-slate-900 mt-0.5">
                  ₹{inv.total_amount.toLocaleString('en-IN')}
                </div>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-[10px] text-slate-500 uppercase font-semibold">Amount Received</span>
                <div className="text-base font-bold text-emerald-700 mt-0.5">
                  ₹{inv.paid_amount.toLocaleString('en-IN')}
                </div>
              </div>
              <div className="p-3 bg-red-50 rounded-lg border border-red-100">
                <span className="text-[10px] text-red-600 uppercase font-semibold">Outstanding Dues</span>
                <div className="text-base font-bold text-red-600 mt-0.5">
                  ₹{inv.outstanding_balance.toLocaleString('en-IN')}
                </div>
              </div>
            </div>

            {inv.goods_services_description && (
              <div className="text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-slate-700">
                <span className="font-semibold text-slate-800">Supplied Goods/Services:</span>{' '}
                {inv.goods_services_description}
              </div>
            )}
          </div>

          {/* Legal Engine: Section 15, 16 & 43B(h) Breakdown */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <Scale className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Deterministic MSMED Act Legal Engine
                </h3>
              </div>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-bold px-2 py-0.5 rounded-full">
                Sections 15 & 16 Verified
              </span>
            </div>

            {/* Critical Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-400 font-semibold uppercase">Reference Date</span>
                <div className="font-bold text-slate-800 mt-0.5">{timeline.reference_date}</div>
                <div className="text-[10px] text-slate-500 capitalize">{timeline.reference_type.replace(/_/g, ' ')}</div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-400 font-semibold uppercase">Statutory Term</span>
                <div className="font-bold text-slate-800 mt-0.5">{timeline.statutory_term_days} Days</div>
                <div className="text-[10px] text-amber-700 font-semibold">
                  {timeline.statutory_term_capped ? 'Capped at 45d' : 'Agreed term'}
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-400 font-semibold uppercase">Days Overdue</span>
                <div className={`font-bold mt-0.5 ${timeline.is_overdue ? 'text-red-600' : 'text-emerald-700'}`}>
                  {timeline.is_overdue ? `${timeline.days_overdue} Days Past Due` : 'Within Term'}
                </div>
                <div className="text-[10px] text-slate-500">Maturity: {timeline.calculated_due_date}</div>
              </div>

              <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                <span className="text-[10px] text-emerald-700 font-semibold uppercase">Statutory Interest Rate</span>
                <div className="font-bold text-emerald-800 mt-0.5">
                  {timeline.annual_statutory_interest_rate_pct}% p.a.
                </div>
                <div className="text-[10px] text-emerald-600">3x RBI Bank Rate (6.75%)</div>
              </div>
            </div>

            {/* Interest Compounder Result Box */}
            <div className="bg-gradient-to-r from-blue-900 to-slate-900 rounded-xl p-4 text-white shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold text-blue-300 uppercase tracking-wider">
                  Accrued Statutory Compound Interest (Section 16)
                </span>
                <div className="text-xl font-extrabold text-white mt-0.5">
                  ₹{timeline.estimated_interest.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
                <p className="text-[11px] text-slate-300 mt-0.5">
                  Compounded monthly for {timeline.interest_breakdown.full_months} months & {timeline.interest_breakdown.residual_days} residual days
                </p>
              </div>
              <div className="text-right sm:border-l sm:border-slate-700 sm:pl-5">
                <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">
                  Total Claimable Debt
                </span>
                <div className="text-2xl font-black text-emerald-400">
                  ₹{timeline.total_claimable_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
                <span className="text-[10px] text-slate-400">Principal + Compound Interest</span>
              </div>
            </div>

            {/* Section 43B(h) Risk Banner */}
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 text-xs text-amber-900 flex items-start space-x-2.5">
              <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Income Tax Act Section 43B(h) Leverage:</span>
                <p className="text-[11px] text-amber-800 mt-0.5 leading-relaxed">
                  {timeline.section_43b_h_impact}
                </p>
              </div>
            </div>

            {/* Expandable Trace */}
            <div>
              <button
                onClick={() => setShowTrace(!showTrace)}
                className="text-xs text-blue-600 font-semibold flex items-center space-x-1 hover:text-blue-800"
              >
                <span>{showTrace ? 'Hide' : 'View'} Traceable Legal Proof & Calculation Formula</span>
                {showTrace ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showTrace && (
                <div className="mt-2 p-3 bg-slate-50 border border-slate-200 rounded-lg text-[11px] font-mono text-slate-700 space-y-1.5 animate-fadeIn">
                  {timeline.calculation_trace.map((tr, idx) => (
                    <div key={idx} className="flex items-start space-x-1.5">
                      <span className="text-blue-600 font-bold">•</span>
                      <span>{tr}</span>
                    </div>
                  ))}
                  <div className="pt-2 text-[10px] text-slate-500 italic">
                    {timeline.disclaimer}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Evidence Completeness Checker (Checklist) */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                  <FileCheck2 className="w-4 h-4 text-emerald-600" />
                  <span>Evidence Completeness Audit (MSEFC Readiness)</span>
                </h3>
                <p className="text-[11px] text-slate-500">
                  Pre-litigation check before initiating official Samadhaan proceedings
                </p>
              </div>
              <div className="text-right">
                <span className="text-xs font-bold text-slate-800">
                  {comp.completeness_percentage}% Verified
                </span>
                <div className="w-24 bg-slate-100 h-1.5 rounded-full overflow-hidden mt-1">
                  <div
                    className="bg-emerald-600 h-full rounded-full transition-all"
                    style={{ width: `${comp.completeness_percentage}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="divide-y divide-slate-100 text-xs">
              {caseData.evidence_items.map((it) => {
                const statusStyles: Record<string, string> = {
                  provided: 'bg-emerald-50 text-emerald-800 border-emerald-200',
                  missing: 'bg-red-50 text-red-800 border-red-200',
                  needs_review: 'bg-amber-50 text-amber-800 border-amber-200',
                  not_applicable: 'bg-slate-50 text-slate-600 border-slate-200',
                };
                return (
                  <div key={it.id} className="py-2.5 flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-slate-800">{it.title}</div>
                      <div className="text-[11px] text-slate-400 capitalize">
                        {it.category.replace(/_/g, ' ')} • {it.file_name ? it.file_name : 'No digital file attached'}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleToggleEvidenceStatus(it.id, it.status)}
                        title="Click to toggle status"
                        className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider border cursor-pointer hover:opacity-80 transition-all ${
                          statusStyles[it.status] || statusStyles.missing
                        }`}
                      >
                        {it.status.replace(/_/g, ' ')}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Chronological Event History & Log Action */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-900">
                Chronological Communication & Event Log
              </h3>
              <button
                onClick={() => setShowEventModal(true)}
                className="bg-slate-100 hover:bg-slate-200 text-slate-800 px-3 py-1.5 rounded-md text-xs font-semibold flex items-center space-x-1 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Log Action</span>
              </button>
            </div>

            <div className="divide-y divide-slate-100 text-xs">
              {caseData.follow_up_events.map((ev) => (
                <div key={ev.id} className="py-2.5 flex items-start justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-slate-800">{ev.summary}</span>
                      <span className="bg-slate-100 text-slate-600 px-1.5 py-0.2 rounded text-[10px] capitalize">
                        {ev.event_type.replace(/_/g, ' ')}
                      </span>
                    </div>
                    {ev.detail && <p className="text-slate-600 text-[11px]">{ev.detail}</p>}
                    {ev.next_action_date && (
                      <span className="inline-block text-[10px] text-amber-700 font-semibold bg-amber-50 px-1.5 py-0.2 rounded">
                        Next Action: {ev.next_action_date}
                      </span>
                    )}
                  </div>
                  <div className="text-right text-[10px] text-slate-400 shrink-0 ml-3">
                    <div>{new Date(ev.performed_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}</div>
                    <div className="text-slate-500 font-medium">{ev.recorded_by}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Pre-Litigation Notice Studio (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4 sticky top-20">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Pre-Litigation Notice Studio
                </h3>
                <p className="text-[11px] text-slate-500">
                  Editable draft communications grounded in verified case data
                </p>
              </div>
              <button
                onClick={handleCopyDraft}
                className="bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 px-3 py-1.5 rounded-md text-xs font-semibold flex items-center space-x-1.5 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied!' : 'Copy Draft'}</span>
              </button>
            </div>

            {/* Tone Selector Tabs */}
            <div className="flex p-1 bg-slate-100 rounded-lg text-xs font-semibold">
              <button
                onClick={() => loadReminderDraft('friendly')}
                className={`flex-1 py-1.5 rounded-md text-center transition-all ${
                  activeTone === 'friendly' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Friendly
              </button>
              <button
                onClick={() => loadReminderDraft('firm')}
                className={`flex-1 py-1.5 rounded-md text-center transition-all ${
                  activeTone === 'firm' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Urgent Notice
              </button>
              <button
                onClick={() => loadReminderDraft('formal_notice')}
                className={`flex-1 py-1.5 rounded-md text-center transition-all ${
                  activeTone === 'formal_notice' ? 'bg-white text-blue-900 shadow-xs font-bold' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Formal Demand (Sec 15/16)
              </button>
            </div>

            {/* Draft Preview Body */}
            {generatingDraft ? (
              <div className="py-16 text-center flex flex-col items-center justify-center space-y-2">
                <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
                <p className="text-xs text-slate-500 font-medium">Interpolating case parameters and statutory citations...</p>
              </div>
            ) : reminderDraft ? (
              <div className="space-y-3">
                <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-xs">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Subject Line</span>
                  <p className="font-semibold text-slate-900 mt-0.5">{reminderDraft.subject}</p>
                </div>

                <div className="bg-slate-900 text-slate-100 p-4 rounded-xl font-mono text-[11px] leading-relaxed max-h-[380px] overflow-y-auto whitespace-pre-wrap select-all">
                  {reminderDraft.body_markdown}
                </div>

                {/* Review Disclaimer */}
                <div className="p-3 bg-amber-50/70 border border-amber-200/80 rounded-lg text-[10px] text-amber-900 leading-normal">
                  <span className="font-bold">Administrative Aid Disclaimer:</span>{' '}
                  {reminderDraft.review_disclaimer}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>

      {/* Log Action Modal */}
      {showEventModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4 animate-scaleUp">
            <h3 className="text-sm font-bold text-slate-900">Log Escalation Action</h3>
            <form onSubmit={handleAddEvent} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Action Type</label>
                <select
                  value={eventType}
                  onChange={(e) => setEventType(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="phone_call">Telephonic Follow-Up</option>
                  <option value="email_follow_up">Email Follow-Up</option>
                  <option value="payment_promised">Payment Promised</option>
                  <option value="formal_notice_served">Formal Notice Served</option>
                  <option value="evidence_reviewed">Evidence Reviewed</option>
                  <option value="samadhaan_application_prepared">Samadhaan Petition Prepared</option>
                  <option value="custom">Other Action</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Action Summary *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Telephonic call with VP Finance"
                  value={eventSummary}
                  onChange={(e) => setEventSummary(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Discussion Detail</label>
                <textarea
                  rows={3}
                  placeholder="e.g. Debtor confirmed bill is approved; awaiting cheque dispatch."
                  value={eventDetail}
                  onChange={(e) => setEventDetail(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Next Follow-Up Date</label>
                <input
                  type="date"
                  value={nextActionDate}
                  onChange={(e) => setNextActionDate(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowEventModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingEvent}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg shadow-sm transition-colors flex items-center space-x-1"
                >
                  {savingEvent && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Save Event</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
