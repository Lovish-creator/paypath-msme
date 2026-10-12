import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Plus,
  Search,
  Filter,
  CreditCard,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  IndianRupee,
  Building,
  FileCheck,
  Loader2,
  X,
} from 'lucide-react';
import { api } from '../../services/api';
import { Invoice } from '../../types';

export const InvoicesView: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [overdueOnly, setOverdueOnly] = useState(false);

  // Create Invoice Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newInvoiceData, setNewInvoiceData] = useState({
    invoice_number: '',
    buyer_name: '',
    buyer_gstin: '',
    buyer_contact_email: '',
    buyer_contact_phone: '',
    invoice_date: new Date().toISOString().split('T')[0],
    delivery_date: new Date().toISOString().split('T')[0],
    has_written_agreement: true,
    agreed_credit_days: 30,
    total_amount: '',
    goods_services_description: '',
  });
  const [creating, setCreating] = useState(false);

  // Record Payment Modal
  const [paymentModalInvoice, setPaymentModalInvoice] = useState<Invoice | null>(null);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().split('T')[0]);
  const [paymentRef, setPaymentRef] = useState('');
  const [paymentMode, setPaymentMode] = useState('Bank Transfer (NEFT/RTGS)');
  const [recordingPayment, setRecordingPayment] = useState(false);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const data = await api.getInvoices({
        search: searchTerm || undefined,
        status: statusFilter || undefined,
        overdue_only: overdueOnly || undefined,
      });
      setInvoices(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch invoices');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, [statusFilter, overdueOnly]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchInvoices();
  };

  const handleCreateInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newInvoiceData.invoice_number || !newInvoiceData.buyer_name || !newInvoiceData.total_amount) {
      alert('Please fill all mandatory fields (Invoice Number, Buyer Name, Total Amount).');
      return;
    }
    try {
      setCreating(true);
      await api.createInvoice({
        ...newInvoiceData,
        total_amount: parseFloat(newInvoiceData.total_amount),
        agreed_credit_days: Number(newInvoiceData.agreed_credit_days),
      });
      setShowCreateModal(false);
      setNewInvoiceData({
        invoice_number: '',
        buyer_name: '',
        buyer_gstin: '',
        buyer_contact_email: '',
        buyer_contact_phone: '',
        invoice_date: new Date().toISOString().split('T')[0],
        delivery_date: new Date().toISOString().split('T')[0],
        has_written_agreement: true,
        agreed_credit_days: 30,
        total_amount: '',
        goods_services_description: '',
      });
      fetchInvoices();
    } catch (err: any) {
      alert('Failed to record invoice: ' + err.message);
    } finally {
      setCreating(false);
    }
  };

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!paymentModalInvoice) return;
    const amountNum = parseFloat(paymentAmount);
    if (isNaN(amountNum) || amountNum <= 0) {
      alert('Please enter a valid positive payment amount.');
      return;
    }
    if (amountNum > paymentModalInvoice.outstanding_balance) {
      alert(`Payment amount (₹${amountNum.toLocaleString('en-IN')}) cannot exceed outstanding balance (₹${paymentModalInvoice.outstanding_balance.toLocaleString('en-IN')}).`);
      return;
    }
    try {
      setRecordingPayment(true);
      await api.recordPayment(paymentModalInvoice.id, {
        amount: amountNum,
        payment_date: paymentDate,
        reference_number: paymentRef || undefined,
        payment_mode: paymentMode,
      });
      setPaymentModalInvoice(null);
      setPaymentAmount('');
      setPaymentRef('');
      fetchInvoices();
    } catch (err: any) {
      alert('Failed to record payment: ' + err.message);
    } finally {
      setRecordingPayment(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Invoices & Commercial Receivables Ledger
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Deterministic statutory tracking with automatic payment balance reconciliation
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2.5 rounded-lg shadow-sm transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Record New Invoice</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="w-full md:w-96 relative">
          <input
            type="text"
            placeholder="Search invoice number, buyer name, or GSTIN..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
        </form>

        <div className="flex items-center space-x-3 w-full md:w-auto justify-end">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="issued">Issued / Normal</option>
            <option value="partially_paid">Partially Paid</option>
            <option value="overdue">Overdue</option>
            <option value="paid">Fully Settled</option>
            <option value="escalated">Under Escalation</option>
          </select>

          <label className="flex items-center space-x-2 text-xs text-slate-700 font-medium cursor-pointer select-none">
            <input
              type="checkbox"
              checked={overdueOnly}
              onChange={(e) => setOverdueOnly(e.target.checked)}
              className="rounded text-red-600 focus:ring-red-500 w-4 h-4"
            />
            <span>Overdue Dues Only</span>
          </label>
        </div>
      </div>

      {/* Invoices Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center flex flex-col items-center justify-center space-y-2">
            <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            <p className="text-xs text-slate-500 font-medium">Loading invoice records...</p>
          </div>
        ) : invoices.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs">
            No invoices match the specified criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3 px-4">Invoice #</th>
                  <th className="py-3 px-4">Buyer / Debtor</th>
                  <th className="py-3 px-4">Dates</th>
                  <th className="py-3 px-4">Credit Terms</th>
                  <th className="py-3 px-4">Financial Ledger</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {invoices.map((inv) => {
                  const isOverdue = inv.status === 'overdue' || (inv.timeline && inv.timeline.is_overdue);
                  return (
                    <tr key={inv.id} className="hover:bg-slate-50/80 transition-colors">
                      {/* Invoice # */}
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                        {inv.invoice_number}
                        {inv.case && (
                          <div className="text-[10px] text-blue-600 font-normal mt-0.5">
                            {inv.case.reference_code}
                          </div>
                        )}
                      </td>

                      {/* Buyer */}
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-slate-800">{inv.buyer_name}</div>
                        <div className="text-[11px] text-slate-400">
                          {inv.buyer_gstin ? `GST: ${inv.buyer_gstin}` : 'GSTIN unrecorded'}
                        </div>
                      </td>

                      {/* Dates */}
                      <td className="py-3.5 px-4 text-slate-600">
                        <div>Inv: {inv.invoice_date}</div>
                        <div className="text-[11px] text-slate-400">
                          Due: {inv.timeline ? inv.timeline.calculated_due_date : 'Pending'}
                        </div>
                      </td>

                      {/* Terms */}
                      <td className="py-3.5 px-4 text-slate-600">
                        <div>
                          {inv.has_written_agreement
                            ? `${inv.agreed_credit_days || 30} days`
                            : '15d Default (No Agreement)'}
                        </div>
                        {inv.timeline?.statutory_term_capped && (
                          <span className="bg-amber-100 text-amber-800 text-[10px] font-semibold px-1.5 py-0.5 rounded">
                            45d Statutory Cap
                          </span>
                        )}
                      </td>

                      {/* Amounts */}
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-slate-900">
                          ₹{inv.total_amount.toLocaleString('en-IN')}
                        </div>
                        <div className="text-[11px] flex items-center space-x-1">
                          <span className="text-slate-400">Bal:</span>
                          <span className={inv.outstanding_balance > 0 ? (isOverdue ? 'font-bold text-red-600' : 'font-semibold text-slate-800') : 'text-emerald-600 font-semibold'}>
                            ₹{inv.outstanding_balance.toLocaleString('en-IN')}
                          </span>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                            inv.status === 'paid'
                              ? 'bg-emerald-100 text-emerald-800'
                              : inv.status === 'partially_paid'
                              ? 'bg-blue-100 text-blue-800'
                              : isOverdue
                              ? 'bg-red-100 text-red-800'
                              : 'bg-slate-100 text-slate-800'
                          }`}
                        >
                          {inv.status.replace(/_/g, ' ')}
                        </span>
                        {isOverdue && inv.timeline && (
                          <div className="text-[10px] text-red-600 font-medium mt-0.5">
                            {inv.timeline.days_overdue} days past due
                          </div>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right space-x-2">
                        {inv.outstanding_balance > 0 && (
                          <button
                            onClick={() => {
                              setPaymentModalInvoice(inv);
                              setPaymentAmount(inv.outstanding_balance.toString());
                            }}
                            className="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded text-xs font-semibold transition-colors"
                          >
                            Record Payment
                          </button>
                        )}
                        {inv.case && (
                          <Link
                            to={`/cases/${inv.case.id}`}
                            className="bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 px-2.5 py-1 rounded text-xs font-semibold inline-flex items-center space-x-1 transition-colors"
                          >
                            <span>Escalate</span>
                          </Link>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Record Payment Modal */}
      {paymentModalInvoice && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4 animate-scaleUp">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Record Commercial Payment</h3>
                <p className="text-xs text-slate-500">Invoice: #{paymentModalInvoice.invoice_number}</p>
              </div>
              <button
                onClick={() => setPaymentModalInvoice(null)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs space-y-1">
              <div className="flex justify-between text-slate-600">
                <span>Buyer / Debtor:</span>
                <span className="font-semibold text-slate-800">{paymentModalInvoice.buyer_name}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Invoice Total:</span>
                <span>₹{paymentModalInvoice.total_amount.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-slate-900 font-bold border-t border-slate-200 pt-1">
                <span>Current Outstanding Balance:</span>
                <span className="text-blue-700">₹{paymentModalInvoice.outstanding_balance.toLocaleString('en-IN')}</span>
              </div>
            </div>

            <form onSubmit={handleRecordPayment} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">
                  Payment Amount Received (₹) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm font-bold text-slate-900 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
                <div className="flex justify-between mt-1 text-[11px] text-slate-500">
                  <span>Enter partial or full sum</span>
                  <button
                    type="button"
                    onClick={() => setPaymentAmount(paymentModalInvoice.outstanding_balance.toString())}
                    className="text-blue-600 hover:underline font-semibold"
                  >
                    Full Balance (₹{paymentModalInvoice.outstanding_balance.toLocaleString('en-IN')})
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Payment Date *</label>
                <input
                  type="date"
                  required
                  value={paymentDate}
                  onChange={(e) => setPaymentDate(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Bank UTR / Cheque Ref #</label>
                <input
                  type="text"
                  placeholder="e.g. UTR-HDFC-9923812 or Cheque 00213"
                  value={paymentRef}
                  onChange={(e) => setPaymentRef(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Mode of Payment</label>
                <select
                  value={paymentMode}
                  onChange={(e) => setPaymentMode(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="Bank Transfer (NEFT/RTGS)">Bank Transfer (NEFT/RTGS)</option>
                  <option value="IMPS / UPI">IMPS / UPI</option>
                  <option value="Account Payee Cheque">Account Payee Cheque</option>
                  <option value="Demand Draft">Demand Draft</option>
                </select>
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setPaymentModalInvoice(null)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={recordingPayment}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg shadow-sm transition-colors flex items-center space-x-1"
                >
                  {recordingPayment && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Confirm & Reconcile</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Invoice Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 space-y-4 max-h-[90vh] overflow-y-auto animate-scaleUp">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Record New Tax Invoice</h3>
                <p className="text-xs text-slate-500">Auto-initializes pre-litigation case tracker and checklist</p>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateInvoice} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Invoice Number *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. INV-2026-1100"
                    value={newInvoiceData.invoice_number}
                    onChange={(e) => setNewInvoiceData({ ...newInvoiceData, invoice_number: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Invoice Amount (₹) *</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    placeholder="e.g. 250000"
                    value={newInvoiceData.total_amount}
                    onChange={(e) => setNewInvoiceData({ ...newInvoiceData, total_amount: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-bold text-slate-900 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Buyer / Company Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Skyline Logistics India Pvt Ltd"
                  value={newInvoiceData.buyer_name}
                  onChange={(e) => setNewInvoiceData({ ...newInvoiceData, buyer_name: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Buyer GSTIN</label>
                  <input
                    type="text"
                    placeholder="07AAACM9981E1Z8"
                    value={newInvoiceData.buyer_gstin}
                    onChange={(e) => setNewInvoiceData({ ...newInvoiceData, buyer_gstin: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Buyer Contact Email</label>
                  <input
                    type="email"
                    placeholder="accounts@buyer.com"
                    value={newInvoiceData.buyer_contact_email}
                    onChange={(e) => setNewInvoiceData({ ...newInvoiceData, buyer_contact_email: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Invoice Date *</label>
                  <input
                    type="date"
                    required
                    value={newInvoiceData.invoice_date}
                    onChange={(e) => setNewInvoiceData({ ...newInvoiceData, invoice_date: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Delivery / LR Date</label>
                  <input
                    type="date"
                    value={newInvoiceData.delivery_date}
                    onChange={(e) => setNewInvoiceData({ ...newInvoiceData, delivery_date: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div>
                  <label className="flex items-center space-x-2 text-slate-700 font-semibold cursor-pointer">
                    <input
                      type="checkbox"
                      checked={newInvoiceData.has_written_agreement}
                      onChange={(e) => setNewInvoiceData({ ...newInvoiceData, has_written_agreement: e.target.checked })}
                      className="rounded text-blue-600 focus:ring-blue-500"
                    />
                    <span>Written Agreement Exists</span>
                  </label>
                  <p className="text-[10px] text-slate-400 mt-1">If unchecked, Section 15 defaults to 15 days.</p>
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Agreed Credit Days</label>
                  <input
                    type="number"
                    min="1"
                    max="180"
                    disabled={!newInvoiceData.has_written_agreement}
                    value={newInvoiceData.agreed_credit_days}
                    onChange={(e) => setNewInvoiceData({ ...newInvoiceData, agreed_credit_days: Number(e.target.value) })}
                    className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none disabled:bg-slate-200"
                  />
                  <p className="text-[10px] text-amber-700 mt-1">Section 15 strictly caps terms at 45 days.</p>
                </div>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Goods / Services Description</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Supply of 500 sets corporate formal shirts with company branding"
                  value={newInvoiceData.goods_services_description}
                  onChange={(e) => setNewInvoiceData({ ...newInvoiceData, goods_services_description: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg shadow-sm transition-colors flex items-center space-x-1"
                >
                  {creating && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Record Invoice</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
