# NexusAPI

A multi-tenant project management REST API built with FastAPI. Organizations, projects, tasks, role-based access control, and real-time WebSocket notifications — all in one backend service.

> **Status:** Core features complete. Actively being extended with Redis caching, AI task assistance, and advanced analytics.

---

## Architecture Overview

```
Client (HTTP/WebSocket)
        ↓
FastAPI Application
        ↓
┌───────────────────────────────────────┐
│  Auth Layer (JWT)                     │
│  RBAC (admin → manager → member)      │
│  Ownership Chain Authorization         │
│  task → project → org → membership   │
└───────────────────────────────────────┘
        ↓
PostgreSQL (SQLAlchemy ORM + Alembic)
        
WebSocket Layer (Real-time Notifications)
ConnectionManager → app.state → shared across all routes

APScheduler (Background Jobs)
→ Deadline checker runs every hour
→ Notifies assigned users 24 hours before deadline
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Framework | FastAPI | Async REST API + WebSocket support |
| Database | PostgreSQL | Primary data store |
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
Every protected resource traces back to organization membership. A user can only access tasks that belong to projects inside organizations they are members of.
```
task → project → organization → membership → user
```
This chain is enforced on every protected route via a single membership query.

**Role-based access control**
Four roles with different permissions:
```
admin    → full access, invite members, manage org
manager  → create projects, create tasks, assign tasks
member   → view projects and tasks, receive assignments
viewer   → read-only access (planned)
```

**WebSocket notification system**
ConnectionManager stored in `app.state` ensures one shared instance across all routes and workers. When a task is assigned, the route pushes instantly to the assigned user's open WebSocket connection. If offline, notification persists in PostgreSQL for retrieval.

```
Task assigned
     ↓
Notification saved to DB (permanent record)
     ↓
WebSocket push attempted (real-time if online)
     ↓
User retrieves via GET /notifications (if offline)
```

**Deadline checking**
APScheduler runs every hour, queries tasks due within 24 hours, and creates notifications for assigned users — but only if a notification doesn't already exist, preventing duplicate alerts.

---

## Project Structure

```
app/
├── main.py                    # App setup, router registration, lifespan
├── database.py                # DB engine, session, get_db dependency
├── models.py                  # SQLAlchemy models
├── schema.py                  # Pydantic request/response schemas
├── auths/
│   └── auth.py                # JWT creation, decoding, getCurrentUser
├── routers/
│   ├── auth.py                # /auth/register, /auth/login
│   ├── organizations.py       # org creation, member management
│   ├── projects.py            # project CRUD
│   ├── tasks.py               # task creation, assignment
│   └── notifications.py       # notification delivery, WebSocket
├── services/
│   ├── auth_services.py       # password hashing, JWT utilities
│   └── connection_manager.py  # WebSocket connection phonebook
└── schedular/
    └── background_job.py      # APScheduler deadline checker
alembic/                       # DB migration files
```

---

## Database Schema

```
users
  id, name, email, password, created_at

organizations
  id, name, created_by (FK users), created_at

memberships                        ← junction table (many-to-many)
  id, user_id (FK), org_id (FK), role, joined_at

projects
  id, title, org_id (FK), created_by (FK users), created_at

tasks
  id, title, project_id (FK), status, priority, deadline, created_at

assignments                        ← junction table (many-to-many)
  id, user_id (FK), task_id (FK), assigned_by (FK), assigned_at

notifications
  id, user_id (FK), task_id (FK), type, message, read, created_at
```

---

## Setup & Installation

**Requirements:** Python 3.10+, PostgreSQL, Git

```bash
# Clone
git clone https://github.com/muhammads-git/nexus-api.git
cd nexus-api

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Fill in your values

# Run migrations
alembic upgrade head

# Start the API
uvicorn app.main:app --reload
```

---

## Environment Variables

```env
DATABASE_URL=
SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=
```

---

## API Endpoints

### Authentication
```
POST /v1/auth/register     Register new user
POST /v1/auth/login        Login, returns JWT token
```

### Organizations
```
POST /v1/organization                    Create organization (auth required)
POST /v1/organizations/{org_id}/invite   Invite member to org (admin only)
```

### Projects
```
POST /v1/projects              Create project (admin/manager only)
GET  /v1/projects/{org_id}     Get all projects in organization
```

### Tasks
```
POST /v1/tasks                      Create task (admin/manager only)
POST /v1/tasks/{task_id}/assign     Assign task to org member
GET  /v1/tasks/{project_id}         Get all tasks in project
```

### Notifications
```
GET   /notifications                          Get all my notifications
PATCH /notifications/{notification_id}/read   Mark notification as read
```

### WebSocket
```
WS /ws/{user_id}    Connect for real-time notifications
```

Connect on login. Server pushes instantly on:
- Task assignment
- Deadline approaching (24 hour warning)

---

## Authentication

All protected routes require a Bearer token:

```
Authorization: Bearer <token>
```

Get token from `POST /v1/auth/login`. In Swagger UI — click **Authorize** and paste your token.

---

## Planned Improvements

- Redis caching layer for frequently accessed data
- AI-powered task description generation via Groq API
- Task status update endpoint with status flow enforcement
- Pagination on list endpoints
- Rate limiting per user
- Docker + docker-compose setup
- Test coverage with pytest
