# NEO documentation architecture

Two kinds of document live here, and the distinction governs everything else.

**Living documents** are edited in place and are always current. The PRD, the ADRs, design
documents, module documentation and runbooks. Their history lives in git; the file itself
reflects today.

**Dated snapshots** are written once and never edited after publication. Audits, gap analyses,
security reviews, capacity reviews. An audit that gets updated is not an audit — it is a claim
about a moment, and editing it destroys the thing that made it worth writing. Findings that
require a change become changes to the *living* documents; the snapshot stands as written and the
next one references it.

That is the same principle as the product's own evidentiary design (`FR-501`), for the same
reason.

## Map

```
docs/
  system/            specification and design — living
    prd.md             requirements. The source everything derives from
    adr/               architecture decisions, one per decision
    threat-model.md    adversaries, controls and residual risk — living
    workflows/         process and state machines, one file per domain
    screens.md         screen inventory per persona and form factor
    data-model.md      schema design (pending)
    api/               API and sync protocol contracts (pending)
    modules/           one document per subsystem, written as each is built
    testing.md         how to run and extend the suites (pending)
  operations/        runbooks, incident response, on-call — living (created when there is
                     something to operate)
  assessments/       dated, immutable snapshots. See assessments/README.md
  compliance/        evidence NEO must be able to produce about itself: aviso de privacidad
                     versions, encargado clauses, PSC agreements, third-party review reports
                     (created when the first such artifact exists)
  prompts/
    common/          instructions every design session reads
    prompt_*.md      one per design session
CLAUDE.md            always-on working agreement, auto-loaded every session
.claude/agents/      agent definitions. See that directory's README
scripts/             tooling that guards the documents themselves
```

Directories marked *pending* or *created when* do not exist yet. Empty scaffolding is noise; a
directory appears when it has content.

## Where a given thing goes

| You are writing | It goes | Class |
|---|---|---|
| A requirement | `system/prd.md`, numbered | living |
| Why we chose X over Y | `system/adr/NNNN-*.md` | living |
| How a subsystem works, for whoever maintains it | `system/modules/<name>.md` | living |
| How to respond when something breaks | `operations/` | living |
| What is true about the system as of a date | `assessments/` | **snapshot** |
| A document a client or auditor may demand of us | `compliance/` | evidence |
| Instructions for a future design session | `prompts/` | living |

## Rules

1. **A requirement lives in exactly one place: the PRD.** Design documents and module docs
   reference `FR-###`; they never restate a requirement in their own words, because a restatement
   is a second source of truth that will drift.
2. **An `Accepted` ADR is never edited to change its decision.** Correct a typo, yes. Change what
   was decided — write a new ADR that supersedes it and say so in both.

   **A `Proposed` ADR is a draft and is edited in place.** It has not been signed off, so there is
   no decision to overturn and nothing downstream relies on it. Bump its date so the amendment is
   visible. The distinction is the point of the status field: `Proposed` invites correction,
   `Accepted` demands a successor.
3. **Assessments are never edited after publication.** See `assessments/README.md`.
4. **Anything unresolved is an `OQ-###` in PRD §13** with options and a recommendation. Not a
   `TODO`, not a comment, not a note in a design doc.
5. **Module documentation is written with the module, not after.** A module without a document is
   incomplete, the same way a module without tests is.
