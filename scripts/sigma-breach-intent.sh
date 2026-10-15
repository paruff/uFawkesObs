#!/usr/bin/env bash
# scripts/sigma-breach-intent.sh — Stage 6 of the AI-SDLC loop (#602): turns
# firing DORASigmaBandBreach alerts into `intent` issues in the affected repo,
# in the same shape dojo-feedback-intent.sh opens (marker, "intent: " title).
#
# Usage: sigma-breach-intent.sh [--prometheus-url URL | --alerts-file FILE]
#          [--default-owner OWNER] [--dry-run]
#   --alerts-file   Prometheus instant-query JSON (for tests); skips the HTTP call.
#   --dry-run       print "<repo>\t<title>" per breach instead of opening issues.
#
# One issue per (team_id, metric): an open issue carrying the same marker
# suppresses a duplicate. team_id is the affected repo ("owner/repo", or a bare
# "repo" under --default-owner). Fails if Prometheus is unreachable: an
# unreadable alert state must never be read as "no breach".
set -euo pipefail

url="http://localhost:9090"
file=""
owner="${SIGMA_DEFAULT_OWNER:-paruff}"
dry=false
while [ $# -gt 0 ]; do
  case "$1" in
    --prometheus-url)
      url="$2"
      shift 2
      ;;
    --alerts-file)
      file="$2"
      shift 2
      ;;
    --default-owner)
      owner="$2"
      shift 2
      ;;
    --dry-run)
      dry=true
      shift
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

query='ALERTS{alertname="DORASigmaBandBreach",alertstate="firing"}'
if [ -n "$file" ]; then
  json="$(cat "$file")"
else
  json="$(curl -fsS --max-time 10 --get --data-urlencode "query=${query}" "${url}/api/v1/query")"
fi

# team_id arrives via ingested webhooks: accept only a plain repo slug.
rows="$(python3 -c '
import json, re, sys
d = json.load(sys.stdin)
assert d["status"] == "success"
slug = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
for r in d["data"]["result"]:
    m = r["metric"]
    team, metric = m.get("team_id", ""), m.get("metric", "")
    repo = team if "/" in team else sys.argv[1] + "/" + team
    if not (slug.match(repo) and re.fullmatch(r"[a-z0-9_]+", metric)):
        print("skipping unsafe series: %r %r" % (team, metric), file=sys.stderr)
        continue
    print(repo + "\t" + metric)
' "$owner" <<< "$json")"

[ -n "$rows" ] || {
  echo "no sigma-band breaches firing"
  exit 0
}

while IFS=$'\t' read -r repo metric; do
  marker="<!-- sigma-breach: ${repo} ${metric} -->"
  title="intent: ${metric} breached its 3σ band in ${repo}"
  if $dry; then
    printf '%s\t%s\n' "$repo" "$title"
    continue
  fi
  if [ -n "$(gh issue list --repo "$repo" --state open --search "\"sigma-breach: ${repo} ${metric}\" in:body" --json number --jq '.[].number')" ]; then
    echo "open intent issue already exists for ${repo} ${metric}"
    continue
  fi
  body="${marker}
\`${metric}\` for \`${repo}\` has been more than 3σ worse than its own 30-day
mean for 24h (alert \`DORASigmaBandBreach\`, uFawkesObs). That restarts the
AI-SDLC cycle at Plan.

**Next step:** write \`docs/ai-sdlc/<feature>/intent.md\` naming the cause and the
outcome you want, in a PR whose description says \`Closes #<this issue>\`, then
continue with the \`spec\` stage. Humans decide the intent.

_Opened by \`sigma-breach-intent.yml\` (uFawkesObs #602)._"
  gh issue create --repo "$repo" --title "$title" --body "$body" --label intent
done <<< "$rows"
