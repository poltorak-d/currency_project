import { useState, useEffect } from 'react';
import { fetchCurrencies, fetchRate } from '../api/client';

function HomePage() {
  const [currencies, setCurrencies] = useState([]);
  const [currency, setCurrency] = useState('USD');
  const [date, setDate] = useState(() => {
    const d = new Date();
    return d.toISOString().slice(0, 10);
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCurrencies()
      .then(setCurrencies)
      .catch(() => setCurrencies(['USD', 'EUR', 'CHF', 'GBP', 'CZK', 'DKK', 'NOK', 'SEK', 'JPY', 'CAD']));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await fetchRate(currency, date);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const maxDate = new Date().toISOString().slice(0, 10);

  return (
    <div className="page">
      <h2>Sprawdź kurs</h2>
      <form onSubmit={handleSubmit} className="rate-form">
        <div className="form-group">
          <label htmlFor="currency">Waluta</label>
          <select
            id="currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            required
          >
            {currencies.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="date">Data</label>
          <input
            id="date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            max={maxDate}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Pobieranie…' : 'Sprawdź kurs'}
        </button>
      </form>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {result && (
        <div className="rate-result card">
          <p className="rate-display">
            1 {result.currency} = <strong>{Number(result.rate).toFixed(4)}</strong> PLN
          </p>
          <p className="rate-date">
            Kurs z dnia {result.date}
          </p>
        </div>
      )}
    </div>
  );
}

export default HomePage;
