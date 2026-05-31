import sys
import json
import time
import uuid
import random
from datetime import datetime, timedelta
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
import splunklib.client as client
import config

def get_splunk_service():
    return client.connect(
        host=config.SPLUNK_HOST,
        port=config.SPLUNK_PORT,
        username=config.SPLUNK_USERNAME,
        password=config.SPLUNK_PASSWORD
    )

tools = ["run_splunk_query", "generate_spl", "explain_spl"]

print("Generating 7 days of spread quality history...")
print("-" * 50)

service = get_splunk_service()
index = service.indexes[config.QUALITY_INDEX]
total = 0

for days_ago in range(7, 0, -1):
    base_time = datetime.now() - timedelta(days=days_ago)
    events_per_day = random.randint(8, 15)

    for i in range(events_per_day):
        event_time = base_time + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # Simulate quality degradation on day 2 and 5
        if days_ago in [2, 5]:
            hallucination = round(random.uniform(0.3, 0.6), 2)
            relevance = round(random.uniform(0.2, 0.5), 2)
        else:
            hallucination = round(random.uniform(0.7, 1.0), 2)
            relevance = round(random.uniform(0.7, 1.0), 2)

        completeness = round(random.uniform(0.4, 1.0), 2)
        overall = round((hallucination + relevance + completeness) / 3, 2)
        flagged = hallucination < 0.7 or relevance < 0.7

        event = {
            "_time": event_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "quality_id": str(uuid.uuid4()),
            "tool": random.choice(tools),
            "hallucination_score": hallucination,
            "relevance_score": relevance,
            "completeness_score": completeness,
            "overall_score": overall,
            "flagged": flagged,
            "reasoning": "historical simulation",
            "source": "agentwatch_quality"
        }

        index.submit(json.dumps(event), sourcetype="agentwatch:quality")
        total += 1

    print(f"✅ Day -{days_ago}: {events_per_day} quality scores generated")

print("-" * 50)
print(f"✅ Done! {total} quality scores logged across 7 days.")
