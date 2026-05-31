import splunklib.client as client
import splunklib.results as results
import time

print("Connecting to Splunk...")

service = client.connect(
    host="localhost",
    port=8089,
    username="admin",
    password="Farhan@123"
)

print("Running test search...")
job = service.jobs.create('search index=_internal | head 5')

while not job.is_done():
    time.sleep(1)

reader = results.JSONResultsReader(job.results(output_mode='json'))
count = 0
for result in reader:
    if isinstance(result, dict):
        count += 1
        print(f"✅ Event {count}: {result.get('source', 'unknown')}")

print(f"\n✅ Day 2 complete — Splunk connection working! Got {count} events.")
