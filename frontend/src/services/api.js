const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function fetchJson(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'API request failed');
  }

  return response.json();
}

export const api = {
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
