# Agent definitions

Subagent definitions for Claude Code. Files here are the mechanism, not documentation of it: each
`*.md` with the right frontmatter becomes an invokable agent in any session opened in this
repository. Source-controlled so that an agent's identity is stable across sessions and machines,
and so that changing one is a reviewable diff rather than a local edit somebody else does not have.

## Format

```markdown
---
name: kebab-case-name
description: when to use this agent — this is what the model matches against, so write it as a
             trigger condition, not as a job title
tools: Read, Grep, Glob        # omit to inherit all
model: opus | sonnet | haiku   # omit to inherit the session model
---

The agent's system prompt. Its identity, what it is responsible for, what it must never do,
and what it should hand back.
```

## Conventions for this repository

1. **Every agent reads `CLAUDE.md` and `docs/prompts/common/` first.** Say so in its prompt. The
   ten invariants and the working method apply to agents exactly as they apply to sessions.
2. **Give read-only agents read-only tools.** An auditor, reviewer or gap-analyst has no reason to
   hold `Edit` or `Write`, and withholding them is cheaper than trusting them not to.
3. **Name what the agent must never do**, not only what it does. For this product that usually
   includes: never resolve an `OQ-###`, never edit a decided ADR, never write to an evidentiary
   record, never widen a tenant context.
4. **One responsibility per agent.** An agent that both finds problems and fixes them will
   under-report, because finding fewer problems is the cheaper path to appearing finished.
5. Create them as the need appears. An unused agent definition is a stale one.

## Likely candidates, when the need arises

`gap-analyst` — PRD versus implementation, read-only, publishes to `docs/assessments/`.
`security-auditor` — threat-model-driven review, read-only.
`evidentiary-verifier` — attempts a cold-start verification bundle check using only published
procedure, read-only. `spec-guardian` — reviews diffs for requirements implemented without a
citation, or behaviour with no requirement.

None exist yet. This file is the convention, not a roster.
