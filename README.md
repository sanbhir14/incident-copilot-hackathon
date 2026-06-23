# Incident Copilot Hackathon

POC SRE copilot untuk triage alert 4xx/5xx. Service ini bisa jalan full local untuk demo cepat, lalu dihubungkan ke Datadog MCP/API dan Amazon Bedrock saat credentials siap.

## Target Demo

1. Demo app menghasilkan 5xx/latency spike.
2. Datadog menangkap metric/log/APM.
3. Incident Copilot mengambil evidence dari Datadog.
4. Bedrock membuat incident analysis berbasis evidence.
5. Dashboard menampilkan observability untuk app dan AI workflow.

## Repo Layout

```text
.
├── app/
│   ├── bedrock.py          # Bedrock invoke + fallback deterministic
│   ├── datadog_client.py   # Datadog evidence fetch + synthetic fallback
│   ├── main.py             # FastAPI app and endpoints
│   ├── metrics.py          # lightweight DogStatsD sender
│   ├── prompts.py          # incident prompt
│   └── scenarios.py        # scripted incident fixtures
├── scripts/
│   └── fire_incident.sh    # generate 5xx/slow requests
├── terraform/              # optional EC2 skeleton
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Quick Start Local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8080
```

Trigger incident:

```bash
./scripts/fire_incident.sh http://localhost:8080
curl -s http://localhost:8080/incident/demo | jq
```

## Important Endpoints

- `GET /health`
- `GET /checkout`
- `GET /checkout?fail=500`
- `GET /checkout?slow=true`
- `GET /checkout?dependency_timeout=true`
- `POST /incident/analyze`
- `GET /incident/demo`

Example analyze request:

```bash
curl -s -X POST http://localhost:8080/incident/analyze \
  -H 'content-type: application/json' \
  -d '{
    "service": "checkout-api",
    "alert_name": "checkout-api 5xx spike",
    "time_window_minutes": 15,
    "severity_hint": "P2"
  }' | jq
```

## AWS / Bedrock

Untuk hackathon, pakai Bedrock on-demand saja. Jangan pakai provisioned throughput, Knowledge Base, RDS, OpenSearch, atau NAT Gateway.

Minimal env:

```bash
USE_BEDROCK=true
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
```

IAM minimum:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "*"
    }
  ]
}
```

## Datadog

POC ini bisa tetap jalan tanpa Datadog key karena `datadog_client.py` akan memakai synthetic evidence. Saat key siap:

```bash
DATADOG_SITE=datadoghq.com
DD_API_KEY=...
DD_APP_KEY=...
DD_AGENT_HOST=127.0.0.1
DD_DOGSTATSD_PORT=8125
```

Dashboard yang perlu dibuat:

- App error rate, 4xx, 5xx.
- App p95 latency.
- Top logs by service.
- Copilot analysis count.
- Bedrock call count.
- Bedrock latency.
- Datadog evidence fetch latency.
- Confidence score.
- User feedback score.

## Perlu Terraform?

Untuk 4 jam dan credit USD 50: **tidak wajib**. Jalur terbaik:

1. Jalan local atau 1 EC2 kecil.
2. Manual setup Datadog Agent.
3. Bedrock pakai IAM user/role yang sudah ada.
4. Terraform hanya dipakai kalau perlu reproducibility untuk EC2 + IAM.

Terraform di folder ini hanya skeleton optional. Jangan deploy kalau waktu mepet.

## Demo Script

Narasi singkat:

1. "Checkout API mengalami 5xx spike dan latency naik."
2. Buka Datadog dashboard: terlihat error rate, latency, logs.
3. Trigger `GET /incident/demo`.
4. Tampilkan hasil:
   - severity
   - suspected cause
   - evidence
   - owner
   - next actions
   - draft postmortem
5. Tunjukkan dashboard AI observability: Bedrock call, latency, confidence, feedback.

