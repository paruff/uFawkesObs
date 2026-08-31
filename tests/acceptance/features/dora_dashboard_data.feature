@full
Feature: DORA dashboard panels have real data (not just provisioned)
  Existing dashboard-provisioning checks only verify a dashboard's UID is
  registered in Grafana — never that its panel queries return real data.
  That gap let dora-overview.json go blank ("No data" on every panel)
  without any acceptance test catching it. These scenarios close that gap
  for the DORA-branded dashboards specifically.

  Background:
    Given the core observability stack is running
    And a real DORA deployment event has been sent

  @dora
  Scenario: DORA Overview ("DORA 2025 framework") shows real data
    # #267: Lead Time and FDRT used to have zero data anywhere in
    # Prometheus. Root cause was two-fold, not "needs incident data" as
    # first assumed: (1) deploy.yml never emitted any deployment event at
    # all, and (2) deployment-event.schema.json's additionalProperties:
    # false rejected the pr_merged_at/first_commit_at fields Lead Time
    # reads, and FDRT only ever needed a failed->success deployment gap
    # for the same source (dora/compute/metrics_db_sqlite.py's fdrt()) —
    # not incident events. Both are now genuinely fed: deploy.yml sends a
    # real event on every deploy/rollback outcome, and the Background step
    # above seeds a failed->success pair with pr_merged_at.
    Then the dashboard "ufawkesobs-dora-overview" panels should return real, labeled data

  @dora
  Scenario: DORA Metrics ("DORA 2026 — Five Key Metrics") shows data
    # #266: the recording rules behind this dashboard used to query a
    # never-fed OTel-native pipeline; now repointed at the same
    # dora-compute/Pushgateway data dora-overview.json uses (see
    # config/prometheus/rules/ufawkesobs-dora-metrics.yml). This dashboard
    # has no team_id variable — its recording rules are org-wide
    # avg()/sum() aggregates by design, which strips labels even when
    # genuinely fed. That makes the stricter "real, labeled data" step
    # unusable here (a correct org-wide "0.2" and a masked "0" fallback
    # are shaped identically) — this uses the weaker non-empty check
    # instead, which only proves the queries are wired correctly.
    Then the dashboard "ufawkesobs-dora-metrics" panels should return non-empty data

  # No dashboard named "DORA AI report" or "DORA 2026 ROI report" exists in
  # this repo (confirmed: zero "ROI" mentions anywhere in dashboards/,
  # docs/dora/, or docs/product/). The closest match to an "AI" dashboard is
  # dashboards/platform/ai-capabilities.json (uid: platform-ai-capabilities),
  # which isn't DORA-branded and doesn't share the dora-compute pipeline this
  # feature file targets — it's covered by its own existing acceptance
  # coverage, not duplicated here. If a DORA-specific AI or ROI dashboard is
  # wanted, it needs to be designed and built first; this feature file has
  # the reusable step ("the dashboard ... panels should return real, labeled
  # data") ready to cover it once it exists.
