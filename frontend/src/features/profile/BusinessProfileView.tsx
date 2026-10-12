import React, { useEffect, useState } from 'react';
import {
  Building2,
  ShieldCheck,
  Save,
  CheckCircle,
  AlertCircle,
  Loader2,
  Tag,
  Scale,
} from 'lucide-react';
import { api } from '../../services/api';
import { BusinessProfile } from '../../types';

export const BusinessProfileView: React.FC = () => {
  const [profile, setProfile] = useState<BusinessProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await api.getCurrentProfile();
      setProfile(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    try {
      setSaving(true);
      const updated = await api.updateProfile(profile);
      setProfile(updated);
      setSuccessMessage('Business Profile successfully updated! Legal engine and supplier recommendations adjusted.');
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: any) {
      alert('Failed to update profile: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !profile) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <p className="text-sm text-slate-500 font-medium">Loading enterprise profile...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">
          Enterprise Profile & Statutory Registration
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Configures MSMED Act statutory classification and signals for contextual B2B discovery
        </p>
      </div>

      {successMessage && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs p-3.5 rounded-xl flex items-center space-x-2 animate-fadeIn">
          <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
        {/* Enterprise Classification */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-2">
            <Building2 className="w-4 h-4 text-blue-600" />
            <span>1. Commercial Enterprise Identification</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-700 font-semibold mb-1">Company Legal Name *</label>
              <input
                type="text"
                required
                value={profile.name}
                onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-semibold text-slate-900 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Enterprise Classification (MSMED Act) *</label>
              <select
                value={profile.enterprise_type}
                onChange={(e) => setProfile({ ...profile, enterprise_type: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-semibold text-slate-900 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="micro">Micro Enterprise (&lt; ₹1 Cr Investment / &lt; ₹5 Cr Turnover)</option>
                <option value="small">Small Enterprise (&lt; ₹10 Cr Investment / &lt; ₹50 Cr Turnover)</option>
                <option value="medium">Medium Enterprise (&lt; ₹50 Cr Investment / &lt; ₹250 Cr Turnover)</option>
              </select>
              <p className="text-[10px] text-slate-400 mt-1">
                Micro & Small enterprises qualify for Section 43B(h) income tax disallowance protections.
              </p>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Udyam Registration Number *</label>
              <input
                type="text"
                required
                placeholder="UDYAM-PB-12-0048291"
                value={profile.udyam_number}
                onChange={(e) => setProfile({ ...profile, udyam_number: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono font-bold text-slate-900 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <p className="text-[10px] text-emerald-700 font-semibold mt-1">
                Verified registration required for MSEFC Facilitation Council claims.
              </p>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">GSTIN</label>
              <input
                type="text"
                placeholder="03AABCA1234F1Z5"
                value={profile.gstin || ''}
                onChange={(e) => setProfile({ ...profile, gstin: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Location & Contacts */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-2">
            <Scale className="w-4 h-4 text-emerald-600" />
            <span>2. Location & Primary Contact</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-700 font-semibold mb-1">State *</label>
              <input
                type="text"
                required
                value={profile.state}
                onChange={(e) => setProfile({ ...profile, state: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">District *</label>
              <input
                type="text"
                required
                value={profile.district}
                onChange={(e) => setProfile({ ...profile, district: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Official Email Address *</label>
              <input
                type="email"
                required
                value={profile.contact_email}
                onChange={(e) => setProfile({ ...profile, contact_email: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Official Phone *</label>
              <input
                type="text"
                required
                value={profile.contact_phone}
                onChange={(e) => setProfile({ ...profile, contact_phone: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Contextual Matching Attributes */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-2">
            <Tag className="w-4 h-4 text-purple-600" />
            <span>3. Contextual B2B Supplier Matching Signals</span>
          </h2>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-700 font-semibold mb-1">Manufacturing Industry Category</label>
              <select
                value={profile.industry_category}
                onChange={(e) => setProfile({ ...profile, industry_category: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="garment_manufacturing">Garment & Textile Manufacturing</option>
                <option value="packaging">Packaging & Paperboard Products</option>
                <option value="industrial_components">Precision Components & Machinery</option>
                <option value="business_services">Business & Professional Services</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">
                Voluntary Material & Purchasing Interests (Comma-separated)
              </label>
              <input
                type="text"
                placeholder="thread,fabric,buttons,zippers,packaging,machinery"
                value={profile.purchasing_interests}
                onChange={(e) => setProfile({ ...profile, purchasing_interests: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <p className="text-[10px] text-slate-400 mt-1">
                Used strictly to rank and surface relevant sponsored B2B listings. Never linked to invoice amounts or buyer debts.
              </p>
            </div>
          </div>
        </div>

        {/* Save Action */}
        <div className="pt-3 border-t border-slate-100 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg shadow-sm transition-colors flex items-center space-x-1.5 text-xs"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            <span>Save Profile Changes</span>
          </button>
        </div>
      </form>
    </div>
  );
};
