import sys
import json
import time
import uuid
import urllib.request
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

def ask_ollama(prompt):
    """Call local Ollama model — free, no API key needed."""
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

def score_response(tool_name, prompt, response):
    """
    Use local Ollama as LLM judge to score an AI agent response.
    Scores hallucination, relevance, and completeness (0.0 to 1.0).
    """
    judge_prompt = f"""You are evaluating the quality of an AI agent response in a Splunk environment.

Tool called: {tool_name}
Input prompt: {prompt}
Agent response: {response}

Score this response on three dimensions from 0.0 to 1.0:
- hallucination: Is the response factually grounded? (1.0 = no hallucination)
- relevance: Does it answer what was asked? (1.0 = fully relevant)
- completeness: Is it complete and useful? (1.0 = fully complete)

Return ONLY a valid JSON object, nothing else, no explanation:
{{"hallucination": 0.0, "relevance": 0.0, "completeness": 0.0, "reasoning": "brief"}}"""

    try:
        raw = ask_ollama(judge_prompt)

        # Extract JSON safely
        start = raw.find("{")
        end = raw.rfind("}") + 1
        scores = json.loads(raw[start:end])

        flagged = (
            scores["hallucination"] < config.QUALITY_THRESHOLD or
            scores["relevance"] < config.QUALITY_THRESHOLD
        )

        quality_event = {
            "quality_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "tool": tool_name,
            "hallucination_score": scores["hallucination"],
            "relevance_score": scores["relevance"],
            "completeness_score": scores["completeness"],
            "overall_score": round(
                (scores["hallucination"] +
                 scores["relevance"] +
                 scores["completeness"]) / 3, 2
            ),
            "reasoning": scores.get("reasoning", ""),
            "flagged": flagged,
            "source": "agentwatch_quality"
        }

        service = get_splunk_service()
        index = service.indexes[config.QUALITY_INDEX]
        index.submit(json.dumps(quality_event), sourcetype="agentwatch:quality")

        status = "⚠️  FLAGGED" if flagged else "✅ PASSED"
        print(f"{status} | {tool_name} | H:{scores['hallucination']} R:{scores['relevance']} C:{scores['completeness']}")
        return quality_event

    except Exception as e:
        print(f"❌ Scoring failed: {e}")
        return None
