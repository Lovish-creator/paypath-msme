import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  IndianRupee,
  Clock,
  AlertCircle,
  Calendar,
  CheckCircle,
  ArrowRight,
  TrendingUp,
  History,
  FileText,
  BadgeAlert,
  Loader2,
} from 'lucide-react';
import { api } from '../../services/api';
import { DashboardData } from '../../types';

export const DashboardView: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getDashboard();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] space-y-3">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <p className="text-sm text-slate-500 font-medium">Computing deterministic receivables ledger...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center max-w-lg mx-auto mt-12">
        <AlertCircle className="w-10 h-10 text-red-600 mx-auto mb-3" />
        <h3 className="text-base font-bold text-red-900">Failed to connect to backend engine</h3>
        <p className="text-sm text-red-700 mt-1">{error}</p>
        <button
          onClick={fetchDashboard}
          className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-semibold rounded-md shadow-sm"
        >
          Retry Computation
        </button>
      </div>
    );
  }

  const stageKeys = Object.keys(data.stage_breakdown);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 rounded-2xl p-6 text-white shadow-md border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="bg-blue-500/20 text-blue-300 text-xs font-bold px-2.5 py-0.5 rounded-full border border-blue-400/30">
                STATUTORY CASHFLOW MONITOR
              </span>
              <span className="text-xs text-slate-400">Micro & Small Enterprise Protection</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight mt-1 text-white">
              Apex Uniforms & Apparel — Receivables Dashboard
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Real-time monitoring of commercial debts under the Micro, Small and Medium Enterprises Development (MSMED) Act, 2006. All figures reflect verified invoice records.
            </p>
          </div>
          <div className="flex items-center space-x-3 shrink-0">
            <Link
              to="/invoices"
              className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2.5 rounded-lg shadow-sm transition-colors flex items-center space-x-1.5"
            >
              <span>Manage Invoices</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Outstanding */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Outstanding</span>
            <div className="p-1.5 rounded-md bg-blue-50 text-blue-600">
              <IndianRupee className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{data.formatted_total_outstanding}</div>
          <p className="text-[11px] text-slate-500 mt-1">
            Across {data.total_invoices_count} total invoiced orders
          </p>
        </div>

        {/* Total Overdue */}
        <div className="bg-white border border-red-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between text-red-600 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Overdue Dues</span>
            <div className="p-1.5 rounded-md bg-red-50 text-red-600">
              <BadgeAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-red-600">{data.formatted_total_overdue}</div>
          <p className="text-[11px] text-red-700 font-medium mt-1">
            {data.overdue_invoices_count} delinquent buyers past credit term
          </p>
        </div>

        {/* Approaching Due Date */}
        <div className="bg-white border border-amber-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between text-amber-700 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Due Soon (14 Days)</span>
            <div className="p-1.5 rounded-md bg-amber-50 text-amber-600">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-amber-800">{data.approaching_due_count}</div>
          <p className="text-[11px] text-amber-700 mt-1">
            Maturity approaching statutory cap
          </p>
        </div>

        {/* Awaiting Follow-up */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Awaiting Follow-Up</span>
            <div className="p-1.5 rounded-md bg-purple-50 text-purple-600">
              <History className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{data.cases_awaiting_followup_count}</div>
          <p className="text-[11px] text-slate-500 mt-1">
            No action recorded in last 7 days
          </p>
        </div>

        {/* Promised Payments */}
        <div className="bg-white border border-emerald-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between text-emerald-700 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Payment Promises</span>
            <div className="p-1.5 rounded-md bg-emerald-50 text-emerald-600">
              <CheckCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-emerald-700">{data.promised_payments_count}</div>
          <p className="text-[11px] text-emerald-700 mt-1">
            Active clearance commitments
          </p>
        </div>
      </div>

      {/* Escalation Stage Progression */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-slate-900">
              Statutory 8-Stage Escalation Funnel
            </h2>
            <p className="text-xs text-slate-500">
              Systematic progression from invoice recording to official MSEFC conciliation readiness
            </p>
          </div>
          <span className="text-xs font-medium text-slate-400">Total Cases: {data.total_invoices_count}</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {stageKeys.map((stageKey, idx) => {
            const count = data.stage_breakdown[stageKey] || 0;
            const stageNum = idx + 1;
            const isActive = count > 0;
            return (
              <div
                key={stageKey}
                className={`p-3 rounded-lg border text-center transition-all ${
                  isActive
                    ? 'bg-blue-50/70 border-blue-200 text-blue-900'
                    : 'bg-slate-50/40 border-slate-100 text-slate-400'
                }`}
              >
                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                  Stage {stageNum}
                </div>
                <div className={`text-xl font-extrabold my-1 ${isActive ? 'text-blue-700' : 'text-slate-400'}`}>
                  {count}
                </div>
                <div className="text-[11px] font-medium leading-tight truncate" title={stageKey}>
                  {stageKey.replace(/Stage \d+: /, '')}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Two Column Section: Approaching Due & Promised Payments */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Approaching Due Date Table */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-amber-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Approaching Statutory Maturity (Next 14 Days)
                </h3>
              </div>
              <span className="text-xs text-slate-400 font-medium">{data.approaching_invoices.length} Invoices</span>
            </div>

            {data.approaching_invoices.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">
                No invoices currently due within 14 days.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {data.approaching_invoices.map((inv) => (
                  <div key={inv.invoice_id} className="py-2.5 flex items-center justify-between text-xs">
                    <div>
                      <div className="font-semibold text-slate-800">{inv.buyer_name}</div>
                      <div className="text-[11px] text-slate-400">Invoice: #{inv.invoice_number}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-slate-900">₹{inv.outstanding_balance.toLocaleString('en-IN')}</div>
                      <span className="inline-block bg-amber-50 text-amber-700 border border-amber-200 px-1.5 py-0.5 rounded text-[10px] font-semibold">
                        {inv.days_remaining} days left ({inv.due_date})
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 text-right">
            <Link to="/invoices" className="text-xs text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center space-x-1">
              <span>View All Invoices</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </div>

        {/* Promised Payments & Alerts */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-emerald-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Debtor Payment Commitments & Promises
                </h3>
              </div>
              <span className="text-xs text-slate-400 font-medium">{data.promised_payment_alerts.length} Recorded</span>
            </div>

            {data.promised_payment_alerts.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">
                No active promised payment commitments logged.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {data.promised_payment_alerts.map((alert) => (
                  <div key={alert.case_id} className="py-2.5 flex items-center justify-between text-xs">
                    <div>
                      <div className="font-semibold text-slate-800">{alert.buyer_name}</div>
                      <div className="text-[11px] text-slate-400">{alert.case_reference}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-emerald-700">₹{alert.promised_amount.toLocaleString('en-IN')}</div>
                      <span
                        className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold border ${
                          alert.is_overdue
                            ? 'bg-red-50 text-red-700 border-red-200'
                            : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        }`}
                      >
                        {alert.is_overdue ? 'Promise Breached' : `Promised by ${alert.promised_date}`}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 text-right">
            <Link to="/cases/1" className="text-xs text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center space-x-1">
              <span>View Case Detail</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </div>

      {/* Chronological Activity Feed */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <History className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Recent Case Escalation Activity
            </h3>
          </div>
          <span className="text-xs text-slate-400">Chronological Event Trail</span>
        </div>

        <div className="divide-y divide-slate-100">
          {data.recent_followups.map((ev) => (
            <div key={ev.id} className="py-3 flex items-start justify-between text-xs">
              <div className="space-y-0.5">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-slate-800">{ev.buyer_name}</span>
                  <span className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded text-[10px] font-mono">
                    {ev.case_reference}
                  </span>
                  <span className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded text-[10px] font-medium capitalize">
                    {ev.event_type.replace(/_/g, ' ')}
                  </span>
                </div>
                <p className="text-slate-600 text-xs">{ev.summary}</p>
              </div>
              <div className="text-right text-[11px] text-slate-400 shrink-0 ml-4">
                <div>{new Date(ev.performed_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}</div>
                <div className="text-[10px] text-slate-500 font-medium">{ev.recorded_by}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
