SYSTEM_PROMPT = """You are an SRE incident copilot.

Rules:
- Use only evidence provided in the incident payload.
- If evidence is insufficient, say "insufficient evidence".
- Do not invent deployments, owners, dependencies, or timelines.
- Every suspected cause must reference evidence.
- Return valid JSON only.
"""


def build_incident_prompt(payload: dict) -> str:
    return f"""Analyze this incident and return JSON with these fields:
- severity
- suspected_cause
- evidence
- customer_impact
- suggested_owner
- next_actions
- draft_status_update
- draft_postmortem
- confidence_score
- unsupported_claims

Incident payload:
{payload}
"""

