# 🐛 IssueHub — Lightweight Bug Tracker

IssueHub is a minimal, fast, and feature-complete bug tracker where teams can create projects, file issues, comment on them, manage project memberships, and track issue resolution.

---

## 🛠️ Tech Choices & Trade-Offs

- **Backend**: **FastAPI (Python 3.11+)**
  - *Why*: High performance, automatic OpenAPI documentation, async support, and explicit type validation via Pydantic v2.
  - *Trade-off*: Lighter out-of-the-box feature set than Django, requiring explicit route/dependency wiring, which keeps the codebase clean and modular.
- **Database & ORM**: **SQLite (Local Dev) / PostgreSQL (Prod ready) with SQLAlchemy 2.0 & Alembic**
  - *Why*: Zero-config local setup using SQLite, with seamless PostgreSQL migration support via SQLAlchemy connection strings and Alembic migrations.
- **Frontend**: **React 19 (Vite) + React Router v7**
  - *Why*: Ultra-fast development and bundle speeds with Vite, clean component structure, and responsive vanilla CSS styling.
- **Authentication**: **JWT (Bearer Tokens & Secure HTTP-only Cookies)**
  - *Why*: Supports both SPA token-based auth and browser cookie auth seamlessly. Passwords hashed using `bcrypt`.

---

## 🚀 Setup Instructions

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`

### 2. Backend Setup
```bash
cd backend

# Create & activate virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` in the `backend/` directory:
```bash
cp .env.example .env
```
Default `.env` values:
```env
DATABASE_URL=sqlite:///./issuehub.db
SECRET_KEY=SUPER_SECRET_KEY_FOR_ISSUEHUB_LOCAL_DEV_JWT_SIGNING
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 4. Database Migrations & Seed Data
```bash
cd backend

# Run database migrations
python -m alembic upgrade head

# (Optional) Seed demo data (3 users, 2 projects, 15 issues, comments)
python seed.py
```

---

## 🏃 How to Run

### Run Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```
- API Endpoint: `http://localhost:8000`
- Interactive API Docs (Swagger): `http://localhost:8000/docs`

### Run Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 🧪 Running Tests

The backend includes a comprehensive test suite (36 unit & integration tests) covering auth, projects, membership permissions, issue CRUD, filtering/sorting, and comments.

```bash
cd backend
pytest tests/ -v
```

---

## 🔑 Demo Credentials

If you ran `python seed.py`, you can log in with:

| User | Email | Password | Role |
|------|-------|----------|------|
| **Alice Admin** | `alice@demo.com` | `password123` | Maintainer |
| **Bob Dev** | `bob@demo.com` | `password123` | Member |
| **Carol QA** | `carol@demo.com` | `password123` | Member |

---

## 📐 Architecture & Project Structure

```
issueTracker/
├── backend/
│   ├── alembic/              # Database migration scripts
│   ├── routers/              # Modular API endpoints
│   │   ├── auth.py           # Login, Signup, Logout, /me
│   │   ├── projects.py       # Project CRUD & Member Management
│   │   ├── issues.py         # Issue CRUD, Filter, Search, Sort
│   │   └── comments.py       # Comment thread endpoints
│   ├── auth_utils.py         # JWT generation/decoding & bcrypt hashing
│   ├── database.py           # SQLAlchemy engine & session factory
│   ├── dependencies.py       # Auth dependencies & member resolution
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic request/response validation schemas
│   ├── seed.py               # Seed script for sample data
│   ├── main.py               # FastAPI application entry & exception handlers
│   └── tests/                # Pytest unit & integration test suite
│       ├── test_auth.py
│       ├── test_projects.py
│       ├── test_issues.py
│       └── test_comments.py
└── frontend/
    ├── src/
    │   ├── components/       # Reusable UI (Navbar, Modal, Toast)
    │   ├── pages/            # Page components (AuthPage, ProjectsPage, IssuesPage, IssueDetailPage)
    │   ├── api.js            # Fetch wrapper for REST API
    │   ├── App.jsx           # Main router & auth state wrapper
    │   └── index.css         # Custom design system & styles
    └── package.json
```

### Core API Endpoints
- `POST /api/auth/signup` — Register new user
- `POST /api/auth/login` — Authenticate user & return JWT token
- `POST /api/auth/logout` — Clear auth cookie
- `GET  /api/me` — Fetch logged in user profile
- `GET  /api/projects` — List user's projects
- `POST /api/projects` — Create project (creator becomes maintainer)
- `GET  /api/projects/{id}` — Get single project details
- `GET  /api/projects/{id}/members` — List project members
- `POST /api/projects/{id}/members` — Invite/add project member (maintainer only)
- `GET  /api/projects/{id}/issues` — List/filter/search/sort issues in project
- `POST /api/projects/{id}/issues` — Create new issue
- `GET  /api/issues/{id}` — Fetch issue details
- `PATCH /api/issues/{id}` — Update issue (status/assignee restricted to maintainers)
- `DELETE /api/issues/{id}` — Delete issue (reporter or maintainer only)
- `GET  /api/issues/{id}/comments` — List comments on issue
- `POST /api/issues/{id}/comments` — Add comment to issue

---

## 🔮 Known Limitations & Future Enhancements

1. **Email Notifications**: Member invitations currently add users directly by email without sending external email tokens.
2. **File Attachments**: Issues and comments currently support plain text / markdown; image/file upload attachments could be added with S3 storage.
3. **Activity Log / Audit History**: Adding an event audit stream for status changes and reassignments on issues.
4. **WebSocket / Live Updates**: Real-time comment updates using FastAPI WebSockets.
