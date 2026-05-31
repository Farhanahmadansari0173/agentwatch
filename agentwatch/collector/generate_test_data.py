import sys
import time
import random
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
from agentwatch.collector.interceptor import log_trace

# Simulate 20 realistic MCP tool calls
tools = [
    "run_splunk_query",
    "generate_spl",
    "explain_spl",
    "run_splunk_query",
    "run_splunk_query"
]

statuses = ["success", "success", "success", "success", "error"]

print("Generating 20 test traces into Splunk...")
print("-" * 50)

for i in range(20):
    tool = random.choice(tools)
    status = random.choices(statuses, weights=[70,10,10,5,5])[0]
    latency = random.randint(200, 5000)

    inputs = f"query_{i}: search index=_internal | head 10"
    outputs = f"result_{i}: 10 events returned" if status == "success" else None
    error = "timeout" if status == "error" else None

    log_trace(tool, inputs, outputs, latency, status, error)
    time.sleep(0.3)

print("-" * 50)
print("✅ Done! 20 traces logged to agentwatch_traces index.")
print("Go to Splunk Search and run: index=agentwatch_traces | head 20")
