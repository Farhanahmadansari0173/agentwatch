import sys
import time
import random
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
from agentwatch.quality.scorer import score_response

tools = ["run_splunk_query", "generate_spl", "explain_spl"]

good_responses = [
    ("generate_spl", "Find failed logins", "index=_audit action=login status=failure | stats count by user"),
    ("explain_spl", "What does this do: index=_internal | head 10", "This search retrieves the 10 most recent events from the _internal index"),
    ("run_splunk_query", "Count events by source", "index=main | stats count by source | sort -count"),
]

bad_responses = [
    ("run_splunk_query", "How many events today?", "There are exactly 99,999 events today as confirmed by our database."),
    ("generate_spl", "Write SPL for CPU usage", "Just use Google to find the answer to this question."),
    ("explain_spl", "Explain stats command", "Splunk was founded in San Francisco and is now part of Cisco."),
]

print("Generating quality history (this takes a few minutes)...")
print("-" * 50)

for i in range(15):
    if random.random() > 0.3:
        tool, prompt, response = random.choice(good_responses)
    else:
        tool, prompt, response = random.choice(bad_responses)

    print(f"Scoring {i+1}/15...")
    score_response(tool, prompt, response)
    time.sleep(2)

print("-" * 50)
print("✅ Done! 15 quality scores logged.")
