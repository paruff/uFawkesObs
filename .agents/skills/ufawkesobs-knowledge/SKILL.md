---
name: ufawkesobs-knowledge
description: Use when searching uFawkesObs institutional knowledge — architecture rationale, ADRs, runbooks, DORA/GitOps/deployment decisions, past incidents, or when an answer should come from this repo's docs rather than its code.
---

# uFawkesObs Knowledge (QMD)

## Overview

This repo has a project-local QMD index (`.qmd/`). **Run every `qmd` command from the repo root** so the project index is picked up. Search for leads, then retrieve full documents before answering — never answer from snippets alone.

## Collections

| Collection | Scope |
|---|---|
| `uFawkesObs-docs` | `docs/**/*.md` |

Not indexed: root docs (`README.md`, `AGENTS.md`, `VISION.md`, `MILESTONES.md`, …) and `.agents/`/`.opencode/` skills — read those files directly.

## Query modes

| Mode | Time | Use for |
|---|---|---|
| `qmd search "..." -n 5` | <1s | **Default.** BM25 keyword search, no LLM |
| `qmd vsearch "..." -n 5` | ~15s | Semantic / paraphrased questions |
| `qmd query "..." --no-rerank -n 5` | ~80s | Hybrid last resort (CPU expansion is slow) |

**Known issue:** plain `qmd query` (rerank enabled) stalls indefinitely on this machine — always pass `--no-rerank`.

## Typical loop

```bash
qmd search "DORA rework rate definition" -n 5   # leads: #docid + snippet
qmd get "#abc123"                               # full doc (line-numbered)
qmd multi-get "#abc123,#def456" --format md     # batch fetch
qmd status                                      # health + pending embeddings
```

## After editing indexed docs

```bash
qmd update && qmd embed -c uFawkesObs-docs      # CPU embed ≈ 8 min for a full pass
```

Deep help: `qmd skills get qmd --full`.
