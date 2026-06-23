import json

from mcp.server.fastmcp import FastMCP

from app.datadog_client import DatadogEvidenceClient

mcp = FastMCP("datadog-incident-copilot")
datadog = DatadogEvidenceClient()


@mcp.tool()
def collect_incident_evidence(service: str = "checkout-api", time_window_minutes: int = 15) -> str:
    """Collect incident evidence for a service from Datadog or synthetic demo data."""
    evidence = datadog.collect_evidence(service, time_window_minutes)
    return json.dumps(evidence, indent=2, default=str)


@mcp.tool()
def search_error_logs(service: str = "checkout-api", time_window_minutes: int = 15) -> str:
    """Search recent error logs for a service."""
    evidence = datadog.collect_evidence(service, time_window_minutes)
    return json.dumps(
        {
            "source": evidence.get("source"),
            "service": service,
            "time_window_minutes": time_window_minutes,
            "logs": evidence.get("logs", []),
        },
        indent=2,
        default=str,
    )


@mcp.tool()
def query_service_metrics(service: str = "checkout-api", time_window_minutes: int = 15) -> str:
    """Query high-level service metrics used for incident triage."""
    evidence = datadog.collect_evidence(service, time_window_minutes)
    return json.dumps(
        {
            "source": evidence.get("source"),
            "service": service,
            "time_window_minutes": time_window_minutes,
            "metrics": evidence.get("metrics", {}),
        },
        indent=2,
        default=str,
    )


if __name__ == "__main__":
    mcp.run()
