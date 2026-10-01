#!/usr/bin/env sh
set -eu

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.example to .env before resetting QuVeTrail." >&2
  exit 1
fi

echo "Removing the local QuVeTrail PostgreSQL volume and recreating the system"
docker compose down --volumes
sh scripts/start.sh
