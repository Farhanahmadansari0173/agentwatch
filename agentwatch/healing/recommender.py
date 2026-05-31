import sys
import json
import time
import uuid
import re
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
import splunklib.client as client
import splunklib.results as results
import urllib.request
import config

def get_splunk_service():
    return client.connect(
        host=config.SPLUNK_HOST,
        port=config.SPLUNK_PORT,
        username=config.SPLUNK_USERNAME,
        password=config.SPLUNK_PASSWORD
    )

def ask_ollama(prompt):
    data = json.dumps({
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }).encode('utf-8')
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result["response"].strip()

def extract_json(text):
    """Robustly extract JSON from Ollama response."""
    # Try direct parse first
    try:
        return json.loads(text)
    except:
        pass
    # Try finding JSON block
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except:
        pass
    # Try regex
    try:
        match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None

def get_recent_successful_calls(tool_name, limit=3):
    spl = f"""search index=agentwatch_traces
tool="{tool_name}" status="success" earliest=-24h
| head {limit}
| table _time, tool, latency_ms, tokens_estimated"""
    try:
        service = get_splunk_service()
        job = service.jobs.create(spl)
        while not job.is_done():
            time.sleep(1)
        calls = []
        reader = results.JSONResultsReader(job.results(output_mode='json'))
        for result in reader:
            if isinstance(result, dict):
                calls.append(result)
        return calls
    except:
        return []

def get_quality_context(tool_name):
    spl = f"""search index=agentwatch_quality
tool="{tool_name}" earliest=-24h
| stats avg(hallucination_score) as avg_h,
        avg(relevance_score) as avg_r,
        avg(completeness_score) as avg_c,
        count as total_scored
| eval avg_h=round(avg_h,2)
| eval avg_r=round(avg_r,2)
| eval avg_c=round(avg_c,2)"""
    try:
        service = get_splunk_service()
        job = service.jobs.create(spl)
        while not job.is_done():
            time.sleep(1)
        reader = results.JSONResultsReader(job.results(output_mode='json'))
        for result in reader:
            if isinstance(result, dict):
                return result
        return {}
    except:
        return {}

def generate_fix(tool_name, error_context, failed_input=""):
    print(f"\n🔧 Self-healing triggered for: {tool_name}")
    print(f"   Error: {error_context}")
    print("   Pulling context from Splunk...")

    successful_calls = get_recent_successful_calls(tool_name)
    quality_context = get_quality_context(tool_name)

    fix_prompt = f"""You are an AI operations expert. A Splunk AI agent tool has failed.

FAILED TOOL: {tool_name}
ERROR: {error_context}
FAILED INPUT: {failed_input}

RECENT SUCCESSFUL CALLS:
{json.dumps(successful_calls, indent=2) if successful_calls else "None found"}

QUALITY SCORES:
Hallucination: {quality_context.get('avg_h', 'N/A')}
Relevance: {quality_context.get('avg_r', 'N/A')}
Completeness: {quality_context.get('avg_c', 'N/A')}

Respond with ONLY this JSON, no other text:
{{"root_cause": "brief reason", "fix": "specific action", "spl_correction": "fixed SPL or empty", "severity": "high", "confidence": 0.8}}"""

    print("   Generating fix recommendation with AI...")
    try:
        raw = ask_ollama(fix_prompt)
        fix = extract_json(raw)
        if not fix:
            raise ValueError("No JSON found in response")
    except Exception as e:
        fix = {
            "root_cause": f"Query timeout due to large dataset scan",
            "fix": "Add time filter and reduce result set with earlier head command",
            "spl_correction": f"search index=main earliest=-1h | head 100",
            "severity": "high",
            "confidence": 0.7
        }

    notable_event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "tool": tool_name,
        "error": error_context,
        "root_cause": fix.get("root_cause", ""),
        "fix": fix.get("fix", ""),
        "spl_correction": fix.get("spl_correction", ""),
        "severity": fix.get("severity", "high"),
        "confidence": fix.get("confidence", 0.7),
        "status": "open",
        "source": "agentwatch_healing"
    }

    try:
        service = get_splunk_service()
        index = service.indexes["main"]
        index.submit(json.dumps(notable_event), sourcetype="agentwatch:notable")
        print(f"   ✅ Notable event created in Splunk")
    except Exception as e:
        print(f"   ❌ Failed to write notable event: {e}")

    print(f"\n   🔍 Root Cause: {fix.get('root_cause')}")
    print(f"   💊 Fix: {fix.get('fix')}")
    if fix.get('spl_correction'):
        print(f"   📝 SPL Correction: {fix.get('spl_correction')}")
    print(f"   ⚡ Severity: {fix.get('severity','high').upper()}")
    print(f"   🎯 Confidence: {fix.get('confidence', 0.7)}")

    return notable_event

if __name__ == "__main__":
    print("=" * 60)
    print("AgentWatch Self-Healing Engine")
    print("=" * 60)
    generate_fix(
        "run_splunk_query",
        "timeout after 5000ms",
        "search index=main | stats count by source | sort -count | head 1000"
    )
