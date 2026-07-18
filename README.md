# NexusAPI

A multi-tenant project management REST API built with FastAPI. Organizations, projects, tasks, role-based access control, Redis caching, and real-time WebSocket notifications — production-grade backend architecture built from scratch.

> **Status:** Core features shipped. Actively extending with AI task assistance and rate limiting.

---

## Architecture Overview

```
Client (HTTP/WebSocket)
        ↓
FastAPI Application
        ↓
┌─────────────────────────────────────────┐
│  Auth Layer (JWT + bcrypt)              │
│  RBAC (admin → manager → member)        │
│  Ownership Chain Authorization           │
│  task → project → org → membership     │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│  Redis Cache Layer                      │
│  projects:{org_id} → project list       │
│  tasks:{project_id} → task list         │
│  Invalidated on write, 5min TTL         │
└─────────────────────────────────────────┘
        ↓
PostgreSQL (SQLAlchemy ORM + Alembic)

WebSocket Layer (Real-time Notifications)
ConnectionManager → app.state → shared across all routes
Pushes instantly on task assignment and deadline warnings

APScheduler (Background Jobs)
→ Deadline checker runs every hour
→ Notifies assigned users 24 hours before deadline
→ Duplicate prevention — one notification per task per user
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Framework | FastAPI | Async REST API + WebSocket support |
| Database | PostgreSQL | Primary data store |
| Cache | Redis | Project and task list caching with TTL |
| ORM | SQLAlchemy 2.0 | Database models and queries |
| Migrations | Alembic | Schema version control |
| Auth | JWT + bcrypt | Stateless authentication |
| Real-time | WebSockets | Instant notification delivery |
| Scheduler | APScheduler | Background deadline checking |
| Validation | Pydantic | Request/response schemas |
| Server | Uvicorn | ASGI server |

---

## Key Design Decisions

**Multi-tenancy via ownership chain**
Every protected resource traces back to organization membership. A user can only access tasks inside projects inside organizations they belong to.
```
task → project → organization → membership → user
```
Enforced on every protected route via a single membership query — no route trusts the client's claimed identity without verifying through this chain.

**Role-based access control**
```
admin    → full access, invite members, manage org
manager  → create projects, create and assign tasks
member   → view projects and tasks, receive assignments
viewer   → read-only (planned)
```

**Redis caching strategy**
Project and task list endpoints check Redis before hitting PostgreSQL. On write (create/assign), the relevant cache key is deleted immediately so the next read fetches fresh data. 5-minute TTL acts as a safety net for any missed invalidations.
```
GET /projects/{org_id}
    ↓
Check Redis: projects:{org_id}
    ↓ hit → return instantly
    ↓ miss → query PostgreSQL → store in Redis → return
```

**WebSocket notification system**
ConnectionManager stored in `app.state` ensures one shared phonebook instance across all routes. Task assignment pushes instantly to the assigned user's open connection. If offline — notification persists in PostgreSQL.
```
Task assigned
     ↓
Notification saved to DB (permanent)
     ↓
WebSocket push attempted (real-time if online)
     ↓
User retrieves via GET /notifications (if offline)
```

**Deadline checker with duplicate prevention**
APScheduler runs hourly, finds tasks due within 24 hours, and creates notifications — but only if one doesn't already exist for that task and user. Prevents notification spam on repeated job runs.

**Junction tables for many-to-many relationships**
Users can belong to multiple organizations with different roles in each. Tasks can be assigned to multiple members. Both modeled via junction tables — memberships and assignments — keeping the core tables clean.

---

## Project Structure

```
app/
├── main.py                    # App setup, router registration, lifespan
├── database.py                # DB engine, session, get_db dependency
├── models.py                  # SQLAlchemy models + Enums
├── schema.py                  # Pydantic request/response schemas
├── auths/
│   └── auth.py                # JWT creation, decoding, getCurrentUser
├── routers/
│   ├── auth.py                # register, login
│   ├── organizations.py       # org creation, member management
│   ├── projects.py            # project CRUD + Redis cache
│   ├── tasks.py               # task creation, assignment + Redis cache
│   └── notifications.py       # WebSocket endpoint, get, mark read
├── services/
│   ├── auth_services.py       # password hashing, JWT utilities
│   └── connection_manager.py  # WebSocket connection phonebook
└── schedular/
    └── background_job.py      # APScheduler deadline checker
alembic/                       # DB migration history
```

---

## Database Schema

```
users
  id, name, email, password, created_at

organizations
  id, name, created_by (FK → users.id), created_at

memberships                        ← junction table
  id, user_id (FK), org_id (FK), role, joined_at

projects
  id, title, org_id (FK), created_by (FK → users.id), created_at

tasks
  id, title, project_id (FK), status, priority, deadline, created_at

assignments                        ← junction table
  id, user_id (FK), task_id (FK), assigned_by (FK → users.id), assigned_at

notifications
  id, user_id (FK), task_id (FK), type, message, read, created_at
```

---

## Setup & Installation

**Requirements:** Python 3.10+, PostgreSQL, Redis

```bash
# Clone
git clone https://github.com/muhammads-git/workstream-api.git
cd workstream-api

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Fill in your values

# Run database migrations
alembic upgrade head

# Start Redis (must be running before app starts)
# Windows: open Memurai
# Linux/Mac: redis-server

# Start the API
uvicorn app.main:app --reload
```

---

## Environment Variables

Create a `.env` file in the root:

```
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
```

Create `.env.example` with the same keys and empty values for contributors.

---

## API Endpoints

### Authentication
```
POST /v1/auth/register     Register new user
POST /v1/auth/login        Login, returns JWT token
```

### Organizations
```
POST /v1/organization                    Create organization
POST /v1/organizations/{org_id}/invite   Add member to org (admin only)
```

### Projects
```
POST /v1/projects              Create project (admin/manager only)
GET  /v1/projects/{org_id}     Get all projects — Redis cached
```

### Tasks
```
POST /v1/tasks                      Create task (admin/manager only)
POST /v1/tasks/{task_id}/assign     Assign task to org member
GET  /v1/tasks/{project_id}         Get all tasks — Redis cached
```

### Notifications
```
GET   /notifications                          Get all my notifications
PATCH /notifications/{notification_id}/read   Mark as read
```

### WebSocket
```
WS /ws/{user_id}    Real-time notification channel
```

Connect on login. Server pushes on:
- Task assigned to you
- Task deadline within 24 hours

---

## Authentication

All protected routes require:

```
Authorization: Bearer <token>
```

Get token from `POST /v1/auth/login`.
In Swagger UI — click **Authorize** at the top and paste your token.

---

## Planned Improvements

- AI-powered task description generation via Groq API
- Task status update endpoint with flow enforcement (todo → in_progress → review → done)
- Rate limiting per user per organization
- Pagination on list endpoints
- Docker + docker-compose for one-command setup
- pytest test coverage for critical routes
