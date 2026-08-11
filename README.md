<div align="center">

# 🎓 AI Educational Platform

### Gamified Learning Platform Powered by AI

<p>
  <img src="https://img.shields.io/badge/Next.js_14-000?style=for-the-badge&logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini_AI-8E75B2?style=for-the-badge&logo=google&logoColor=white" />
</p>

<p><i>A comprehensive online learning platform with AI-powered course generation, in-browser coding, and gamified rewards</i></p>

</div>

---

## ✨ Features

- 🤖 **AI Course Generation** — Google Gemini creates personalized learning paths
- 💻 **Monaco Code Editor** — Full VS Code experience in the browser
- 🎮 **Gamification System** — XP, levels, badges, and leaderboards
- 👥 **Real-Time Collaboration** — Code together with other students
- 🐳 **Docker Infrastructure** — One-command deployment
- 🔐 **JWT Authentication** — Secure user accounts and sessions
- 📊 **Admin Dashboard** — Analytics, user management, content moderation
- 📈 **Progress Tracking** — Visual learning progress for each student

## 🛠️ Tech Stack

| Layer | Technology |
|:---:|:---|
| ![Next.js](https://img.shields.io/badge/Next.js_14-000?style=flat-square&logo=next.js&logoColor=white) | Frontend Framework |
| ![React](https://img.shields.io/badge/React_19-20232A?style=flat-square&logo=react&logoColor=61DAFB) | UI Components |
| ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) | Type Safety |
| ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) | Backend API |
| ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square) | ORM & Database |
| ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) | Containerization |
| ![Gemini](https://img.shields.io/badge/Gemini_AI-8E75B2?style=flat-square&logo=google&logoColor=white) | AI Engine |

## 🚀 Quick Start

```bash
# Clone the repository
git clone git@github.com:Zishwhwhw/ai-educational-platform.git
cd ai-educational-platform

# Start with Docker
docker-compose up --build

# Or run manually:
# Backend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## 📁 Project Structure

```
ai-educational-platform/
├── 🐳 docker-compose.yml     # Container orchestration
├── 📂 backend/                # FastAPI backend
│   ├── ⚙️ main.py             # App entry point
│   ├── 🗃️ database.py         # Database connection
│   ├── 📊 models.py           # SQLAlchemy models
│   ├── 📝 schemas.py          # Pydantic schemas
│   ├── 🔐 auth/               # JWT authentication
│   ├── 🛣️ routers/            # API endpoints
│   └── 🔧 services/           # Business logic
└── 📂 frontend/               # Next.js 14 frontend
    ├── 📂 src/                 # Source code
    ├── 📂 public/              # Static assets
    └── ⚙️ next.config.ts       # Next.js config
```

## 👨‍💻 Author

**Andrii Drymchenko** — Full-Stack Developer & AI Product Builder

[![GitHub](https://img.shields.io/badge/GitHub-Zishwhwhw-181717?style=flat-square&logo=github)](https://github.com/Zishwhwhw)
[![Upwork](https://img.shields.io/badge/Upwork-Hire_Me-14A800?style=flat-square&logo=upwork&logoColor=white)](https://www.upwork.com)

## 📄 License

MIT License

---

<div align="center">
  <sub>Built with ❤️ and 🤖 AI</sub><br/>
  <sub>⭐ Star this repo if you found it useful!</sub>
</div>