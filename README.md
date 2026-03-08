# Aplikacja kursów walut NBP

Aplikacja do pobierania i archiwizacji kursów walut z API Narodowego Banku Polskiego (NBP).  
Minimalizuje liczbę zapytań do API NBP dzięki hierarchii: **Redis (cache) → PostgreSQL → API NBP**.

## Funkcje

- **Sprawdź kurs** — wybór waluty i daty, wyświetlenie kursu
- **Wykres** — wykres zmian kursu w wybranym przedziale czasowym
- **Cache** — Redis z TTL 24h dla pojedynczych kursów
- **Archiwizacja** — zapis w PostgreSQL

## Wymagania

- Docker i Docker Compose
- (Opcjonalnie) Node.js 20+, Python 3.11+ do rozwoju lokalnego

## Uruchomienie z Docker Compose

```bash
# Sklonuj repozytorium i wejdź do katalogu
cd currency_project

# Uruchom wszystkie usługi
docker-compose up --build

# Aplikacja dostępna:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - Dokumentacja API: http://localhost:8000/docs
```

## Rozwój lokalny

### Backend

```bash
cd backend

# Utwórz wirtualne środowisko
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom PostgreSQL i Redis (np. docker-compose up postgres redis -d)
# Skopiuj .env.example do .env i dostosuj DATABASE_URL, REDIS_URL (localhost)

# Uruchom serwer
uvicorn app.main:app --reload --host 0.0.0.0
```

### Frontend

```bash
cd frontend

npm install
npm run dev

# Frontend: http://localhost:5173 (proxy API na localhost:8000)
```

### Baza danych

Dla rozwoju lokalnego uruchom tylko postgres i redis:

```bash
docker-compose up postgres redis -d
```

Następnie ustaw w `.env`:
```
DATABASE_URL=postgresql+asyncpg://currency:currency_secret@localhost:5432/currency_db
REDIS_URL=redis://localhost:6379/0
```

## API

| Endpoint | Opis |
|----------|------|
| `GET /rates/{currency}?date=YYYY-MM-DD` | Kurs dla pojedynczej daty |
| `GET /rates/{currency}/range?start_date=...&end_date=...` | Kursy w zakresie dat |
| `GET /currencies` | Lista obsługiwanych walut |
| `GET /health` | Health check |

## Struktura projektu

```
currency_project/
├── backend/          # FastAPI, SQLAlchemy, Redis
├── frontend/         # React, Vite, Chart.js
├── docker-compose.yml
└── PROJECT_PLAN.md   # Pełna specyfikacja
```

## Licencja

Projekt edukacyjny.
