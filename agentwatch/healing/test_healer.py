import sys
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
from agentwatch.healing.recommender import generate_fix
import time

print("Testing AgentWatch Self-Healing Engine")
print("=" * 60)

# Test 1 - Timeout
print("\n--- Test 1: Query Timeout ---")
generate_fix(
    "run_splunk_query",
    "timeout after 5000ms",
    "search index=main | stats count by source | sort -count | head 1000"
)
time.sleep(2)

# Test 2 - Bad SPL
print("\n--- Test 2: Invalid SPL ---")
generate_fix(
    "generate_spl",
    "SPL syntax error: unexpected token 'FORM'",
    "search index=main FORM source | head 10"
)
time.sleep(2)

# Test 3 - Low quality
print("\n--- Test 3: Low Quality Response ---")
generate_fix(
    "explain_spl",
    "quality score below threshold: relevance=0.2, hallucination=0.3",
    "explain what this does: index=_internal | head 10"
)

print("\n" + "=" * 60)
print("✅ Self-healing tests complete!")
print("Check Splunk: index=main sourcetype=agentwatch:notable")
