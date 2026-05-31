import splunklib.client as client
import json
import time
import uuid
import sys
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
import config

def get_splunk_service():
    """Connect to Splunk and return service object."""
    return client.connect(
        host=config.SPLUNK_HOST,
        port=config.SPLUNK_PORT,
        username=config.SPLUNK_USERNAME,
        password=config.SPLUNK_PASSWORD
    )

def log_trace(tool_name, inputs, outputs, latency_ms, status="success", error=None):
    """
    Log a single AI agent tool call trace to Splunk.
    This is the core function that AgentWatch uses to capture everything.
    """
    trace = {
        "trace_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "tool": tool_name,
        "latency_ms": latency_ms,
        "status": status,
        "input_length": len(str(inputs)),
        "output_length": len(str(outputs)) if outputs else 0,
        "tokens_estimated": len(str(inputs).split()) + len(str(outputs).split()) if outputs else 0,
        "error": error or "",
        "source": "agentwatch"
    }

    try:
        service = get_splunk_service()
        index = service.indexes[config.TRACES_INDEX]
        index.submit(json.dumps(trace), sourcetype="agentwatch:trace")
        print(f"✅ Trace logged: {tool_name} | {latency_ms}ms | {status}")
        return trace
    except Exception as e:
        print(f"❌ Failed to log trace: {e}")
        return None

def trace_tool_call(tool_name, inputs):
    """
    Decorator-style function to wrap any AI tool call.
    Usage:
        start = time.time()
        result = your_tool_call(inputs)
        latency = int((time.time() - start) * 1000)
        log_trace(tool_name, inputs, result, latency)
    """
    start_time = time.time()
    return start_time

def end_trace(tool_name, inputs, outputs, start_time, status="success", error=None):
    """Complete a trace that was started with trace_tool_call."""
    latency_ms = int((time.time() - start_time) * 1000)
    return log_trace(tool_name, inputs, outputs, latency_ms, status, error)

