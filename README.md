# 🧠 Multi-Agent Competitive Programming Coach

An AI-powered coaching platform that uses a team of specialized agents to teach competitive programming through **Socratic dialogue** — never giving direct answers, always guiding through questions.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                  │
│              Real-time SSE streaming UI                │
└────────────────────────┬─────────────────────────────┘
                         │ REST + SSE
┌────────────────────────▼─────────────────────────────┐
│                  FastAPI Backend                       │
│  ┌─────────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Auth (JWT)  │  │ Sessions │  │  SSE Streaming │  │
│  └─────────────┘  └──────────┘  └────────┬───────┘  │
│                                           │          │
│  ┌────────────────────────────────────────▼───────┐  │
│  │            LangGraph Supervisor                 │  │
│  │  ┌─────────────────────────────────────────┐   │  │
│  │  │  Problem   │ Teaching │ Algorithm │ Code │   │  │
│  │  │  Analyzer  │  Agent   │  Expert   │Review│   │  │
│  │  ├─────────────────────────────────────────┤   │  │
│  │  │ Complexity │  Test    │ Learning  │      │   │  │
│  │  │ Analyzer   │  Cases   │  Memory   │      │   │  │
│  │  └─────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
│  ┌────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ PostgreSQL │  │  Qdrant  │  │      Redis       │  │
│  │  (state)   │  │ (vectors)│  │    (caching)     │  │
│  └────────────┘  └──────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer          | Technology                        |
| -------------- | --------------------------------- |
| Frontend       | Next.js 14, TypeScript, Tailwind  |
| Backend        | FastAPI (async), Python 3.12+     |
| Agent Framework| LangGraph + LangChain             |
| LLM            | OpenAI GPT-4o                     |
| Database       | PostgreSQL 16 (async via asyncpg) |
| Vector DB      | Qdrant                            |
| Cache          | Redis 7                           |
| Auth           | JWT (python-jose + passlib)       |

## Agent System

| Agent                | Role                                                        |
| -------------------- | ----------------------------------------------------------- |
| **Supervisor**       | Routes queries to the right specialist agent                |
| **Problem Analyzer** | Parses problems, estimates difficulty, identifies categories|
| **Teaching Agent**   | Core Socratic coach — guides with questions, not answers    |
| **Algorithm Expert** | Explains algorithms, compares approaches pedagogically     |
| **Complexity Analyzer** | Analyzes time/space complexity, validates student analysis|
| **Test Case Generator**| Creates edge cases, explains why each matters             |
| **Code Review**      | Reviews code WITHOUT rewriting — only explains issues       |
| **Learning Memory**  | Tracks proficiency, identifies patterns and weaknesses      |

## Two Modes

- **Learning Mode** — Full Socratic coaching with progressive hints (levels 0–5)
- **Contest Mode** — Timer, no hints, only clarification questions allowed

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key

### Setup

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 2. Start all services
make dev

# 3. Access
# Backend API:  http://localhost:8000
# API Docs:     http://localhost:8000/docs
# Frontend:     http://localhost:3000
```

### Local Development (without Docker)

```bash
# Start infrastructure
docker compose up -d postgres redis qdrant

# Install backend deps
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Path                              | Description                    |
| ------ | --------------------------------- | ------------------------------ |
| POST   | `/api/auth/register`              | Register new user              |
| POST   | `/api/auth/login`                 | Login, get JWT                 |
| POST   | `/api/sessions/`                  | Create coaching session        |
| GET    | `/api/sessions/`                  | List sessions                  |
| GET    | `/api/sessions/{id}`              | Session details + messages     |
| POST   | `/api/sessions/{id}/chat/stream`  | SSE streaming chat             |
| POST   | `/api/sessions/{id}/submit-code`  | Submit code for review         |
| PATCH  | `/api/sessions/{id}`              | Update session status          |
| GET    | `/api/profile/`                   | User learning profile          |
| GET    | `/api/profile/progress`           | Progress over time             |
| GET    | `/api/problems/`                  | List problems                  |
| GET    | `/health`                         | Health check                   |

## License

MIT
