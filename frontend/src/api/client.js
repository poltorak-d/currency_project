const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function handleResponse(res) {
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || res.statusText || 'Błąd sieci');
  }
  return res.json();
}

export async function fetchCurrencies() {
  const res = await fetch(`${API_BASE}/currencies`);
  const data = await handleResponse(res);
  return data.currencies;
}

export async function fetchRate(currency, date) {
  const params = new URLSearchParams({ date });
  const res = await fetch(`${API_BASE}/rates/${currency}?${params}`);
  return handleResponse(res);
}

export async function fetchRatesRange(currency, startDate, endDate) {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  });
  const res = await fetch(`${API_BASE}/rates/${currency}/range?${params}`);
  return handleResponse(res);
}
