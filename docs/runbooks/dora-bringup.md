# DORA bring-up (no GitHub runner needed)

Gets the DORA dashboards populated from GitHub history. Run on the NAS first,
then from your Mac. Commands marked ⚠ have not been run end to end.

## 1. Start dora-api on the NAS

```sh
ssh 192.168.1.10
cd /var/services/homes/philaruff/uFawkesObs
git fetch origin && git checkout --detach origin/main
docker compose -f compose.drill.yaml -f compose.drill-user.yaml \
  --profile core --profile dora up -d --build        # ⚠ dora-api under user 1026:100
curl -s localhost:8088/health                          # {"status":"ok","queue_depth":0}
```

`compose.drill*.yaml` are the host-local overrides (Grafana on 3001, services run
as the NAS user). Add `dora-api: user: "1026:100"` to `compose.drill-user.yaml` if missing.

## 2. Reach it from the Mac

dora-api listens on the NAS loopback only. Open a tunnel and leave it running:

```sh
ssh -N -L 8088:127.0.0.1:8088 192.168.1.10
```

## 3. Dry-run, then post the backfill (new terminal)

```sh
cd uFawkesObs && git pull
scripts/backfill_dora_from_github.py paruff/uFawkesObs | head -3     # dry-run
scripts/backfill_dora_from_github.py --post http://localhost:8088 \
  paruff/uFawkesObs paruff/uFawkesPipe paruff/uFawkesDevX paruff/uFawkesDojo \
  paruff/uFawkesAI paruff/uFawkes.dev paruff/fawkes
```

If `DORA_API_KEY` is set on dora-api, export it first. A 40-PR/day cap warning
means that day was truncated.

## 4. Check

```sh
curl -s localhost:8088/metrics | grep '^dora_'     # gauges per repo (team_id)
```

Then Grafana (http://192.168.1.10:3001) → DORA dashboards. dora-api recomputes
on `DORA_COMPUTE_INTERVAL_SECONDS` (default 3600) — lower it in `.env` and restart
to see data sooner. Prometheus must scrape `dora-api:8088` (job `dora-api`).

## Limits

- dora-api windows on ingest time, so a backfill only represents the last 30 days
  and FDRT is not meaningful for it.
- Live feed from each repo's workflows still needs a runner or a reachable endpoint.
