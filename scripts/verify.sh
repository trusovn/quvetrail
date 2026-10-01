#!/usr/bin/env sh
set -eu

cleanup() {
  docker compose down
}
trap cleanup EXIT INT TERM

pnpm check
sh scripts/start.sh
pnpm test:api
pnpm test:e2e
sh scripts/check-persistence.sh
