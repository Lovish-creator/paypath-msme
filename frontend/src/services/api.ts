import {
  Invoice,
  Payment,
  CaseDetail,
  ReminderDraft,
  DashboardData,
  SupplierListing,
  SupplierEnquiry,
  BusinessProfile,
  User,
  TokenResponse,
  DocumentExtractionResult,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';
const TOKEN_KEY = 'paypath_token';

export const tokenStorage = {
  get: (): string | null => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const token = tokenStorage.get();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Optional auto-clear if unauthorized
      tokenStorage.clear();
    }
    let errorDetail = 'Request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      errorDetail = response.statusText || errorDetail;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Dashboard
  getDashboard: () => request<DashboardData>('/dashboard'),

  // Invoices
  getInvoices: (params?: { search?: string; status?: string; overdue_only?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.search) q.set('search', params.search);
    if (params?.status) q.set('status', params.status);
    if (params?.overdue_only) q.set('overdue_only', 'true');
    const queryStr = q.toString() ? `?${q.toString()}` : '';
    return request<Invoice[]>(`/invoices${queryStr}`);
  },

  getInvoice: (id: number) => request<Invoice>(`/invoices/${id}`),

  createInvoice: (data: Partial<Invoice>) =>
    request<Invoice>('/invoices', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateInvoice: (id: number, data: Partial<Invoice>) =>
    request<Invoice>(`/invoices/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  recordPayment: (invoiceId: number, data: { amount: number; payment_date: string; reference_number?: string; payment_mode?: string; notes?: string }) =>
    request<Payment>(`/invoices/${invoiceId}/payments`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Cases & Escalation
  getCase: (id: number) => request<CaseDetail>(`/cases/${id}`),
  getCaseByInvoice: (invoiceId: number) => request<CaseDetail>(`/cases/by-invoice/${invoiceId}`),

  updateCaseStage: (caseId: number, stage: number, notes?: string, promisedDate?: string, promisedAmount?: number) =>
    request<CaseDetail>(`/cases/${caseId}/stage`, {
      method: 'PUT',
      body: JSON.stringify({
        current_stage: stage,
        notes,
        promised_payment_date: promisedDate || null,
        promised_payment_amount: promisedAmount || null,
      }),
    }),

  updateEvidenceItem: (caseId: number, itemId: number, data: { status: string; notes?: string; file_name?: string }) =>
    request<any>(`/cases/${caseId}/evidence/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  addFollowUpEvent: (caseId: number, data: { event_type: string; summary: string; detail?: string; next_action_date?: string; recorded_by?: string }) =>
    request<any>(`/cases/${caseId}/events`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  generateReminderDraft: (caseId: number, tone: 'friendly' | 'firm' | 'formal_notice', customMessage?: string) =>
    request<ReminderDraft>(`/cases/${caseId}/reminders`, {
      method: 'POST',
      body: JSON.stringify({ tone, custom_message: customMessage }),
    }),

  downloadReportPdfUrl: (caseId: number) => `${API_BASE}/cases/${caseId}/report/pdf`,

  // Suppliers & Contextual Matching
  getSuppliers: (category?: string, search?: string) => {
    const q = new URLSearchParams();
    if (category) q.set('category', category);
    if (search) q.set('search', search);
    const queryStr = q.toString() ? `?${q.toString()}` : '';
    return request<SupplierListing[]>(`/suppliers${queryStr}`);
  },

  getSupplier: (id: number) => request<SupplierListing>(`/suppliers/${id}`),

  submitSupplierEnquiry: (supplierId: number, data: Omit<SupplierEnquiry, 'id' | 'created_at' | 'consent_timestamp'>) =>
    request<SupplierEnquiry>(`/suppliers/${supplierId}/enquiries`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getAdvertiserLeads: (supplierId: number) => request<SupplierEnquiry[]>(`/suppliers/${supplierId}/advertiser-leads`),

  // Business Profile
  getCurrentProfile: () => request<BusinessProfile>('/suppliers/profile/current'),
  updateProfile: (data: Partial<BusinessProfile>) =>
    request<BusinessProfile>('/suppliers/profile/current', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Authentication & Workspaces
  login: async (data: { email: string; password: string }) => {
    const res = await request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    tokenStorage.set(res.access_token);
    return res;
  },

  register: async (data: {
    email: string;
    password: string;
    business_name: string;
    enterprise_type?: string;
    udyam_number?: string;
    state?: string;
    district?: string;
    industry_category?: string;
    contact_phone?: string;
  }) => {
    const res = await request<TokenResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    tokenStorage.set(res.access_token);
    return res;
  },

  getMe: () => request<User>('/auth/me'),

  logout: () => {
    tokenStorage.clear();
  },

  // Document Extraction
  extractInvoiceDocument: async (file: File): Promise<DocumentExtractionResult> => {
    const formData = new FormData();
    formData.append('file', file);

    const token = tokenStorage.get();
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}/invoices/extract-document`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      let err = 'Document extraction failed';
      try {
        const json = await response.json();
        err = json.detail || json.message || err;
      } catch {
        err = response.statusText || err;
      }
      throw new Error(err);
    }

    return response.json();
  },

  // Demo Controls
  resetDemoData: () => request<{ status: string; message: string; invoices_seeded: number; cases_seeded: number }>('/demo/reset', { method: 'POST' }),
  getDemoStatus: () => request<{ is_demo_mode: boolean; total_invoices: number; total_cases: number; active_company: string }>('/demo/status'),
};
