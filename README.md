# 📋 Pastebin Lite

A lightweight, feature-rich pastebin application for sharing text content with expiry and view limits. Create, share, and view pastes with optional time-to-live (TTL) and maximum view restrictions.

## 🔗 Live Deployment

**[View Live Application](https://pastebin-litee-chi.vercel.app)**

---

## ✨ Features

- **Create Pastes**: Share text content with a unique shareable URL
- **Time-to-Live (TTL)**: Set optional expiration time for pastes (in seconds)
- **View Limits**: Restrict the number of times a paste can be viewed
- **Unique IDs**: Auto-generated unique identifiers for each paste
- **Health Monitoring**: Built-in health check endpoint for monitoring
- **Async Processing**: Fast, non-blocking operations using async/await
- **Database Persistence**: PostgreSQL-backed storage with SQLAlchemy ORM

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Async Driver**: asyncpg
- **Migrations**: Alembic
- **Logging**: structlog
- **Configuration**: Pydantic Settings
- **Python**: 3.13+

### Frontend
- **Framework**: React with TypeScript
- **Router**: React Router
- **Build Tool**: Vite
- **Styling**: TailwindCSS + Emotion
- **UI Components**: Radix UI
- **Animations**: Motion
- **Package Manager**: npm

---

## 📡 API Routes

### Health & Status

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/healthz` | Health check endpoint (verifies database connectivity) | `{ "ok": true }` |

### Paste Management

#### Create a Paste
```
POST /pastes
Content-Type: application/json

Request Body:
{
  "content": "string",           // Required: Paste content (non-empty)
  "ttl_seconds": 3600,          // Optional: Expiry in seconds (≥ 1)
  "max_views": 5                // Optional: Max views allowed (≥ 1)
}

Response (201):
{
  "id": "abc123xyz",
  "url": "https://pastebinlitee-nu.vercel.app/p/abc123xyz"
}

Error Responses:
- 400: Invalid request (empty content, negative TTL/views)
- 500: Server error creating paste
```

#### Retrieve a Paste (API)
```
GET /pastes/{paste_id}

Response (200):
{
  "content": "string",
  "remaining_views": 4,         // null if unlimited
  "expires_at": "2026-01-01T00:00:00.000Z"  // null if no TTL
}

Error Responses:
- 404: Paste not found, expired, or view limit exceeded
- 400: Invalid x-test-now-ms header
- 500: Server error retrieving paste

Note: Each successful API fetch counts as one view
```

#### View a Paste (HTML)
```
GET /p/{paste_id}

Response (200): HTML page displaying the paste content
Error (404): Paste unavailable or not found

Note: Paste content is rendered safely without script execution
```

---

## 🖥️ Frontend Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | `CreatePaste` | Main page for creating new pastes |
| `/p/:id` | `ViewPaste` | Display a specific paste with full content |
| `/success/:id` | `SuccessPage` | Confirmation page after paste creation |

---

## 🚀 Local Deployment Guide

### Prerequisites

- **Python 3.13+** (with `uv` package manager)
- **Node.js 18+** (with npm)
- **PostgreSQL** (local or Docker)
- **Git**

### Prerequisites Setup

#### 1. Install uv (Python Package Manager)
```bash
pip install uv
# or follow: https://docs.astral.sh/uv/getting-started/installation/
```

#### 2. Verify Node.js & npm
```bash
node --version  # Should be v18+
npm --version   # Should be v9+
```

#### 3. Start PostgreSQL (using Docker)
```bash
docker pull postgres:15
docker run --name pastebin_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pastebin \
  -p 5432:5432 \
  -d postgres:15
```

---

### Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

#### Step 1: Create Environment File
Create a `.env` file in the `backend/` directory with local settings:

```env
# Database Configuration (LOCAL)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pastebin

# API Configuration (LOCAL)
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Environment Settings
ENVIRONMENT=LOCAL
ENV_MODE=LOCAL
LOG_LEVEL=INFO
```

#### Step 2: Install Dependencies
```bash
uv sync
```

#### Step 3: Run Database Migrations
```bash
uv run alembic upgrade head
```

#### Step 4: Start the Backend Server
```bash
uv run fastapi dev main.py
```

**Backend runs at**: `http://localhost:8000`

**API Documentation** (auto-generated):
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

### Frontend Setup

In a new terminal, navigate to the frontend directory:
```bash
cd frontend
```

#### Step 1: Create Environment File
Create a `.env` file in the `frontend/` directory with local settings:

```env
# API Configuration (LOCAL)
VITE_API_URL=http://localhost:8000
```

#### Step 2: Install Dependencies
```bash
npm install
```

#### Step 3: Start the Development Server
```bash
npm run dev
```

**Frontend runs at**: `http://localhost:5173`

---

## 📦 API Request Examples

### Create a Paste
```bash
curl -X POST http://localhost:8000/pastes \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello, World! This is a test paste.",
    "ttl_seconds": 3600,
    "max_views": 10
  }'
```

### Retrieve a Paste
```bash
curl http://localhost:8000/pastes/abc123xyz
```

### View Paste as HTML
```bash
curl http://localhost:8000/p/abc123xyz
```

### Health Check
```bash
curl http://localhost:8000/healthz
```

---

## 🔧 Environment Variables

### Backend (`.env` in `backend/`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost:5432/pastebin` |
| `API_BASE_URL` | Backend API base URL | `http://localhost:8000` (local) / `https://your-domain.com` (prod) |
| `FRONTEND_URL` | Frontend application URL | `http://localhost:5173` (local) / `https://your-frontend.vercel.app` (prod) |
| `ENVIRONMENT` | Deployment environment | `LOCAL`, `STAGING`, `PRODUCTION` |
| `ENV_MODE` | Application mode | `LOCAL`, `PRODUCTION` |
| `LOG_LEVEL` | Logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Frontend (`.env` in `frontend/`)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` (local) / `https://your-api-domain.com` (prod) |

---

## 📁 Project Structure

```
pastebin_Lite/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── routes.py            # API endpoint definitions
│   ├── service.py           # Business logic for paste operations
│   ├── model.py             # Pydantic request/response models
│   ├── orm.py               # SQLAlchemy ORM setup
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection manager
│   ├── background_tasks.py  # Async background cleanup tasks
│   ├── requirements.txt      # Python dependencies (legacy)
│   ├── pyproject.toml       # Modern Python project config
│   ├── alembic.ini          # Alembic migration config
│   └── migrations/          # Database migration files
├── frontend/
│   ├── src/
│   │   ├── main.tsx         # React entry point
│   │   ├── app/
│   │   │   ├── App.tsx      # Main App component
│   │   │   ├── routes.tsx   # React Router configuration
│   │   │   ├── pages/       # Page components
│   │   │   │   ├── CreatePaste.tsx
│   │   │   │   ├── ViewPaste.tsx
│   │   │   │   └── SuccessPage.tsx
│   │   │   └── components/  # Reusable UI components
│   │   │       ├── ui/      # Radix UI components
│   │   │       └── figma/   # Figma integration components
│   │   └── styles/          # CSS/TailwindCSS styles
│   ├── vite.config.ts       # Vite configuration
│   └── package.json         # npm dependencies
└── docker-compose.yml       # Docker multi-container setup
```

---

## 🐳 Docker Deployment (Optional)

To run the entire application stack using Docker:

```bash
docker-compose up --build
```

This starts:
- Backend (FastAPI) on `http://localhost:8000`
- Frontend (Vite dev server) on `http://localhost:5173`
- PostgreSQL database on `localhost:5432`

---

## 🧪 Testing

### Test Health Endpoint
```bash
curl http://localhost:8000/healthz
# Expected: { "ok": true }
```

### Test Paste Creation & Retrieval
```bash
# Create
RESPONSE=$(curl -X POST http://localhost:8000/pastes \
  -H "Content-Type: application/json" \
  -d '{"content": "Test paste"}')

PASTE_ID=$(echo $RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

# Retrieve
curl http://localhost:8000/pastes/$PASTE_ID
```

---

## 🚨 Troubleshooting

### Backend Issues

**PostgreSQL connection error**
- Ensure PostgreSQL is running: `docker ps | grep postgres`
- Verify `DATABASE_URL` in `.env` is correct
- Check database exists: `psql -l`

**Port 8000 already in use**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Migrations failed**
```bash
# Reset and re-run migrations
alembic downgrade base
alembic upgrade head
```

### Frontend Issues

**Port 5173 already in use**
```bash
# Kill process using port 5173
lsof -ti:5173 | xargs kill -9
```

**Dependencies not found**
```bash
npm install
npm cache clean --force
```

---

## 📚 Additional Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Router Documentation](https://reactrouter.com/)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/)
- [Vite Documentation](https://vitejs.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/)

---

## 📝 License

This project is open source. See LICENSE file for details.

---

## 👨‍💻 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Last Updated**: March 14, 2026
