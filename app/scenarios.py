from datetime import datetime, timezone


def checkout_dependency_timeout() -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "service": "checkout-api",
            "error_rate_5xx_percent": 18.7,
            "error_rate_4xx_percent": 1.2,
            "latency_p95_ms": 2400,
            "latency_baseline_p95_ms": 320,
            "request_rate_per_minute": 220,
        },
        "logs": [
            {
                "level": "error",
                "message": "dependency timeout calling payment-service /payment/charge",
                "count": 73,
            },
            {
                "level": "warn",
                "message": "retry budget exhausted for payment-service",
                "count": 41,
            },
        ],
        "traces": [
            {
                "trace_id": "demo-trace-001",
                "slow_span": "POST /payment/charge",
                "duration_ms": 2100,
                "error": "upstream timeout",
            }
        ],
        "known_context": {
            "recent_deploy": "insufficient evidence",
            "owner_mapping": "checkout-api -> backend/checkout",
        },
    }

