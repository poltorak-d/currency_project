import { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Filler, Title, Tooltip } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { fetchCurrencies, fetchRate, fetchRatesRange } from '../api/client';
import { getCurrencyLabel } from '../currencyLabels';
import { useTheme } from '../ThemeContext';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Title, Tooltip);

function formatDateDisplay(d) {
  return new Date(d + 'T12:00:00').toLocaleDateString('pl-PL', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

function formatDateShort(d) {
  return new Date(d + 'T12:00:00').toLocaleDateString('pl-PL', {
    day: 'numeric',
    month: 'short',
  });
}

function HistoricalChartTab({ currencies, currency, setCurrency }) {
  const { isDark } = useTheme();
  const today = new Date().toISOString().slice(0, 10);
  const monthAgo = new Date();
  monthAgo.setMonth(monthAgo.getMonth() - 1);
  const defaultStart = monthAgo.toISOString().slice(0, 10);

  const [startDate, setStartDate] = useState(defaultStart);
  const [endDate, setEndDate] = useState(today);
  const [rates, setRates] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetched, setFetched] = useState(false);

  const loadChart = async () => {
    setError(null);
    setRates([]);
    setLoading(true);
    setFetched(true);
    try {
      const data = await fetchRatesRange(currency, startDate, endDate);
      setRates(data.rates || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const dateRangeDisplay = `${formatDateDisplay(startDate)} - ${formatDateDisplay(endDate)}`;
  const firstRate = rates[0]?.rate;
  const lastRate = rates[rates.length - 1]?.rate;
  const change = firstRate != null && lastRate != null ? Number(lastRate) - Number(firstRate) : null;
  const changePct = change != null && firstRate ? ((change / Number(firstRate)) * 100).toFixed(2) : null;

  const chartLineColor = isDark ? '#94a3b8' : '#64748b';
  const chartFillColor = isDark ? 'rgba(148, 163, 184, 0.2)' : 'rgba(100, 116, 139, 0.25)';
  const chartTickColor = isDark ? '#64748b' : '#94a3b8';
  const chartGridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';

  const chartData = {
    labels: rates.map((r) => formatDateShort(r.date)),
    datasets: [
      {
        label: `${currency} / PLN`,
        data: rates.map((r) => Number(r.rate)),
        borderColor: chartLineColor,
        backgroundColor: chartFillColor,
        fill: true,
        tension: 0.25,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => `${Number(ctx.parsed.y).toFixed(4)} PLN`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 13 }, color: chartTickColor },
      },
      y: {
        beginAtZero: false,
        grid: { color: chartGridColor },
        ticks: { font: { size: 13 }, color: chartTickColor },
      },
    },
  };

  return (
    <>
      <div className="card">
        <div className="card-title">Wybierz walutę i zakres dat</div>
        <div className="form-row">
          <div>
            <label className="form-label">Waluta do porównania</label>
            <div className="select-wrap">
              <select value={currency} onChange={(e) => setCurrency(e.target.value)}>
                {currencies.map((c) => (
                  <option key={c} value={c}>
                    {getCurrencyLabel(c)}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="form-label">Zakres dat</label>
            <div className="form-row" style={{ gap: '12px', gridTemplateColumns: '1fr 1fr' }}>
              <div className="date-wrap">
                <span className="date-icon">📅</span>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  max={endDate}
                />
              </div>
              <div className="date-wrap">
                <span className="date-icon">📅</span>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate}
                  max={today}
                />
              </div>
            </div>
          </div>
        </div>
        <div className="form-note">Wszystkie kursy w relacji do złotówki (PLN)</div>
        <button
          type="button"
          onClick={loadChart}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Ładowanie…' : 'Pokaż wykres'}
        </button>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {rates.length > 0 && (
        <div className="card">
          <div className="chart-label">Kurs {currency} / PLN</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginBottom: '16px', flexWrap: 'wrap' }}>
            <span className="chart-value">{Number(lastRate).toFixed(4)}</span>
            <span className="chart-muted">PLN za 1 {currency}</span>
            {change != null && (
              <span className={`chart-change ${change >= 0 ? '' : 'negative'}`}>
                {change >= 0 ? '+' : ''}{change.toFixed(4)} ({changePct}%)
              </span>
            )}
          </div>
          <div className="chart-container">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      )}

      {!loading && !error && rates.length === 0 && fetched && (
        <p className="loading-hint">Brak danych dla wybranego zakresu.</p>
      )}

      {!fetched && (
        <p className="loading-hint">Wybierz walutę i zakres dat, następnie kliknij „Pokaż wykres”.</p>
      )}
    </>
  );
}

function SingleDayComparisonTab({ currencies, currency, setCurrency }) {
  const today = new Date().toISOString().slice(0, 10);
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  const weekAgoStr = weekAgo.toISOString().slice(0, 10);
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const defaultDate = yesterday.toISOString().slice(0, 10);

  const [selectedDate, setSelectedDate] = useState(defaultDate);
  const [compareWithDate, setCompareWithDate] = useState('');
  const [pastRate, setPastRate] = useState(null);
  const [pastRateDate, setPastRateDate] = useState(null);
  const [currentRate, setCurrentRate] = useState(null);
  const [currentRateDate, setCurrentRateDate] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const compareTwoDatesOnly = !!compareWithDate;

  const loadComparison = async () => {
    setError(null);
    setPastRate(null);
    setPastRateDate(null);
    setCurrentRate(null);
    setCurrentRateDate(null);
    setLoading(true);
    try {
      const fetchLastRateInRange = async (start, end) => {
        const data = await fetchRatesRange(currency, start, end);
        const rates = data.rates || [];
        if (rates.length === 0) throw new Error('Brak notowania dla wybranej daty');
        return rates[rates.length - 1];
      };

      const pastStart = new Date(selectedDate);
      pastStart.setDate(pastStart.getDate() - 14);
      const pastLatest = await fetchLastRateInRange(pastStart.toISOString().slice(0, 10), selectedDate);
      setPastRate({ currency, date: pastLatest.date, rate: pastLatest.rate });
      setPastRateDate(pastLatest.date);

      if (compareTwoDatesOnly) {
        const secondStart = new Date(compareWithDate);
        secondStart.setDate(secondStart.getDate() - 14);
        const secondLatest = await fetchLastRateInRange(secondStart.toISOString().slice(0, 10), compareWithDate);
        setCurrentRate({ currency, date: secondLatest.date, rate: secondLatest.rate });
        setCurrentRateDate(secondLatest.date);
      } else {
        const rangeData = await fetchRatesRange(currency, weekAgoStr, today);
        const rates = rangeData.rates || [];
        if (rates.length === 0) throw new Error('Brak notowania dla wybranej daty');
        const latest = rates[rates.length - 1];
        setCurrentRate({ currency, date: latest.date, rate: latest.rate });
        setCurrentRateDate(latest.date);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const pastVal = pastRate ? Number(pastRate.rate) : null;
  const currentVal = currentRate ? Number(currentRate.rate) : null;
  const diff = pastVal != null && currentVal != null ? currentVal - pastVal : null;
  const pct = diff != null && pastVal ? ((diff / pastVal) * 100).toFixed(2) : null;

  return (
    <>
      <div className="card">
        <div className="card-title">Wybierz walutę i daty</div>
        <div className="form-row form-row-3">
          <div>
            <label className="form-label">Waluta do porównania</label>
            <div className="select-wrap">
              <select value={currency} onChange={(e) => setCurrency(e.target.value)}>
                {currencies.map((c) => (
                  <option key={c} value={c}>
                    {getCurrencyLabel(c)}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="form-label">Data 1</label>
            <div className="date-wrap">
              <span className="date-icon">📅</span>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                max={today}
              />
            </div>
          </div>
          <div>
            <label className="form-label">Data 2 (opcjonalnie)</label>
            <div className="date-wrap">
              <span className="date-icon">📅</span>
              <input
                type="date"
                value={compareWithDate}
                onChange={(e) => setCompareWithDate(e.target.value)}
                max={today}
              />
            </div>
            {compareWithDate && (
              <button
                type="button"
                className="form-clear-link"
                onClick={() => setCompareWithDate('')}
              >
                Wyczyść – porównaj z dzisiaj
              </button>
            )}
          </div>
        </div>
        <div className="form-note">
          {compareWithDate
            ? 'Porównanie dwóch wybranych dat ze sobą.'
            : 'Pozostaw „Data 2” pustą, aby porównać Data 1 z dzisiejszym kursem.'}
        </div>
        <button
          type="button"
          onClick={loadComparison}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Ładowanie…' : 'Porównaj'}
        </button>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {pastRate && currentRate && (
        <div className="card">
          <div className="chart-label">Porównanie {currency} / PLN</div>
          {!compareTwoDatesOnly && currentRateDate !== today && (
            <div className="alert alert-info" role="status">
              Brak notowań na dzień dzisiejszy – wyświetlana jest cena z {formatDateDisplay(currentRateDate)}. NBP nie publikuje kursów w weekendy.
            </div>
          )}
          <div className="comparison-desc">
            {compareTwoDatesOnly
              ? `Porównanie kursu z ${formatDateDisplay(pastRateDate)} z kursem z ${formatDateDisplay(currentRateDate)}`
              : 'Porównanie kursu z wybranej daty z kursem bieżącym'}
          </div>
          <div className="comparison-row">
            <div className="comp-box past">
              <div className="comp-date">
                {formatDateDisplay(pastRateDate)}
                {pastRateDate !== selectedDate && (
                  <span className="comp-date-note"> (wybrano {formatDateDisplay(selectedDate)}, brak notowań)</span>
                )}
              </div>
              <div className="comp-rate">{pastVal.toFixed(4)}</div>
              <div className="comp-unit">PLN za 1 {currency}</div>
            </div>
            <div className="arrow-area">
              <span className="arrow-icon">→</span>
              <div className={`arrow-change ${diff >= 0 ? '' : 'negative'}`}>
                {diff >= 0 ? '↗' : '↘'} {diff >= 0 ? '+' : ''}{diff.toFixed(4)}
              </div>
              <div className={`arrow-pct ${diff >= 0 ? '' : 'negative'}`}>({diff >= 0 ? '+' : ''}{pct}%)</div>
            </div>
            <div className="comp-box current">
              <div className="comp-date">
                {formatDateDisplay(currentRateDate)}
                {!compareTwoDatesOnly && (currentRateDate === today ? ' (Dzisiaj)' : ' (ostatni dostępny)')}
              </div>
              <div className="comp-rate">{currentVal.toFixed(4)}</div>
              <div className="comp-unit">PLN za 1 {currency}</div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default function CurrencyPage({ activeTab }) {
  const [currencies, setCurrencies] = useState([]);
  const [currency, setCurrency] = useState('USD');

  useEffect(() => {
    fetchCurrencies()
      .then(setCurrencies)
      .catch(() => setCurrencies(['USD', 'EUR', 'CHF', 'GBP', 'CZK', 'DKK', 'NOK', 'SEK', 'JPY', 'CAD']));
  }, []);

  return (
    <div className="main">
      {activeTab === 'historical' && (
        <div className="tab-panel active">
          <HistoricalChartTab
            currencies={currencies}
            currency={currency}
            setCurrency={setCurrency}
          />
        </div>
      )}

      {activeTab === 'singleday' && (
        <div className="tab-panel active">
          <SingleDayComparisonTab
            currencies={currencies}
            currency={currency}
            setCurrency={setCurrency}
          />
        </div>
      )}
    </div>
  );
}
