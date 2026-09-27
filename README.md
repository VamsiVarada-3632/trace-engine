# TRACE — Troubleshooting & Root-Cause Adaptive Context Engine

An AI-powered manufacturing defect resolution agent that uses persistent memory to assist engineers with troubleshooting machine defects.

## Overview

TRACE maintains a persistent memory of:
- Machine-specific incidents
- Observed symptoms and operating conditions
- Suspected and confirmed root causes
- Troubleshooting actions and their outcomes
- Resolution details

As incidents accumulate, TRACE becomes increasingly effective at recommending interventions based on verified historical outcomes.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│  ┌─────────┐ ┌──────────────┐ ┌────────────┐ ┌───────────┐  │
│  │Dashboard│ │Report Incident│ │  Analysis  │ │  Memory   │  │
│  └─────────┘ └──────────────┘ └────────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────┐ ┌───────────────┐ ┌────────────────────┐  │
│  │Incident API  │ │ Analysis API  │ │  Recommendation    │  │
│  │              │ │               │ │      Engine        │  │
│  └──────────────┘ └───────────────┘ └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │   Hindsight  │ │   SQLite     │ │   LLM API    │
      │   (Memory)   │ │ (App State)  │ │  (Analysis)  │
      └──────────────┘ └──────────────┘ └──────────────┘
```

## Tech Stack

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: Python 3.11 + FastAPI
- **Memory**: Hindsight (persistent operational memory)
- **Database**: SQLite (application state)
- **LLM**: OpenAI GPT-4 / Anthropic Claude

## Project Structure

```
trace-engine/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   ├── lib/             # Utilities and API clients
│   │   └── types/           # TypeScript types
│   └── package.json
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── core/            # Core configuration
│   │   ├── models/          # Data models
│   │   ├── services/        # Business logic
│   │   └── hindsight/       # Hindsight integration
│   ├── requirements.txt
│   └── main.py
├── data/                     # Synthetic data and schemas
│   ├── schema/
│   └── synthetic/
└── docs/                     # Documentation
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Hindsight API access

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Configure environment
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local  # Configure environment
npm run dev
```

## Core Workflow

1. **Report Incident** — Submit machine defect details
2. **Retrieve Memory** — Search Hindsight for similar historical incidents
3. **Analyze** — Compare successful vs failed interventions
4. **Recommend** — Generate evidence-based troubleshooting guidance
5. **Record Outcome** — Document intervention results
6. **Learn** — Store verified outcomes for future retrieval

## Key Principle

> TRACE does not simply know manufacturing knowledge. It remembers the organization's own troubleshooting experience and uses verified historical outcomes to assist engineers with future incidents.

## License

MIT
