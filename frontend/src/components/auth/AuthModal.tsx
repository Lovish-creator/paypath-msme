import React, { useState } from 'react';
import { X, Lock, Mail, Building2, ShieldCheck, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const { login, register, loginDemo } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Login form
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form
  const [regData, setRegData] = useState({
    email: '',
    password: '',
    business_name: '',
    enterprise_type: 'micro',
    udyam_number: '',
    state: 'Punjab',
    district: 'Sangrur',
    industry_category: 'manufacturing',
    contact_phone: '',
  });

  if (!isOpen) return null;

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      setLoading(true);
      await login(loginEmail, loginPassword);
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setError(null);
    try {
      setLoading(true);
      await loginDemo();
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!regData.email || !regData.password || !regData.business_name) {
      setError('Please provide Email, Password, and Enterprise Name');
      return;
    }
    try {
      setLoading(true);
      await register(regData);
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/70 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden animate-scaleUp">
        {/* Header */}
        <div className="bg-slate-900 text-white p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex items-center space-x-2 text-blue-400 mb-1 text-xs font-semibold uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4" />
            <span>Secure MSME Workspace Access</span>
          </div>
          <h2 className="text-xl font-bold">
            {mode === 'login' ? 'Sign In to PayPath' : 'Create MSME Workspace'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {mode === 'login'
              ? 'Access your statutory receivables ledger & escalation workflows.'
              : 'Register your micro/small enterprise for legally grounded dues recovery.'}
          </p>

          {/* Mode Switch Tabs */}
          <div className="flex bg-slate-800 rounded-lg p-1 mt-4 text-xs">
            <button
              onClick={() => { setMode('login'); setError(null); }}
              className={`flex-1 py-1.5 rounded-md font-semibold transition-all ${
                mode === 'login' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setMode('register'); setError(null); }}
              className={`flex-1 py-1.5 rounded-md font-semibold transition-all ${
                mode === 'register' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              New Registration
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {mode === 'login' ? (
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="email"
                    required
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="user@enterprise.in"
                    className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-lg text-xs font-bold transition-colors shadow-sm disabled:opacity-50"
              >
                {loading ? 'Authenticating...' : 'Sign In to Workspace'}
              </button>

              <div className="relative my-4">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200"></div>
                </div>
                <div className="relative flex justify-center text-[11px] uppercase">
                  <span className="bg-white px-2 text-slate-400 font-semibold">Or for Demo Workspace</span>
                </div>
              </div>

              {/* Demo Account Button */}
              <button
                type="button"
                onClick={handleDemoLogin}
                disabled={loading}
                className="w-full bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 text-emerald-800 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-2"
              >
                <Building2 className="w-4 h-4 text-emerald-600" />
                <span>1-Click Sign In: Apex Uniforms (Sample Account)</span>
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegisterSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-0.5">Enterprise Name *</label>
                <input
                  type="text"
                  required
                  value={regData.business_name}
                  onChange={(e) => setRegData({ ...regData, business_name: e.target.value })}
                  placeholder="e.g. Kaveri Tooling & Moulds"
                  className="w-full px-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-0.5">Category *</label>
                  <select
                    value={regData.enterprise_type}
                    onChange={(e) => setRegData({ ...regData, enterprise_type: e.target.value })}
                    className="w-full px-2 py-1.5 text-xs border border-slate-300 rounded-lg bg-white"
                  >
                    <option value="micro">Micro (&lt; ₹1 Cr / ₹5 Cr)</option>
                    <option value="small">Small (&lt; ₹10 Cr / ₹50 Cr)</option>
                    <option value="medium">Medium (&lt; ₹50 Cr / ₹250 Cr)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-0.5">Udyam Registration</label>
                  <input
                    type="text"
                    value={regData.udyam_number}
                    onChange={(e) => setRegData({ ...regData, udyam_number: e.target.value })}
                    placeholder="UDYAM-XX-00-0000000"
                    className="w-full px-2 py-1.5 text-xs border border-slate-300 rounded-lg font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-0.5">State</label>
                  <input
                    type="text"
                    value={regData.state}
                    onChange={(e) => setRegData({ ...regData, state: e.target.value })}
                    className="w-full px-2 py-1.5 text-xs border border-slate-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-0.5">District</label>
                  <input
                    type="text"
                    value={regData.district}
                    onChange={(e) => setRegData({ ...regData, district: e.target.value })}
                    className="w-full px-2 py-1.5 text-xs border border-slate-300 rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-0.5">Email Address *</label>
                <input
                  type="email"
                  required
                  value={regData.email}
                  onChange={(e) => setRegData({ ...regData, email: e.target.value })}
                  placeholder="accounts@kaveritools.in"
                  className="w-full px-3 py-1.5 text-xs border border-slate-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-0.5">Password *</label>
                <input
                  type="password"
                  required
                  value={regData.password}
                  onChange={(e) => setRegData({ ...regData, password: e.target.value })}
                  placeholder="At least 6 characters"
                  className="w-full px-3 py-1.5 text-xs border border-slate-300 rounded-lg"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-xs font-bold transition-colors shadow-sm disabled:opacity-50 mt-2"
              >
                {loading ? 'Creating Workspace...' : 'Register Isolated Workspace'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
