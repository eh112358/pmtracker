const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getAuthHeader() {
  const token = localStorage.getItem('pmtracker_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchJson(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
      ...options.headers,
    },
  });

  if (response.status === 401) {
    // Token expired or invalid
    localStorage.removeItem('pmtracker_token');
    window.location.reload();
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'API request failed');
  }

  return response.json();
}

export const api = {
  // Auth endpoints (no auth header needed for these)
  getAuthStatus: () =>
    fetch(`${API_BASE}/api/auth/status`).then((r) => r.json()),

  login: (password) =>
    fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    }).then((r) => {
      if (!r.ok) return r.json().then((e) => Promise.reject(new Error(e.detail)));
      return r.json();
    }),

  setupPassword: (password) =>
    fetch(`${API_BASE}/api/auth/setup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    }).then((r) => {
      if (!r.ok) return r.json().then((e) => Promise.reject(new Error(e.detail)));
      return r.json();
    }),

  // Spot prices
  getPrices: () => fetchJson('/api/portfolio/prices'),

  // Portfolio
  getPortfolioSummary: () => fetchJson('/api/portfolio/summary'),
  getHoldingsWithValues: () => fetchJson('/api/portfolio/holdings'),

  // Holdings CRUD
  getHoldings: () => fetchJson('/api/holdings'),
  getHolding: (id) => fetchJson(`/api/holdings/${id}`),
  createHolding: (data) =>
    fetchJson('/api/holdings', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateHolding: (id, data) =>
    fetchJson(`/api/holdings/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  deleteHolding: (id) =>
    fetchJson(`/api/holdings/${id}`, {
      method: 'DELETE',
    }),

  // Products
  getProducts: (metalId = null) => {
    const url = metalId ? `/api/products?metal_id=${metalId}` : '/api/products';
    return fetchJson(url);
  },

  // Metals
  getMetals: () => fetchJson('/api/metals'),
};
