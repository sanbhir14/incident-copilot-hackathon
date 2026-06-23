import random
import time
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from app.bedrock import BedrockIncidentAnalyzer
from app.datadog_client import DatadogEvidenceClient
from app.metrics import metrics, timed_metric

app = FastAPI(title="Incident Copilot Hackathon")
datadog = DatadogEvidenceClient()
analyzer = BedrockIncidentAnalyzer()


class AnalyzeIncidentRequest(BaseModel):
    service: str = Field(default="checkout-api")
    alert_name: str = Field(default="checkout-api 5xx spike")
    time_window_minutes: int = Field(default=15, ge=1, le=120)
    severity_hint: Literal["P1", "P2", "P3", "P4"] | None = "P2"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/checkout")
def checkout(
    fail: int | None = Query(default=None),
    slow: bool = Query(default=False),
    dependency_timeout: bool = Query(default=False),
) -> dict:
    tags = ["service:checkout-api"]
    metrics.increment("checkout.request.count", tags=tags)

    if slow:
        time.sleep(1.2)
        metrics.increment("checkout.slow.count", tags=tags)

    if dependency_timeout:
        time.sleep(1.8)
        metrics.increment("checkout.dependency_timeout.count", tags=tags)
        metrics.increment("checkout.response.5xx", tags=tags)
        return {
            "status": "error",
            "error": "payment-service timeout",
            "dependency": "payment-service",
        }

    if fail:
        metric_name = "checkout.response.5xx" if fail >= 500 else "checkout.response.4xx"
        metrics.increment(metric_name, tags=tags)
        return {"status": "error", "code": fail, "request_id": f"demo-{random.randint(1000, 9999)}"}

    metrics.increment("checkout.response.2xx", tags=tags)
    return {"status": "ok", "order_id": f"ord-{random.randint(10000, 99999)}"}


@app.post("/incident/analyze")
def analyze_incident(request: AnalyzeIncidentRequest) -> dict:
    with timed_metric("copilot.datadog_evidence.latency_ms", ["service:incident-copilot"]):
        evidence = datadog.collect_evidence(request.service, request.time_window_minutes)

    incident = {
        "alert_name": request.alert_name,
        "service": request.service,
        "time_window_minutes": request.time_window_minutes,
        "severity_hint": request.severity_hint,
        "evidence": evidence,
    }

    with timed_metric("copilot.bedrock.latency_ms", ["service:incident-copilot"]):
        analysis = analyzer.analyze(incident)

    metrics.increment("copilot.analysis.count", tags=["service:incident-copilot"])
    metrics.gauge("copilot.confidence_score", analysis.get("confidence_score", 0), ["service:incident-copilot"])

    return {
        "incident": incident,
        "analysis": analysis,
    }


@app.get("/incident/demo")
def demo_incident() -> dict:
    request = AnalyzeIncidentRequest(
        service="checkout-api",
        alert_name="checkout-api 5xx spike and p95 latency regression",
        time_window_minutes=15,
        severity_hint="P2",
    )
    return analyze_incident(request)

