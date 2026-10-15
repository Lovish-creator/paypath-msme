import React, { useEffect, useState } from 'react';
import {
  ShoppingBag,
  Sparkles,
  ShieldCheck,
  CheckCircle,
  Building,
  Mail,
  Phone,
  MapPin,
  ExternalLink,
  Lock,
  Eye,
  Send,
  Loader2,
  X,
  Search,
  Tag,
} from 'lucide-react';
import { api } from '../../services/api';
import { SupplierListing, SupplierEnquiry, BusinessProfile } from '../../types';

export const SupplierDiscoveryView: React.FC = () => {
  const [suppliers, setSuppliers] = useState<SupplierListing[]>([]);
  const [profile, setProfile] = useState<BusinessProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  // Mode: 'directory' or 'my_enquiries'
  const [viewMode, setViewMode] = useState<'directory' | 'my_enquiries'>('directory');
  const [myEnquiries, setMyEnquiries] = useState<SupplierEnquiry[]>([]);
  const [loadingEnquiries, setLoadingEnquiries] = useState(false);

  // Enquiry Modal
  const [enquiryModalSupplier, setEnquiryModalSupplier] = useState<SupplierListing | null>(null);
  const [enquiryCompanyName, setEnquiryCompanyName] = useState('');
  const [enquiryName, setEnquiryName] = useState('');
  const [enquiryEmail, setEnquiryEmail] = useState('');
  const [enquiryPhone, setEnquiryPhone] = useState('');
  const [enquiryProductInterest, setEnquiryProductInterest] = useState('');
  const [enquiryMessage, setEnquiryMessage] = useState('');
  const [consentGiven, setConsentGiven] = useState(false);
  const [submittingEnquiry, setSubmittingEnquiry] = useState(false);
  const [enquirySuccessMessage, setEnquirySuccessMessage] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [supList, prof] = await Promise.all([
        api.getSuppliers(selectedCategory || undefined, searchQuery || undefined),
        api.getCurrentProfile(),
      ]);
      setSuppliers(supList);
      setProfile(prof);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedCategory]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchData();
  };

  const handleOpenEnquiryModal = (supplier: SupplierListing) => {
    setEnquiryModalSupplier(supplier);
    setEnquiryCompanyName(profile?.name || 'Apex Uniforms & Apparel');
    setEnquiryName('Finance & Procurement Lead');
    setEnquiryEmail(profile?.contact_email || 'procurement@apexuniforms.in');
    setEnquiryPhone(profile?.contact_phone || '+91 98765 43210');
    setEnquiryProductInterest(supplier.product_tags.split(',')[0].trim());
    setEnquiryMessage(`Hello, we are requesting catalog pricing and minimum delivery timelines for ${supplier.product_tags.split(',')[0].trim()}.`);
    setConsentGiven(false);
  };

  const handleSubmitEnquiry = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!enquiryModalSupplier) return;
    if (!consentGiven) {
      alert('You must provide explicit consent to transmit your commercial contact details.');
      return;
    }
    try {
      setSubmittingEnquiry(true);
      await api.submitSupplierEnquiry(enquiryModalSupplier.id, {
        supplier_id: enquiryModalSupplier.id,
        requester_company_name: enquiryCompanyName,
        requester_name: enquiryName,
        requester_email: enquiryEmail,
        requester_phone: enquiryPhone,
        product_interest: enquiryProductInterest,
        message: enquiryMessage,
        consent_given: true,
      });
      setEnquirySuccessMessage(`Enquiry submitted to ${enquiryModalSupplier.company_name}! Lead recorded with explicit consent.`);
      setEnquiryModalSupplier(null);
      setTimeout(() => setEnquirySuccessMessage(null), 5000);
      if (viewMode === 'my_enquiries') {
        loadMyEnquiries();
      }
    } catch (err: any) {
      alert('Failed to submit enquiry: ' + err.message);
    } finally {
      setSubmittingEnquiry(false);
    }
  };

  const loadMyEnquiries = async () => {
    try {
      setLoadingEnquiries(true);
      const data = await api.getEnquiryHistory();
      setMyEnquiries(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingEnquiries(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 rounded-2xl p-6 text-white shadow-md border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="bg-emerald-500/20 text-emerald-300 text-xs font-bold px-2.5 py-0.5 rounded-full border border-emerald-400/30 flex items-center space-x-1">
                <Sparkles className="w-3 h-3 text-emerald-400" />
                <span>CONTEXTUAL B2B DISCOVERY</span>
              </span>
              <span className="text-xs text-slate-400">Sustainable Revenue Model</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight mt-1 text-white">
              B2B Sponsored Supplier Discovery
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Match your manufacturing needs with specialized wholesale suppliers based strictly on your industry category and voluntary purchasing interests.
            </p>
          </div>

          {/* Perspective Switcher */}
          <div className="flex items-center bg-slate-800/80 p-1 rounded-lg border border-slate-700/80 self-start md:self-auto text-xs font-medium">
            <button
              onClick={() => setViewMode('directory')}
              className={`px-3 py-1.5 rounded-md transition-all ${
                viewMode === 'directory' ? 'bg-blue-600 text-white shadow-xs font-semibold' : 'text-slate-400 hover:text-white'
              }`}
            >
              Enterprise Buyer Directory
            </button>
            <button
              onClick={() => {
                setViewMode('my_enquiries');
                loadMyEnquiries();
              }}
              className={`px-3 py-1.5 rounded-md transition-all ${
                viewMode === 'my_enquiries' ? 'bg-emerald-600 text-white shadow-xs font-semibold' : 'text-slate-400 hover:text-white'
              }`}
            >
              My Sent Enquiries
            </button>
          </div>
        </div>
      </div>

      {/* Strict Privacy & Safeguard Callout */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-start space-x-3 text-xs">
        <div className="p-2 rounded-lg bg-emerald-50 text-emerald-700 shrink-0 mt-0.5">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div className="space-y-0.5">
          <span className="font-bold text-slate-900">Privacy & Data Safeguard Commitment:</span>
          <p className="text-slate-600 leading-relaxed text-[11px]">
            Targeting is driven solely by your business industry classification (<strong>{profile?.industry_category.replace(/_/g, ' ')}</strong>) and selected material tags (<strong>{profile?.purchasing_interests}</strong>).
            Under no circumstances are unpaid invoice amounts, buyer identities, dispute documents, or debt distress used for ad matching.
          </p>
        </div>
      </div>

      {enquirySuccessMessage && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs p-3 rounded-xl flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{enquirySuccessMessage}</span>
        </div>
      )}

      {/* DIRECTORY VIEW */}
      {viewMode === 'directory' && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
            <form onSubmit={handleSearchSubmit} className="w-full md:w-80 relative">
              <input
                type="text"
                placeholder="Search materials, products, or suppliers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
              />
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            </form>

            <div className="flex items-center space-x-2 overflow-x-auto w-full md:w-auto text-xs">
              <span className="text-slate-400 text-[11px] font-semibold uppercase mr-1">Categories:</span>
              <button
                onClick={() => setSelectedCategory('')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  selectedCategory === '' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                All Contextual
              </button>
              <button
                onClick={() => setSelectedCategory('garment_manufacturing')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  selectedCategory === 'garment_manufacturing' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                Garment Trims & Textiles
              </button>
              <button
                onClick={() => setSelectedCategory('packaging')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  selectedCategory === 'packaging' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                Cartons & Packaging
              </button>
              <button
                onClick={() => setSelectedCategory('industrial_components')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  selectedCategory === 'industrial_components' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                Machinery & Equipment
              </button>
            </div>
          </div>

          {/* Supplier Listings Grid */}
          {loading ? (
            <div className="p-12 text-center flex flex-col items-center justify-center space-y-2">
              <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
              <p className="text-xs text-slate-500 font-medium">Matching contextual B2B listings...</p>
            </div>
          ) : suppliers.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-xs text-slate-500">
              No suppliers found for the selected criteria.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {suppliers.map((sup) => (
                <div
                  key={sup.id}
                  className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-2.5">
                    {/* Badges */}
                    <div className="flex items-center justify-between">
                      {sup.is_sponsored ? (
                        <span className="bg-amber-100 text-amber-900 border border-amber-300 text-[10px] font-extrabold px-2 py-0.5 rounded uppercase tracking-wider flex items-center space-x-1">
                          <Sparkles className="w-3 h-3 text-amber-600" />
                          <span>SPONSORED PLACEMENT</span>
                        </span>
                      ) : (
                        <span className="bg-slate-100 text-slate-700 text-[10px] font-semibold px-2 py-0.5 rounded">
                          STANDARD DIRECTORY
                        </span>
                      )}
                      <span className="text-[11px] font-medium text-slate-400 capitalize">
                        {sup.industry_category.replace(/_/g, ' ')}
                      </span>
                    </div>

                    {/* Company Name */}
                    <div>
                      <h3 className="text-base font-bold text-slate-900">{sup.company_name}</h3>
                      <div className="flex items-center space-x-1 text-slate-500 text-xs mt-0.5">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        <span>{sup.city}, {sup.state}</span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed line-clamp-3">
                      {sup.description}
                    </p>

                    {/* Product Tags */}
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {sup.product_tags.split(',').map((tag, idx) => (
                        <span
                          key={idx}
                          className="bg-blue-50 text-blue-700 text-[10px] font-semibold px-2 py-0.5 rounded-full border border-blue-100"
                        >
                          {tag.trim()}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Footer & Action */}
                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    <div>
                      <span className="text-[10px] text-slate-400 block font-semibold uppercase">Min Order (MOQ)</span>
                      <span className="font-semibold text-slate-800">{sup.min_order_quantity || 'Flexible'}</span>
                    </div>

                    <button
                      onClick={() => handleOpenEnquiryModal(sup)}
                      className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-3 py-1.5 rounded-lg shadow-xs transition-colors flex items-center space-x-1"
                    >
                      <Send className="w-3.5 h-3.5" />
                      <span>Send Enquiry</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* MY SENT ENQUIRIES VIEW */}
      {viewMode === 'my_enquiries' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
          <div className="border-b border-slate-100 pb-4">
            <h2 className="text-base font-bold text-slate-900">
              My Sent B2B Enquiries
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Track commercial quotation requests sent from your business profile to verified supplier partners.
            </p>
          </div>

          {loadingEnquiries ? (
            <div className="p-8 text-center flex flex-col items-center justify-center space-y-2">
              <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
              <p className="text-xs text-slate-500 font-medium">Loading your sent enquiries...</p>
            </div>
          ) : myEnquiries.length === 0 ? (
            <div className="bg-slate-50 rounded-xl p-8 text-center text-xs text-slate-500 space-y-2">
              <p className="font-semibold text-slate-700">No enquiries submitted yet.</p>
              <p className="text-[11px] text-slate-400">
                Switch to the "Enterprise Buyer Directory" tab above, click "Send Enquiry" on any verified supplier partner to request quotations or commercial terms.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden text-xs">
              <div className="bg-slate-50 px-4 py-2.5 font-bold text-slate-600 uppercase text-[10px] grid grid-cols-4">
                <span>Supplier / Product</span>
                <span>Requester Details</span>
                <span>Enquiry Message</span>
                <span className="text-right">Consent & Date</span>
              </div>
              {myEnquiries.map((lead) => {
                const matchedSup = suppliers.find((s) => s.id === lead.supplier_id);
                return (
                  <div key={lead.id} className="p-4 grid grid-cols-4 items-start hover:bg-slate-50/50">
                    <div>
                      <div className="font-bold text-slate-900">
                        {matchedSup ? matchedSup.company_name : `Supplier #${lead.supplier_id}`}
                      </div>
                      <span className="inline-block mt-1 bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded font-semibold text-[10px]">
                        {lead.product_interest}
                      </span>
                    </div>
                    <div>
                      <div className="font-semibold text-slate-800">{lead.requester_name}</div>
                      <div className="text-[11px] text-slate-500">{lead.requester_company_name}</div>
                      <div className="text-[11px] text-blue-600 font-mono mt-0.5">{lead.requester_email}</div>
                    </div>
                    <div className="text-slate-600 pr-4">
                      {lead.message}
                    </div>
                    <div className="text-right space-y-1">
                      <span className="inline-block bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                        Explicit Consent Verified
                      </span>
                      <div className="text-[10px] text-slate-400">
                        {new Date(lead.consent_timestamp).toLocaleString('en-IN')}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Consent-Gated Enquiry Modal */}
      {enquiryModalSupplier && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 space-y-4 max-h-[90vh] overflow-y-auto animate-scaleUp">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-[10px] font-bold text-amber-700 uppercase bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
                  Sponsored Supplier Enquiry
                </span>
                <h3 className="text-sm font-bold text-slate-900 mt-1">
                  Connect with {enquiryModalSupplier.company_name}
                </h3>
              </div>
              <button
                onClick={() => setEnquiryModalSupplier(null)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSubmitEnquiry} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Company Name *</label>
                  <input
                    type="text"
                    required
                    value={enquiryCompanyName}
                    onChange={(e) => setEnquiryCompanyName(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Contact Person *</label>
                  <input
                    type="text"
                    required
                    value={enquiryName}
                    onChange={(e) => setEnquiryName(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Email Address *</label>
                  <input
                    type="email"
                    required
                    value={enquiryEmail}
                    onChange={(e) => setEnquiryEmail(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Phone Number *</label>
                  <input
                    type="text"
                    required
                    value={enquiryPhone}
                    onChange={(e) => setEnquiryPhone(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Product Requirement *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 500 Cones Polyester Thread 40/2 White"
                  value={enquiryProductInterest}
                  onChange={(e) => setEnquiryProductInterest(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Commercial Message / Specs</label>
                <textarea
                  rows={3}
                  value={enquiryMessage}
                  onChange={(e) => setEnquiryMessage(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              {/* Mandatory Consent Checkbox */}
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl space-y-1">
                <label className="flex items-start space-x-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    required
                    checked={consentGiven}
                    onChange={(e) => setConsentGiven(e.target.checked)}
                    className="mt-0.5 rounded text-blue-600 focus:ring-blue-500 w-4 h-4"
                  />
                  <div className="text-[11px] text-blue-900 leading-normal">
                    <span className="font-bold">Explicit Data Sharing Consent:</span> I hereby explicitly authorize PayPath MSME to transmit the commercial contact details above to {enquiryModalSupplier.company_name} solely for the purpose of fulfilling this B2B quotation enquiry.
                  </div>
                </label>
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setEnquiryModalSupplier(null)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingEnquiry || !consentGiven}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg shadow-sm transition-colors flex items-center space-x-1 disabled:bg-slate-400"
                >
                  {submittingEnquiry && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Submit Consented Enquiry</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
