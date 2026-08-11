# AI Educational Platform

## Overview
A full-stack gamified online learning platform for programming and IT technologies, featuring an AI course generator, collaborative code editing, and a reward-based progression system.

## Architecture
- **Frontend:** Next.js 14 (App Router), React, TypeScript, Tailwind CSS, Framer Motion, Monaco Editor
- **Backend:** FastAPI (Python 3), SQLAlchemy ORM, Alembic migrations, JWT authentication
- **Database:** PostgreSQL (production), SQLite (development)
- **Infrastructure:** Docker Compose, Redis (caching & sessions)

## Key Features
- 🤖 **AI Course Generation** — Automatically generates lessons, coding challenges, and video recommendations using LLM APIs
- 📝 **Monaco Code Editor** — Full-featured code editor with syntax highlighting, auto-completion, and real-time collaboration (CRDT)
- 🎮 **Gamification System** — Internal currency, achievement badges, customizable avatars, and leaderboards
- 👥 **Role System** — Student and Teacher roles with different dashboards and permissions
- 🛡️ **Anti-Fraud Engine** — Detects suspicious activity patterns and prevents points manipulation
- 💳 **Subscription System** — Tiered access levels with premium content gating

## How to Run
```bash
# Start infrastructure
docker-compose up -d

# Backend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## Screenshots
Open `index.html` or run the dev server to view the platform UI.
