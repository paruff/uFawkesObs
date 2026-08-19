---
name: pr-review-block
description: Use when opening a pull request in uFawkesObs — provides the required "AI-Assisted Review Block" template every agent-opened PR description must include (AGENTS.md §7).
---

# AI-Assisted Review Block

Every PR opened by an agent in this repo must include this block in its description. `review.md` checks for this literal structure — if you change the headings, update `review.md`'s check to match.

```markdown
## AI-Assisted Review Block

**What does this PR do?**
[...]

**What could go wrong?**
[...]

**What tests cover this change?**
[...]

**Architecture check:**
- What layer(s) were touched and are they correct per §4?
- Any cross-plane impact (uFawkesPipe, uFawkesRes, uFawkesDevX)?

**What I was NOT sure about:**
[...]
```
