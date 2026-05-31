import sys
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
from agentwatch.quality.scorer import score_response
import time

print("Testing AgentWatch Quality Scorer...")
print("=" * 60)

# Test 1 - Good response
print("\nTest 1: Good SPL query response")
score_response(
    "generate_spl",
    "Write an SPL query to find failed login attempts in the last hour",
    "index=_audit action=login status=failure earliest=-1h | stats count by user | sort -count"
)
time.sleep(1)

# Test 2 - Hallucinated response
print("\nTest 2: Hallucinated response (should be FLAGGED)")
score_response(
    "run_splunk_query",
    "How many events are in the main index?",
    "There are exactly 1,234,567 events in your main index as of yesterday at 3pm."
)
time.sleep(1)

# Test 3 - Irrelevant response
print("\nTest 3: Irrelevant response (should be FLAGGED)")
score_response(
    "explain_spl",
    "Explain what this SPL query does: index=_internal | stats count by source",
    "Splunk is a great platform for data analytics and was founded in 2003."
)
time.sleep(1)

# Test 4 - Good security response
print("\nTest 4: Good security analysis response")
score_response(
    "run_splunk_query",
    "Find anomalous network traffic patterns",
    "index=network | stats count by src_ip dest_port | where count > 1000 | sort -count | head 20"
)

print("\n" + "=" * 60)
print("✅ Quality scoring complete! Check agentwatch_quality index in Splunk.")
print("Run: index=agentwatch_quality | table tool, hallucination_score, relevance_score, flagged")
