import { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { fetchCurrencies, fetchRatesRange } from '../api/client';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

function ChartPage() {
  const [currencies, setCurrencies] = useState([]);
  const [currency, setCurrency] = useState('USD');
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setMonth(d.getMonth() - 1);
    return d.toISOString().slice(0, 10);
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [rates, setRates] = useState([]);
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
    setRates([]);
    setLoading(true);
    try {
      const data = await fetchRatesRange(currency, startDate, endDate);
      setRates(data.rates || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const maxDate = new Date().toISOString().slice(0, 10);

  const chartData = {
    labels: rates.map((r) => r.date),
    datasets: [
      {
        label: `${currency} / PLN`,
        data: rates.map((r) => r.rate),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true },
      title: { display: false },
    },
    scales: {
      x: {
        title: { display: true, text: 'Data' },
      },
      y: {
        title: { display: true, text: 'Kurs (PLN)' },
        beginAtZero: false,
      },
    },
  };

  return (
    <div className="page">
      <h2>Wykres kursu</h2>
      <form onSubmit={handleSubmit} className="rate-form">
        <div className="form-group">
          <label htmlFor="chart-currency">Waluta</label>
          <select
            id="chart-currency"
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
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="start-date">Data od</label>
            <input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              max={maxDate}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="end-date">Data do</label>
            <input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              max={maxDate}
              required
            />
          </div>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Pobieranie…' : 'Pokaż wykres'}
        </button>
      </form>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {rates.length > 0 && (
        <div className="chart-container">
          <Line data={chartData} options={chartOptions} />
        </div>
      )}

      {!loading && !error && rates.length === 0 && (
        <p className="hint">Wybierz walutę i zakres dat, następnie kliknij „Pokaż wykres”.</p>
      )}
    </div>
  );
}

export default ChartPage;
