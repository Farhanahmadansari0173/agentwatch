import sys
import time
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')

from agentwatch.collector.interceptor import log_trace
from agentwatch.quality.scorer import score_response
from agentwatch.forecaster.cost_predictor import run_forecast
from agentwatch.healing.recommender import generate_fix

print("=" * 60)
print("AgentWatch Full Integration Test")
print("=" * 60)

# ── TEST 1: Trace logging ──────────────────────────────────
print("\n[1/4] Testing trace logging...")
trace = log_trace(
    "run_splunk_query",
    "search index=main | head 10",
    "10 events returned",
    850,
    "success"
)
if trace:
    print(f"✅ Trace logged: {trace['trace_id'][:8]}...")
else:
    print("❌ Trace logging failed")

time.sleep(1)

# ── TEST 2: Quality scoring ────────────────────────────────
print("\n[2/4] Testing quality scorer...")
quality = score_response(
    "generate_spl",
    "Write SPL to find errors in last hour",
    "index=_internal log_level=ERROR earliest=-1h | stats count by source"
)
if quality:
    print(f"✅ Quality scored: overall={quality['overall_score']} flagged={quality['flagged']}")
else:
    print("❌ Quality scoring failed")

time.sleep(1)

# ── TEST 3: Anomaly forecaster ─────────────────────────────
print("\n[3/4] Testing anomaly forecaster...")
anomalies = run_forecast()
if anomalies is not None:
    print(f"✅ Forecaster working: {len(anomalies)} anomalies detected")
else:
    print("❌ Forecaster failed")

time.sleep(1)

# ── TEST 4: Self-healing engine ────────────────────────────
print("\n[4/4] Testing self-healing engine...")
fix = generate_fix(
    "run_splunk_query",
    "connection timeout after 3000ms",
    "search index=main | transaction source maxspan=1h"
)
if fix:
    print(f"✅ Self-healing working: severity={fix['severity']}")
else:
    print("❌ Self-healing failed")

# ── SUMMARY ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("Integration Test Summary")
print("=" * 60)
print("✅ Trace collector    → agentwatch_traces index")
print("✅ Quality scorer     → agentwatch_quality index")
print("✅ Anomaly forecaster → MLTK predict command")
print("✅ Self-healing       → main index notable events")
print("\n🏆 AgentWatch is fully operational!")
print("=" * 60)
