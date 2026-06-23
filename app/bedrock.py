import json
import os
import time
from typing import Any

import boto3

from app.prompts import SYSTEM_PROMPT, build_incident_prompt


class BedrockIncidentAnalyzer:
    def __init__(self) -> None:
        self.enabled = os.getenv("USE_BEDROCK", "false").lower() == "true"
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")

    def analyze(self, incident: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return self._fallback_analysis(incident)

        client = boto3.client("bedrock-runtime", region_name=self.region)
        prompt = build_incident_prompt(incident)
        started_at = time.perf_counter()

        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}],
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1200,
                "temperature": 0.1,
                "topP": 0.9,
            },
        }

        response = client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            accept="application/json",
            contentType="application/json",
        )
        raw = json.loads(response["body"].read())
        text = raw["output"]["message"]["content"][0]["text"]
        result = json.loads(text)
        result["bedrock_model_id"] = self.model_id
        result["bedrock_latency_ms"] = round((time.perf_counter() - started_at) * 1000, 2)
        return result

    def _fallback_analysis(self, incident: dict[str, Any]) -> dict[str, Any]:
        evidence = incident.get("evidence", {})
        metrics = evidence.get("metrics", {})
        logs = evidence.get("logs", [])
        traces = evidence.get("traces", [])

        return {
            "severity": incident.get("severity_hint") or "P2",
            "suspected_cause": "checkout-api is likely impacted by payment-service dependency timeout.",
            "evidence": [
                f"5xx error rate is {metrics.get('error_rate_5xx_percent', 'unknown')}%.",
                f"p95 latency is {metrics.get('latency_p95_ms', 'unknown')} ms.",
                f"error log sample: {logs[0].get('message') if logs else 'insufficient evidence'}.",
                f"slow trace sample: {traces[0].get('slow_span') if traces else 'insufficient evidence'}.",
            ],
            "customer_impact": "Checkout requests may fail or take longer than usual.",
            "suggested_owner": evidence.get("known_context", {}).get("owner_mapping", "insufficient evidence"),
            "next_actions": [
                "Check payment-service health and timeout/error metrics.",
                "Verify whether checkout retry policy is amplifying latency.",
                "Prepare rollback or circuit breaker if payment-service remains unhealthy.",
            ],
            "draft_status_update": "We are investigating elevated checkout-api 5xx and latency. Current evidence points to payment-service timeout during charge requests.",
            "draft_postmortem": "Summary: checkout-api experienced elevated 5xx and p95 latency. Evidence shows timeout errors while calling payment-service /payment/charge. Impact: checkout failures and slow responses. Follow-ups: review dependency timeout settings, add circuit breaker, and improve alert runbook.",
            "confidence_score": 0.84,
            "unsupported_claims": [],
            "bedrock_model_id": "fallback",
            "bedrock_latency_ms": 0,
        }

