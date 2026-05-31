import sys
import json
import time
import uuid
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
    """Call local Ollama for fix recommendations."""
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

def get_recent_successful_calls(tool_name, limit=3):
    """Pull recent successful calls for a tool from Splunk."""
    spl = f"""search index=agentwatch_traces 
tool="{tool_name}" status="success" earliest=-24h
| head {limit}
| table _time, tool, latency_ms, input_length, output_length, tokens_estimated"""

    try:
        service = get_splunk_service()
        job = service.jobs.create(spl)
        while not job.is_done():
            time.sleep(1)
        successful_calls = []
        reader = results.JSONResultsReader(job.results(output_mode='json'))
        for result in reader:
            if isinstance(result, dict):
                successful_calls.append(result)
        return successful_calls
    except Exception as e:
        print(f"❌ Failed to get context: {e}")
        return []

def get_quality_context(tool_name):
    """Get recent quality scores for a tool."""
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
    except Exception as e:
        return {}

def generate_fix(tool_name, error_context, failed_input=""):
    """
    Main self-healing function.
    Given a failed tool call, generate a fix recommendation.
    """
    print(f"\n🔧 Self-healing triggered for: {tool_name}")
    print(f"   Error: {error_context}")

    # Step 1: Pull context from Splunk
    print("   Pulling context from Splunk...")
    successful_calls = get_recent_successful_calls(tool_name)
    quality_context = get_quality_context(tool_name)

    # Step 2: Build fix prompt
    fix_prompt = f"""You are an AI operations expert helping fix a failing Splunk AI agent tool.

FAILED TOOL: {tool_name}
ERROR: {error_context}
FAILED INPUT: {failed_input}

RECENT SUCCESSFUL CALLS FOR THIS TOOL:
{json.dumps(successful_calls, indent=2) if successful_calls else "No recent successful calls found"}

RECENT QUALITY SCORES:
- Avg Hallucination Score: {quality_context.get('avg_h', 'N/A')}
- Avg Relevance Score: {quality_context.get('avg_r', 'N/A')}
- Avg Completeness Score: {quality_context.get('avg_c', 'N/A')}
- Total Scored: {quality_context.get('total_scored', 'N/A')}

Based on this context, provide a fix recommendation.
Return ONLY a valid JSON object:
{{
  "root_cause": "one sentence explanation of why it failed",
  "fix": "specific actionable fix in one sentence",
  "spl_correction": "corrected SPL query if applicable, else empty string",
  "severity": "high|medium|low",
  "confidence": 0.0
}}"""

    # Step 3: Get fix from Ollama
    print("   Generating fix recommendation with AI...")
    try:
        raw = ask_ollama(fix_prompt)
        start = raw.find("{")
        end = raw.rfind("}") + 1
        fix = json.loads(raw[start:end])
    except Exception as e:
        fix = {
            "root_cause": f"Unable to parse fix: {e}",
            "fix": "Manual investigation required",
            "spl_correction": "",
            "severity": "high",
            "confidence": 0.0
        }

    # Step 4: Write notable event to Splunk
    notable_event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "tool": tool_name,
        "error": error_context,
        "root_cause": fix.get("root_cause", ""),
        "fix": fix.get("fix", ""),
        "spl_correction": fix.get("spl_correction", ""),
        "severity": fix.get("severity", "medium"),
        "confidence": fix.get("confidence", 0.5),
        "status": "open",
        "source": "agentwatch_healing"
    }

    try:
        service = get_splunk_service()
        # Write to main index as a notable event
        index = service.indexes["main"]
        index.submit(
            json.dumps(notable_event),
            sourcetype="agentwatch:notable"
        )
        print(f"   ✅ Notable event created in Splunk")
    except Exception as e:
        print(f"   ❌ Failed to write notable event: {e}")

    # Print the fix
    print(f"\n   🔍 Root Cause: {fix.get('root_cause', 'Unknown')}")
    print(f"   💊 Fix: {fix.get('fix', 'Unknown')}")
    if fix.get('spl_correction'):
        print(f"   📝 SPL Correction: {fix.get('spl_correction', '')}")
    print(f"   ⚡ Severity: {fix.get('severity', 'medium').upper()}")
    print(f"   🎯 Confidence: {fix.get('confidence', 0.5)}")

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
