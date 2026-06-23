#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"

for _ in $(seq 1 20); do
  curl -s "${BASE_URL}/checkout?dependency_timeout=true" >/dev/null &
done

for _ in $(seq 1 10); do
  curl -s "${BASE_URL}/checkout?fail=500" >/dev/null &
done

for _ in $(seq 1 10); do
  curl -s "${BASE_URL}/checkout?slow=true" >/dev/null &
done

wait
echo "incident traffic generated against ${BASE_URL}"

