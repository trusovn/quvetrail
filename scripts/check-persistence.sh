#!/usr/bin/env sh
set -eu

token="foundation-restart-smoke"

docker compose exec -T api node apps/api/dist/foundation-probe.js write "$token"
docker compose restart api
sh scripts/wait-for-health.sh
docker compose exec -T api node apps/api/dist/foundation-probe.js read "$token"
