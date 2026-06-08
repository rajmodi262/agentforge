<div align="center">

# 🤖 AgentForge

### Multi-Agent AI Planning Engine

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Give it a business idea. Watch 7 AI agents debate, analyze, and build your startup blueprint — live.**

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [Tech Stack](#-tech-stack) · [Demo](#-live-demo)

---

</div>

## 🎯 What is AgentForge?

AgentForge is a **production-grade multi-agent AI system** that transforms a raw business idea into a comprehensive startup blueprint. It orchestrates **7 specialized AI agents** through a sophisticated LangGraph state-machine workflow, featuring parallel execution, multi-step reasoning, and a unique Board Meeting debate mechanism for cross-validation.

> **💡 Example:** You type *"AI-powered fitness coaching app"* → AgentForge deploys 7 agents simultaneously → Within minutes, you get a 30-page PDF blueprint covering market research, competitive analysis, technical architecture, financial projections, go-to-market strategy, operations plan, and risk assessment.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **7 Autonomous Agents** | CEO, Research, Marketing, Developer, Finance, Analytics, Operations — each with domain-specific prompts and tools |
| 💎 **Diamond Topology** | Fan-out/fan-in parallel execution via LangGraph state machine (4 agents run simultaneously) |
| 🔄 **Multi-Step Reasoning** | Each agent runs a 3-step pipeline: Generate → Self-Critique → Refine with confidence scoring |
| ⚡ **Real-Time Streaming** | WebSocket-powered live visibility into agent thinking, reasoning steps, and inter-agent messages |
| 🏛️ **Board Meeting Debate** | Unique 4-round cross-functional debate where agents challenge each other's assumptions |
| 📄 **Auto-Generated Reports** | Beautiful PDF blueprints compiled from all agent outputs with charts and data |
| 🔐 **JWT Authentication** | Secure user sessions with protected routes and role-based access |
| 🐳 **Docker Compose** | One-command deployment with PostgreSQL, Redis, and all services containerized |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   PRESENTATION TIER                         │
│              React + Vite + WebSocket Client                │
│   ┌──────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │Dashboard │  │ Live Stream  │  │Report Viewer │         │
│   └──────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST + WebSocket
┌─────────────────────────┴───────────────────────────────────┐
│                   APPLICATION TIER                          │
│              FastAPI + LangGraph + Claude/Gemini            │
│                                                             │
│   ┌─────────┐    ┌───────────────┐    ┌──────────────┐     │
│   │REST API │───▶│  Orchestrator │───▶│  AI Service   │     │
│   └─────────┘    └───────┬───────┘    └──────────────┘     │
│                          │                                   │
│              ┌───────────┼───────────┐                      │
│              ▼           ▼           ▼                      │
│         ┌────────┐ ┌────────┐ ┌────────┐                   │
│         │Research│ │  Dev   │ │Finance │  ... (7 agents)    │
│         └────────┘ └────────┘ └────────┘                   │
│                          │                                   │
│              ┌───────────┴───────────┐                      │
│              ▼                       ▼                      │
│        ┌──────────┐          ┌────────────┐                 │
│        │Board Meet│          │Report Gen  │                 │
│        └──────────┘          └────────────┘                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                      DATA TIER                              │
│           PostgreSQL + Redis + SQLAlchemy ORM               │
└─────────────────────────────────────────────────────────────┘
```

### 🔀 Agent Pipeline (9-Node Diamond Topology)

```
START → CEO Agent → ┬─ Research Agent  ─┐
                    ├─ Marketing Agent ─┤
                    ├─ Developer Agent ─┤─→ Analytics → Operations → Board Meeting → Report → END
                    └─ Finance Agent   ─┘
                      (parallel fan-out)    (fan-in)        (sequential)         (debate)
```

### 🧠 Multi-Step Reasoning (Per Agent)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Step 1:     │────▶│  Step 2:     │────▶│  Step 3:     │────▶│  Validate:   │
│  Generate    │     │  Self-Critique│     │  Refine      │     │  Pydantic    │
│  (Claude API)│     │  (3 flaws)   │     │  (Fix flaws) │     │  (JSON safe) │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
   🔴 stream:           🔴 stream:           🔴 stream:
   agent_thinking       reasoning_step       agent_completed
```

### 🔄 User Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as Startup Founder
    participant UI as React UI (WebSocket Client)
    participant API as FastAPI Gateway
    participant LG as LangGraph Orchestrator
    participant AG as 7-Agent Cluster
    participant DB as PostgreSQL Database

    User->>UI: Submits raw startup idea
    UI->>API: POST /api/blueprint (Initialize Session)
    API->>DB: Create project record & audit trail
    API->>LG: Trigger graph orchestration (background task)
    LG->>UI: Establish WebSocket connection
    
    rect rgb(30, 41, 59)
        note over LG, AG: Parallel Agent Execution (Diamond Topology)
        LG->>AG: Fan-out: Invoke CEO, Research, Marketing, Dev, & Finance agents
        AG-->>UI: Live-stream thinking tokens & reasoning steps via WS
    end

    rect rgb(15, 23, 42)
        note over LG, AG: Consensus Debate & Report Generation
        LG->>AG: Initiate structured 4-Round Board Meeting Debate
        AG-->>UI: Broadcast inter-agent debate statements
        LG->>API: Compile final consolidated markdown report
        API->>DB: Save generated PDF/Markdown blueprint files
    end

    API-->>UI: Emit workflow completion signal
    UI->>User: Render 3D debate visualization & enable PDF download
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Claude API key or Gemini API key

### 1. Clone & Configure

```bash
git clone https://github.com/rajmodi262/agentforge.git
cd agentforge
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run with Docker (Recommended)

```bash
docker-compose up --build
```

### 3. Run Locally (Development)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### 4. Access

| Service | URL |
|---------|-----|
| 🌐 Frontend | http://localhost:5173 |
| ⚡ Backend API | http://localhost:8000 |
| 📚 API Docs | http://localhost:8000/docs |

---

## 🛠 Tech Stack

<table>
<tr>
<td><b>Layer</b></td>
<td><b>Technology</b></td>
<td><b>Purpose</b></td>
</tr>
<tr>
<td>🧠 AI Engine</td>
<td>LangGraph, Claude API, Gemini API</td>
<td>Agent orchestration, multi-step LLM reasoning</td>
</tr>
<tr>
<td>⚡ Backend</td>
<td>FastAPI, SQLAlchemy, Pydantic</td>
<td>Async REST API, ORM, schema validation</td>
</tr>
<tr>
<td>🔄 Real-Time</td>
<td>WebSocket, Redis</td>
<td>Live agent streaming, event broadcasting</td>
</tr>
<tr>
<td>🎨 Frontend</td>
<td>React 18, Vite, GSAP</td>
<td>Interactive dashboard, 3D animations</td>
</tr>
<tr>
<td>🗄️ Database</td>
<td>PostgreSQL, SQLite (dev)</td>
<td>Persistent storage, session management</td>
</tr>
<tr>
<td>🐳 DevOps</td>
<td>Docker Compose, GitHub Actions</td>
<td>Containerized deployment, CI/CD</td>
</tr>
</table>

---

## 📂 Project Structure

```
agentforge/
├── backend/
│   ├── app/
│   │   ├── agents/              # 7 AI agents + orchestrator
│   │   │   ├── base_agent.py    # Multi-step reasoning engine
│   │   │   ├── orchestrator.py  # LangGraph workflow builder
│   │   │   ├── board_meeting.py # Multi-round debate engine
│   │   │   ├── ceo_agent.py
│   │   │   ├── research_agent.py
│   │   │   ├── marketing_agent.py
│   │   │   ├── developer_agent.py
│   │   │   ├── finance_agent.py
│   │   │   ├── analytics_agent.py
│   │   │   ├── operations_agent.py
│   │   │   └── report_compiler.py
│   │   ├── api/                 # REST endpoints
│   │   ├── models/              # Pydantic schemas + DB models
│   │   ├── services/            # Claude/Gemini, WebSocket, RAG
│   │   └── main.py              # FastAPI application entry
│   ├── tests/                   # Pytest test suite
│   └── requirements.txt
├── frontend/                    # React + Vite SPA
├── docker-compose.yml
└── README.md
```

---

## 🏛️ Board Meeting — The Secret Sauce

What makes AgentForge unique is the **Board Meeting Debate Engine**. After all 7 agents complete their analysis, they enter a structured 4-round debate:

| Round | Matchup | Topic |
|-------|---------|-------|
| 1 | Finance → CEO | Revenue model & unit economics viability |
| 2 | Developer → Marketing | Go-to-market timeline vs. technical feasibility |
| 3 | Research → Finance | TAM/SAM accuracy & market sizing assumptions |
| 4 | Operations → Developer | Infrastructure scaling readiness |

A **Board Secretary** then synthesizes all debates into a consensus score, identifies key risks, and produces the final strategic recommendation.

---

## 📊 What You Get

When you submit a business idea, AgentForge generates a comprehensive blueprint including:

- ✅ **Vision & Problem Statement** — Clear articulation of the opportunity
- ✅ **Market Research** — TAM/SAM/SOM analysis with competitor mapping
- ✅ **Go-to-Market Strategy** — Pricing, channels, customer acquisition cost
- ✅ **Technical Architecture** — Full stack recommendation with MVP roadmap
- ✅ **Financial Projections** — 3-year revenue model with break-even analysis
- ✅ **KPI Dashboard** — Key metrics and success criteria
- ✅ **Operations Plan** — Hiring roadmap, launch timeline, risk mitigation
- ✅ **Board Consensus** — Cross-validated insights from agent debates

---

## 🔧 Environment Variables

```env
# AI Provider (at least one required)
ANTHROPIC_API_KEY=sk-ant-...       # Claude API
GOOGLE_API_KEY=AIza...             # Gemini API (free tier)

# Database
DATABASE_URL=postgresql://user:pass@localhost/agentforge

# Security
JWT_SECRET_KEY=your-secret-key

# Optional
MOCK_MODE=true                     # Use dynamic mocks (no API cost)
LOG_LEVEL=INFO
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Raj Modi](https://github.com/rajmodi262)**

*If you found this useful, please ⭐ the repo!*

</div>
