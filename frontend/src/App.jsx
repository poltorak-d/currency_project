import { useState } from 'react';
import { useTheme } from './ThemeContext';
import CurrencyPage from './pages/CurrencyPage';
import './App.css';

function App() {
  const { isDark, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('historical');

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-icon">📈</div>
          <div className="sidebar-brand-text">
            <span className="sidebar-title">Kursy</span>
            <span className="sidebar-subtitle">Walut NBP</span>
          </div>
        </div>
        <nav className="sidebar-nav">
          <button
            type="button"
            className={`sidebar-link ${activeTab === 'historical' ? 'sidebar-link-active' : ''}`}
            onClick={() => setActiveTab('historical')}
          >
            <span className="sidebar-link-icon">📊</span>
            <span className="sidebar-link-text">Wykres historyczny</span>
          </button>
          <button
            type="button"
            className={`sidebar-link ${activeTab === 'singleday' ? 'sidebar-link-active' : ''}`}
            onClick={() => setActiveTab('singleday')}
          >
            <span className="sidebar-link-icon">🔄</span>
            <span className="sidebar-link-text">Porównanie dni</span>
          </button>
        </nav>
        <div className="sidebar-footer">
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            title={isDark ? 'Przełącz na tryb jasny' : 'Przełącz na tryb ciemny'}
          >
            <span className="theme-toggle-icon">{isDark ? '☀️' : '🌙'}</span>
            <span className="theme-toggle-label">{isDark ? 'Tryb jasny' : 'Tryb ciemny'}</span>
          </button>
          <p className="sidebar-credits">Dane z NBP</p>
        </div>
      </aside>
      <div className="app-content">
        <header className="header">
          <h1 className="header-title">Porównaj kursy walut w czasie</h1>
          <p className="header-sub">Kursy NBP w relacji do PLN</p>
        </header>
        <CurrencyPage activeTab={activeTab} />
      </div>
    </div>
  );
}

export default App;
