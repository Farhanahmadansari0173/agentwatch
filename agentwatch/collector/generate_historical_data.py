import sys
import random
from datetime import datetime, timedelta
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
import splunklib.client as client
import json
import uuid
import config

def get_splunk_service():
    return client.connect(
        host=config.SPLUNK_HOST,
        port=config.SPLUNK_PORT,
        username=config.SPLUNK_USERNAME,
        password=config.SPLUNK_PASSWORD
    )

tools = ["run_splunk_query", "generate_spl", "explain_spl"]
statuses = ["success", "success", "success", "success", "error"]

print("Generating 7 days of historical trace data...")
print("-" * 50)

service = get_splunk_service()
index = service.indexes[config.TRACES_INDEX]

total = 0
for days_ago in range(7, 0, -1):
    base_time = datetime.now() - timedelta(days=days_ago)
    events_per_day = random.randint(40, 80)
    for i in range(events_per_day):
        event_time = base_time + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        tool = random.choice(tools)
        status = random.choices(statuses, weights=[70,10,10,5,5])[0]
        latency = random.randint(200, 5000)
        tokens = random.randint(50, 500)
        trace = {
            "_time": event_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "trace_id": str(uuid.uuid4()),
            "tool": tool,
            "latency_ms": latency,
            "status": status,
            "input_length": random.randint(30, 200),
            "output_length": random.randint(20, 150) if status == "success" else 0,
            "tokens_estimated": tokens,
            "error": "timeout" if status == "error" else "",
            "source": "agentwatch"
        }
        index.submit(
            json.dumps(trace),
            sourcetype="agentwatch:trace"
        )
        total += 1
    print(f"✅ Day -{days_ago}: {events_per_day} events generated")

print("-" * 50)
print(f"✅ Done! {total} historical traces logged.")
