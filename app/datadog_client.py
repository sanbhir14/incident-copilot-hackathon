import os
from datetime import datetime, timezone

import requests

from app.scenarios import checkout_dependency_timeout


class DatadogEvidenceClient:
    def __init__(self) -> None:
        self.site = os.getenv("DATADOG_SITE", "datadoghq.com")
        self.api_key = os.getenv("DD_API_KEY")
        self.app_key = os.getenv("DD_APP_KEY")

    def collect_evidence(self, service: str, time_window_minutes: int) -> dict:
        if not self.api_key or not self.app_key:
            evidence = checkout_dependency_timeout()
            evidence["source"] = "synthetic"
            return evidence

        headers = {
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key,
        }

        # Keep the hackathon implementation intentionally narrow.
        # Datadog MCP can replace this with richer metrics/logs/traces tool calls.
        now = int(datetime.now(timezone.utc).timestamp())
        start = now - (time_window_minutes * 60)
        query = f"service:{service} status:error"
        logs_url = f"https://api.{self.site}/api/v2/logs/events/search"
        response = requests.post(
            logs_url,
            headers=headers,
            json={
                "filter": {
                    "from": datetime.fromtimestamp(start, timezone.utc).isoformat(),
                    "to": datetime.fromtimestamp(now, timezone.utc).isoformat(),
                    "query": query,
                },
                "page": {"limit": 10},
            },
            timeout=8,
        )
        response.raise_for_status()

        return {
            "source": "datadog_api",
            "service": service,
            "time_window_minutes": time_window_minutes,
            "logs": response.json().get("data", []),
            "metrics": {
                "note": "replace with Datadog MCP metrics query during hackathon",
            },
            "traces": {
                "note": "replace with Datadog MCP trace query during hackathon",
            },
        }

