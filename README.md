# AgentWatch — AI Observability for Splunk AI Agents

> **Splunk Agentic Ops Hackathon 2026** | Track: Observability

## 🏆 What is AgentWatch?

AgentWatch is a real-time AI observability platform that monitors the health, quality, and cost of AI agents running inside your Splunk environment.

When your MCP Server returns a hallucinated result, when your AI Assistant starts drifting in quality, or when your token costs are about to spike — **AgentWatch catches it first, explains why, and fixes it automatically.**

> *"Who watches your AI? AgentWatch does."*

---

## 🎯 The Problem

As organizations deploy AI agents inside Splunk for security operations, observability, and developer productivity, a critical gap emerges:

- **No visibility** into AI agent health, latency, or failure rates
- **No quality control** — hallucinated SPL queries go undetected
- **No cost forecasting** — token spikes hit billing before anyone notices
- **No self-healing** — failed agent calls require manual investigation

AgentWatch solves all four problems in a single Splunk app.

---

## ✨ Key Features

### 1. 🔥 Agent Trace Collection
- Captures every MCP tool call with latency, token usage, and status
- OpenTelemetry-compatible trace format
- Real-time flame graph visualization in Splunk dashboard

### 2. 🎯 AI Quality Scoring
- Uses LLM-as-judge to score every agent response
- Scores hallucination, relevance, and completeness (0.0–1.0)
- Fires drift alerts when quality drops below threshold

### 3. 📈 Token Cost Forecasting
- Uses Splunk MLTK `predict` command for time-series forecasting
- Detects token usage anomalies against upper confidence bounds
- Predicts cost spikes 24 hours before they hit billing

### 4. 🔧 Self-Healing Engine
- Pulls context from recent successful calls via Splunk search
- Generates root cause + corrective SPL using local AI
- Writes notable events back to Splunk automatically

### 5. 🌐 REST API
- FastAPI endpoint accepts traces and quality scores via HTTP
- Any external tool can push data to AgentWatch
- Auto-generated Swagger docs at `/docs`

---

## 🏗️ Architecture

See [architecture_diagram.png](./architecture_diagram.png) for the full system diagram.
---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Data Platform | Splunk Enterprise 10.4 |
| MCP Integration | Splunk MCP Server 1.2.0 |
| ML Forecasting | Splunk AI Toolkit 5.7.4 (MLTK predict) |
| Quality Scoring | Ollama llama3.2 (LLM-as-judge) |
| Backend API | Python 3.13 + FastAPI |
| Splunk SDK | splunk-sdk 3.0.0 |

---

## 🚀 Setup Instructions

### Prerequisites
- Mac/Linux/Windows machine with 8GB+ RAM
- Python 3.9+
- Splunk Enterprise 10.4 (free trial)
- Ollama (free, runs locally)

### Step 1 — Install Splunk Enterprise
```bash
# Download from splunk.com/download
# Install and start
/Applications/Splunk/bin/splunk start --accept-license
```

### Step 2 — Install required Splunk apps
Install from Splunkbase:
- Splunk MCP Server 1.2.0 (app ID: 7931)
- Splunk AI Toolkit 5.7.4
- Python for Scientific Computing for Mac Apple Silicon

### Step 3 — Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

### Step 4 — Clone and configure
```bash
git clone https://github.com/Farhanahmadansari0173/agentwatch.git
cd agentwatch
cp config.example.py config.py
# Edit config.py with your Splunk credentials
pip install splunk-sdk fastapi uvicorn anthropic requests
```

### Step 5 — Create Splunk indexes
In Splunk → Settings → Indexes → New Index:
- `agentwatch_traces`
- `agentwatch_quality`

### Step 6 — Enable token authentication
In Splunk → Settings → Tokens → Enable Token Authentication → New Token

### Step 7 — Run AgentWatch
```bash
# Terminal 1: Start FastAPI server
uvicorn main:app --reload --port 8001

# Terminal 2: Generate test data
python agentwatch/collector/generate_test_data.py

# Terminal 3: Run quality scorer
python agentwatch/quality/test_scorer.py

# Terminal 4: Run forecaster
python agentwatch/forecaster/cost_predictor.py
```

### Step 8 — Import dashboard
In Splunk → Search & Reporting → Dashboards → Create New Dashboard → Source → paste contents of `agentwatch/dashboard/agentwatch_dashboard.xml`

### Step 9 — Run full integration test
```bash
python test_integration.py
```

---

## 📁 Project Structure
---

## 🎬 Demo

Watch the demo video: https://youtu.be/-21cVP-gzXU

The demo shows:
1. Live MCP agent call being captured and traced
2. Quality drift detected and alert fired
3. Token cost spike predicted 2 hours ahead
4. Self-healing engine generating a fix automatically

---

## 🏆 Prize Targets

| Prize | Why AgentWatch qualifies |
|---|---|
| **Grand Prize ($7,000)** | Strongest all-round submission — novel, impactful, technically deep |
| **Best Observability ($3,000)** | Direct track submission — observability for AI agents |
| **Best Hosted Models ($1,000)** | MLTK forecasting + LLM-as-judge quality scoring |

---

## 📄 License

MIT License — see [LICENSE](./LICENSE)

---

## 👤 Author

**Farhan Ahmad Ansari**
Splunk Agentic Ops Hackathon 2026
