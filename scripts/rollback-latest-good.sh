#!/usr/bin/env bash
# Roll the deploy host's checkout back to the deploy-latest-good tag.
# Runs ON the host (cfr-rollback.yml pipes it over ssh). Read-only from git's
# perspective: fetch + checkout, never a push or revert (#182).
# Exit 0 = rolled back or already there; 3 = no deploy-latest-good tag.
set -euo pipefail

cd "${REPO_DIR:?REPO_DIR must be set}"
git fetch --tags --force origin

if ! git rev-parse -q --verify refs/tags/deploy-latest-good > /dev/null; then
  echo "No deploy-latest-good tag: no verified deploy to return to." >&2
  exit 3
fi

# Already on the known-good revision: rolling back again would loop on a
# still-firing alert without changing anything.
if [ "$(git rev-parse HEAD)" = "$(git rev-parse 'deploy-latest-good^{commit}')" ]; then
  echo "Already at deploy-latest-good; nothing to do."
  exit 0
fi

git checkout --detach deploy-latest-good
./scripts/check-env.sh
docker compose --profile core up -d
./scripts/wait-healthy.sh

DORA_SERVICE="ufawkesobs" DORA_ENVIRONMENT="production" DORA_STATUS="success" \
  DORA_COMMIT_SHA="$(git rev-parse HEAD)" ./scripts/send-dora-deployment-event.sh
