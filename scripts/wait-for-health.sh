#!/usr/bin/env sh
set -eu

api_url="${API_URL:-http://localhost:3000}/health"
web_url="${WEB_URL:-http://localhost:4173}"
attempt=1

while [ "$attempt" -le 30 ]; do
  if curl --fail --silent --show-error "$api_url" >/dev/null 2>&1 && \
     curl --fail --silent --show-error "$web_url" >/dev/null 2>&1; then
    echo "QuVeTrail is ready: $web_url (API: $api_url)"
    exit 0
  fi
  sleep 2
  attempt=$((attempt + 1))
done

echo "QuVeTrail did not become ready within 60 seconds" >&2
docker compose ps >&2
docker compose logs --tail=100 >&2
exit 1
