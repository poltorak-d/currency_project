import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ChartPage from './pages/ChartPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="header">
          <h1>Kursy walut NBP</h1>
          <nav>
            <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
              Sprawdź kurs
            </NavLink>
            <NavLink to="/chart" className={({ isActive }) => isActive ? 'active' : ''}>
              Wykres
            </NavLink>
          </nav>
        </header>
        <main className="main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chart" element={<ChartPage />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>Dane z API Narodowego Banku Polskiego</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
