# 🚀 StartupOS AI

**Multi-Agent AI Orchestration for Startup Business Planning**

Type your startup idea → 7 specialized AI agents collaboratively research, plan, and deliver a complete business package — all visible in real-time on a live dashboard.

## ⚡ Quick Start

```bash
# 1. Clone and setup
cp .env.example .env     # Edit with your API keys

# 2. Start with Docker
docker-compose up -d

# 3. Open browser
# Backend API: http://localhost:8000/docs
# Frontend:    http://localhost:5173
```

## 🏗️ Architecture

```
React + Vite (Frontend)
    ↕ REST + WebSocket
FastAPI (Backend)
    ↕ Sequential Agent Pipeline
Claude API (AI) + Brave Search (Tools)
    ↕
PostgreSQL (Data) + ChromaDB (Knowledge)
```

## 🤖 The 7 Agents

| Agent | Role | What It Does |
|-------|------|-------------|
| CEO Agent | Orchestrator | Decomposes idea into structured brief |
| Research Agent | Market Analyst | Finds market data, competitors, trends |
| Marketing Agent | Growth Strategist | Creates GTM strategy, branding, pricing |
| Developer Agent | Tech Lead | Designs tech stack and development roadmap |
| Finance Agent | CFO | Builds financial projections and unit economics |
| Analytics Agent | Data Analyst | Defines KPIs and measurement framework |
| Operations Agent | Project Manager | Creates 90-day execution checklist |

## 💰 Budget-Safe Development

**MOCK MODE is enabled by default.** Set `MOCK_MODE=true` in `.env` to use pre-built responses instead of burning API credits. Real Claude API calls only when you're ready.

## 📁 Project Structure

```
startupos-ai/
├── backend/          ← FastAPI + Python
│   ├── app/
│   │   ├── agents/   ← 7 agent classes + orchestrator
│   │   ├── api/      ← REST + WebSocket endpoints
│   │   ├── models/   ← SQLAlchemy + Pydantic schemas
│   │   ├── services/ ← Claude, WebSocket, DB services
│   │   └── tools/    ← Web search, calculator
│   └── tests/
├── frontend/         ← React + Vite
└── docker-compose.yml
```

## 🛠️ Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic v2
- **Frontend:** React 18, Vite, Zustand, Recharts
- **AI:** Claude API (Anthropic), Brave Search API
- **Database:** PostgreSQL, ChromaDB
- **Infrastructure:** Docker, Railway.app, Vercel

---

*Built by Raj Modi | MIT-WPU, Pune | B.Tech CSE (AI & Data Science)*
