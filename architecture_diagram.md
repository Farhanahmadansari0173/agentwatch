# AgentWatch — Architecture Diagram

## System Overview
## Data Flow

1. AI agent makes a tool call (MCP, AI Assistant, etc.)
2. AgentWatch Collector intercepts and logs trace to `agentwatch_traces`
3. Quality Scorer evaluates the response and logs to `agentwatch_quality`
4. Forecaster runs MLTK predict on token usage, detects anomalies
5. Self-Healing Engine pulls context, generates fix, writes to `main`
6. Dashboard visualizes all data in real-time across 8 panels

## How AI Models are Integrated

- **Ollama llama3.2** — local LLM used as quality judge and fix generator
- **Splunk MLTK predict** — built-in ML command for time-series forecasting
- **Splunk MCP Server** — provides AI agents access to Splunk data
- **Splunk AI Toolkit** — provides ML algorithms and visualizations

## How the App Interacts with Splunk

- Uses **Splunk Python SDK** for all data ingestion and search
- Uses **Splunk REST API** (port 8089) for programmatic access
- Uses **Splunk indexes** for storing all AgentWatch events
- Uses **Splunk dashboard XML** for visualization layer
- Uses **Splunk saved searches** for automated drift and spike alerts
