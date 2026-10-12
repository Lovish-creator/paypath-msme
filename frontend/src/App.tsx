import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { DashboardView } from './features/dashboard/DashboardView';
import { InvoicesView } from './features/invoices/InvoicesView';
import { CaseDetailView } from './features/cases/CaseDetailView';
import { SupplierDiscoveryView } from './features/suppliers/SupplierDiscoveryView';
import { BusinessProfileView } from './features/profile/BusinessProfileView';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
        <Navbar onDataReset={() => window.location.reload()} />
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full">
            <Routes>
              <Route path="/" element={<DashboardView />} />
              <Route path="/invoices" element={<InvoicesView />} />
              <Route path="/cases" element={<Navigate to="/cases/1" replace />} />
              <Route path="/cases/:id" element={<CaseDetailView />} />
              <Route path="/suppliers" element={<SupplierDiscoveryView />} />
              <Route path="/profile" element={<BusinessProfileView />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
