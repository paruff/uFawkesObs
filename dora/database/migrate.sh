#!/bin/sh
# Applies DORA schema, migrations, and TimescaleDB hypertables against the
# existing DORA_POSTGRES_URL database (owned by uFawkesRes — see AGENTS.md
# §10). Every SQL file here is idempotent (IF NOT EXISTS / IF EXISTS guards),
# so this is safe to re-run on every `docker compose --profile dora up`.
#
# Deliberately does NOT create databases or roles: that's the shared
# Postgres server's own provisioning (uFawkesRes), out of scope here.
set -eu

: "${DORA_POSTGRES_URL:?Set DORA_POSTGRES_URL in .env (see .env.example)}"

apply() {
    echo "Applying $1"
    psql "$DORA_POSTGRES_URL" -v ON_ERROR_STOP=1 -f "$1"
}

apply /migrations/init/01-dora-schema.sql
for f in /migrations/migrations/*.sql; do
    apply "$f"
done
apply /migrations/timescaledb/hypertables.sql

echo "DORA database migration complete."
