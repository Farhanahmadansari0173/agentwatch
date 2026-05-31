# AgentWatch Configuration Template
# Copy this to config.py and fill in your values

SPLUNK_HOST = "localhost"
SPLUNK_PORT = 8089
SPLUNK_USERNAME = "admin"
SPLUNK_PASSWORD = "YOUR_SPLUNK_PASSWORD"

TRACES_INDEX = "agentwatch_traces"
QUALITY_INDEX = "agentwatch_quality"

QUALITY_THRESHOLD = 0.7
LATENCY_THRESHOLD_MS = 3000

import os
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
