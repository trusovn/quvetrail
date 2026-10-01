#!/usr/bin/env sh
set -eu

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.example to .env before starting QuVeTrail." >&2
  exit 1
fi

docker compose up --build --detach
sh scripts/wait-for-health.sh
