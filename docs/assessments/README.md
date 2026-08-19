# Assessments

Point-in-time judgments about the system. **Dated snapshots, never edited after publication.**

An assessment is a claim about a moment. Editing it later destroys the only thing that made it
worth writing — you can no longer say what was true, or known, on that date. Findings that require
a change become changes to the *living* documents; the assessment stands as written, and the next
one of its type references its predecessor and says what moved.

This is the same rule as `FR-501` for *jornada* records, for the same reason: a record that can be
revised is a record nobody has to believe.

## Naming

`YYYY-MM-DD-<type>-<scope>.md` — for example `2026-11-04-security-audit-capture-path.md`.

## Types

| Type | What it asks | Cadence |
|---|---|---|
| `gap-analysis` | Where does the implementation diverge from the PRD? Which requirements have no code, no test, or code that contradicts them? | Before each release; before go-live |
| `security-audit` | Internal review against the threat model, including the customer-as-adversary cases | Quarterly, and after any change to auth, tenancy or the evidentiary path |
| `security-review` | **Third-party** review. Required by `NFR-106` before the first client goes live and annually thereafter | Pre-launch, then annual |
| `compliance-audit` | Do the LFT, IMSS, Infonavit, STPS and LFPDPPP obligations in PRD §10 each still map to something that works? Validated with counsel | Annual, and on any regulatory change |
| `capacity-review` | Where is the system against the stage envelopes in PRD §9.5, and which of the constraints in `NFR-507` is nearest? | Semi-annual, or on crossing a stage |
| `evidentiary-review` | Pick a random historical date. Produce a verification bundle. Have someone outside the team verify it using only the published procedure. Did it work? | Quarterly |
| `dependency-review` | Supply chain: what do we depend on, what would each cost us if it failed or was compromised, and which are unreplaceable? | Semi-annual |

**`evidentiary-review` is the one nobody else runs and the one this product cannot do without.**
The ability to produce a verifiable bundle can decay silently — a schema change, a key rotation, a
retired dependency — and you find out in front of a tribunal. Exercise it on a schedule, from a
cold start, using only what is published.

## Required frontmatter

```markdown
---
type: gap-analysis | security-audit | security-review | compliance-audit |
      capacity-review | evidentiary-review | dependency-review
date: YYYY-MM-DD
scope: what was and was not examined
author: who performed it
method: how — what was read, run, or attempted
supersedes: prior assessment of this type, if any
---
```

## Structure

1. **Scope and method** — including what was deliberately *not* examined. An assessment that does
   not state its boundaries invites the reader to assume it had none.
2. **Findings** — each with severity, evidence, and what it would take to be wrong about it.
3. **Disposition** — for each finding: the `FR-###`/`OQ-###`/issue it became. A finding with no
   disposition is a finding that will be rediscovered next quarter.
4. **What changed since the previous assessment of this type.**

## Rules

1. Never edit a published assessment. Correct it by publishing a new one.
2. Findings never resolve themselves in the document. They resolve in the PRD, an ADR, or the code,
   and the assessment records where.
3. A finding that is accepted rather than fixed is recorded as accepted, with who accepted it and
   why. Silent acceptance is indistinguishable from an oversight six months later.
4. Assessments are evidence about NEO itself. Write them as though a client's auditor will read
   them, because eventually one will.
