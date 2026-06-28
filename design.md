# Design — M2-03: Publish and Verify Platform Documentation

**Based on:** specification.md (M2-03), plan.md

---

## Impacted Components

| Component | File | Change Type |
|---|---|---|
| Change impact map | `docs/CHANGE_IMPACT_MAP.md` | **Fix** — stale path `config/prometheus/ai-rules.yml` → `config/prometheus/rules/ai-rules.yml` |
| Architecture | `docs/ARCHITECTURE.md` | **Verify** — already synced in M1.5, confirm correct |
| Known limitations | `docs/KNOWN_LIMITATIONS.md` | **Verify** — comprehensive, confirm correct |

---

## Technical Approach

### 1. Verify ARCHITECTURE.md

The doc was already synced in M1.5 (PR #125) with correct versions, ports, and config
paths. Run `markdownlint` to validate. If it passes, no changes needed.

### 2. Verify KNOWN_LIMITATIONS.md

The doc is 186 lines with 12 documented limitations across 7 categories. It already
covers all required topics. Run `markdownlint` to validate. If it passes, no changes
needed.

### 3. Fix CHANGE_IMPACT_MAP.md

Line 53 references `config/prometheus/ai-rules.yml` which does not exist at that path.
The file was moved to `config/prometheus/rules/ai-rules.yml` in PR #124.

Change:
```
| `config/prometheus/ai-rules.yml`                             | Grafana AI capabilities dashboard panels that reference `ai:*` recording rules; `docs/ai-runbook.md`                   |
```
To:
```
| `config/prometheus/rules/ai-rules.yml`                       | Grafana AI capabilities dashboard panels that reference `ai:*` recording rules; `docs/ai-runbook.md`                   |
```

Also verify all other file paths resolve by checking against filesystem.

---

## Constraints

1. All three docs must pass markdownlint
2. No new limitations should be added unless they represent actual known issues
3. No architecture changes should be introduced — verification only
