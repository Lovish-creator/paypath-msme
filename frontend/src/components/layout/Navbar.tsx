import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, RotateCcw, Building2, CheckCircle2, User, LogOut, LogIn } from 'lucide-react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { AuthModal } from '../auth/AuthModal';

interface NavbarProps {
  onDataReset?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onDataReset }) => {
  const { user, logout } = useAuth();
  const [resetting, setResetting] = useState(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  const handleReset = async () => {
    if (!window.confirm("Reset demo data to canonical SLIET PitchVerse 2026 baseline?")) {
      return;
    }
    try {
      setResetting(true);
      const res = await api.resetDemoData();
      setResetMessage(res.message);
      if (onDataReset) onDataReset();
      setTimeout(() => setResetMessage(null), 4000);
    } catch (err: any) {
      alert("Failed to reset demo data: " + err.message);
    } finally {
      setResetting(false);
    }
  };

  const businessName = user?.business_profile?.name || "Apex Uniforms & Apparel";
  const enterpriseType = (user?.business_profile?.enterprise_type || "micro").toUpperCase();

  return (
    <>
      <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center space-x-3">
            <Link to="/" className="flex items-center space-x-2.5 group">
              <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm font-bold text-xl group-hover:bg-blue-500 transition-colors">
                P
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-lg tracking-tight text-white">PayPath MSME</span>
                  <span className="bg-blue-500/20 text-blue-300 text-[10px] font-semibold px-2 py-0.5 rounded-full border border-blue-400/30">
                    SLIET PITCHVERSE 2026
                  </span>
                </div>
                <p className="text-xs text-slate-400 hidden sm:block">
                  Delayed Payment Escalation, Traceable Legal Engine & B2B Discovery
                </p>
              </div>
            </Link>
          </div>

          {/* Status & Actions */}
          <div className="flex items-center space-x-3">
            {/* Active Enterprise Banner */}
            <button
              onClick={() => setShowAuthModal(true)}
              title="Click to switch workspace or register a new business"
              className="flex items-center space-x-2 bg-slate-800/90 hover:bg-slate-700/80 border border-slate-700/60 rounded-md px-3 py-1.5 text-xs text-slate-200 transition-colors cursor-pointer"
            >
              <Building2 className="w-4 h-4 text-emerald-400" />
              <span className="font-semibold">{businessName}</span>
              <span className="bg-emerald-500/20 text-emerald-300 text-[10px] px-1.5 py-0.5 rounded font-mono font-medium">
                {enterpriseType} MSME
              </span>
            </button>

            {/* User Session Action */}
            {user ? (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="hidden md:flex items-center space-x-1 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors"
                  title="Switch MSME account"
                >
                  <User className="w-3.5 h-3.5 text-blue-400" />
                  <span className="truncate max-w-[120px]">{user.email}</span>
                </button>
                <button
                  onClick={logout}
                  title="Sign out of current workspace"
                  className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-md transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-md text-xs font-bold transition-all shadow-sm"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In / Switch</span>
              </button>
            )}

            {/* Reset Demo Data Button */}
            <button
              onClick={handleReset}
              disabled={resetting}
              title="Reset dataset to canonical pitch scenario"
              className="hidden lg:flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 hover:text-white px-2.5 py-1.5 rounded-md text-xs font-medium transition-all shadow-sm"
            >
              <RotateCcw className={`w-3.5 h-3.5 text-blue-400 ${resetting ? 'animate-spin' : ''}`} />
              <span>{resetting ? 'Resetting...' : 'Reset Demo'}</span>
            </button>

            {/* Health indicator */}
            <div className="hidden sm:flex items-center space-x-1.5 text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2.5 py-1 rounded-md">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="font-medium">Online</span>
            </div>
          </div>
        </div>

        {resetMessage && (
          <div className="bg-emerald-600 text-white text-xs py-1.5 px-4 text-center flex items-center justify-center space-x-2 animate-fadeIn">
            <CheckCircle2 className="w-4 h-4" />
            <span>{resetMessage}</span>
          </div>
        )}
      </header>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={() => {
          if (onDataReset) onDataReset();
        }}
      />
    </>
  );
};
