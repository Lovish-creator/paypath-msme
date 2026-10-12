import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Receipt,
  AlertTriangle,
  ShoppingBag,
  Building,
  Scale,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Executive Dashboard', icon: LayoutDashboard },
    { to: '/invoices', label: 'Invoices & Receivables', icon: Receipt },
    { to: '/cases/1', label: 'Escalation Case Detail', icon: AlertTriangle, badge: 'Live Demo' },
    { to: '/suppliers', label: 'B2B Supplier Discovery', icon: ShoppingBag, badge: 'Sponsored' },
    { to: '/profile', label: 'Enterprise Profile', icon: Building },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-6">
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Core Modules
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 shadow-sm border border-blue-100 font-semibold'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`
                  }
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded-full font-semibold uppercase tracking-wider ${
                        item.badge === 'Live Demo'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Legal Authority Reference Card */}
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-xs space-y-2">
          <div className="flex items-center space-x-1.5 text-slate-800 font-semibold">
            <Scale className="w-4 h-4 text-blue-600" />
            <span>Statutory Foundations</span>
          </div>
          <p className="text-slate-500 text-[11px] leading-relaxed">
            Deterministic calculations grounded in Sections 15–18 of the MSMED Act, 2006 & Section 43B(h) Income Tax Act.
          </p>
          <div className="pt-1 border-t border-slate-200 text-[11px] text-slate-600 space-y-1">
            <div className="flex justify-between">
              <span>Section 15 Max Cap:</span>
              <span className="font-semibold text-slate-800">45 Days</span>
            </div>
            <div className="flex justify-between">
              <span>Section 16 Rate:</span>
              <span className="font-semibold text-slate-800">3x RBI Rate (20.25%)</span>
            </div>
          </div>
        </div>

        {/* Official Links */}
        <div className="space-y-1.5 px-3 text-[11px] text-slate-500">
          <p className="font-medium text-slate-400 uppercase text-[10px] tracking-wider mb-1">
            Official Portals (External)
          </p>
          <a
            href="https://samadhaan.msme.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between text-slate-600 hover:text-blue-600 transition-colors"
          >
            <span>MSME Samadhaan</span>
            <ExternalLink className="w-3 h-3 text-slate-400" />
          </a>
          <a
            href="https://udyamregistration.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between text-slate-600 hover:text-blue-600 transition-colors"
          >
            <span>Udyam Registration</span>
            <ExternalLink className="w-3 h-3 text-slate-400" />
          </a>
        </div>
      </div>

      {/* Footer Pitch Note */}
      <div className="p-4 border-t border-slate-200 bg-slate-50/60 text-center">
        <p className="text-[11px] font-medium text-slate-500">
          PayPath MSME Prototype
        </p>
        <p className="text-[10px] text-slate-400 mt-0.5">
          Judge-Ready • Tier 1 Architecture
        </p>
      </div>
    </aside>
  );
};
