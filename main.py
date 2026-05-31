import sys
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import time
from agentwatch.collector.interceptor import log_trace
from agentwatch.quality.scorer import score_response

app = FastAPI(
    title="AgentWatch API",
    description="AI Observability for Splunk AI Agents",
    version="1.0.0"
)

class TraceRequest(BaseModel):
    tool_name: str
    inputs: str
    outputs: Optional[str] = None
    latency_ms: int
    status: Optional[str] = "success"
    error: Optional[str] = None

class QualityRequest(BaseModel):
    tool_name: str
    prompt: str
    response: str

@app.get("/")
def root():
    return {
        "app": "AgentWatch",
        "status": "running",
        "description": "AI Observability for Splunk AI Agents"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/trace")
def submit_trace(req: TraceRequest):
    """Submit an AI agent tool call trace to Splunk."""
    result = log_trace(
        req.tool_name,
        req.inputs,
        req.outputs,
        req.latency_ms,
        req.status,
        req.error
    )
    if result:
        return {"status": "logged", "trace_id": result["trace_id"]}
    raise HTTPException(status_code=500, detail="Failed to log trace")

@app.post("/score")
def submit_quality(req: QualityRequest):
    """Score an AI agent response for quality."""
    result = score_response(req.tool_name, req.prompt, req.response)
    if result:
        return {
            "status": "scored",
            "quality_id": result["quality_id"],
            "overall_score": result["overall_score"],
            "flagged": result["flagged"]
        }
    raise HTTPException(status_code=500, detail="Failed to score response")

@app.get("/status")
def get_status():
    """Get AgentWatch system status."""
    return {
        "agentwatch": "running",
        "version": "1.0.0",
        "endpoints": ["/trace", "/score", "/health"],
        "timestamp": time.time()
    }
