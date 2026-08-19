# Common — conventions

## Language

- **English** — this document, the PRD, ADRs, code, identifiers, comments, commit messages, logs.
- **Spanish (es-MX)** — every string a user reads: UI, notifications, documents, exports.
- **Spanish stays Spanish for legal terms of art**, in prose and in identifiers alike:
  *registro patronal*, *jornada*, *incidencia*, *movimiento*, *expediente*, *desviación*,
  *lista de asistencia*, *prueba plena*. Translating them invents English nobody uses and
  desynchronises the work from both the statute and the UI. PRD §15 is the glossary.
- Italicise Spanish domain terms in prose. Do not italicise them in identifiers.

## Requirement identifiers

| Prefix | Meaning |
|---|---|
| `FR-###` | Functional requirement. Individually testable. |
| `NFR-###` | Non-functional requirement. |
| `INV-###` | Data invariant that must hold at all times. |
| `A-###` | Assumption. If falsified, requirements citing it must be revisited. |
| `OQ-###` | Open question or decision pending. |

A requirement is **defined** by a table row in the PRD that opens with its identifier in backticks.
It is **referenced** by writing the identifier in backticks anywhere. `scripts/check_docs.py`
enforces that every reference resolves and that no identifier is defined twice.

### Reserved ranges

Design sessions run in parallel and all add requirements to `prd.md`. Use **only** your track's
range, and take the next free number *within it* — never "the next free number."

| Track | `FR` | `NFR` | `INV` | `OQ` |
|---|---|---|---|---|
| Identity and security | 1400–1499 | 1000–1099 | 060–069 | 040–049 |
| Process workflows | 1500–1599 | 1100–1199 | 070–079 | 050–059 |
| Testing and telemetry | — | 1200–1299 | 080–089 | 060–069 |

If you must touch a requirement outside your range, **note it in your summary as a conflict**
rather than editing it silently.

## Writing requirements

Each is individually testable as written. "The system is secure" is not a requirement; "no database
role holds `UPDATE` on an evidentiary table" is. Where a requirement depends on an unresolved
decision, cite the `OQ-###` and state the default that applies until it is settled.

## Diagrams

Mermaid only. `stateDiagram-v2` for lifecycles, `sequenceDiagram` for multi-actor flows,
`flowchart` for decision trees, `erDiagram` for entity relationships. Every state machine shows its
failure states — a diagram with only the happy path is the diagram that hides the work.

## ADR format

Filename `NNNN-kebab-case-title.md`, four digits, sequential. Structure:

```
# ADR-NNNN — Title

- **Status:** Accepted | Proposed | Superseded by ADR-NNNN
- **Date:** YYYY-MM-DD
- **Source:** PRD sections, prior decisions
- **Satisfies:** the requirement identifiers this decision serves
- **Related:** other ADRs

## Context      what forced a decision, including the constraints that bind
## Decision     numbered points, stated as decisions and not as discussion
## Consequences Positive / Negative / Neutral — state the negatives honestly
## Alternatives considered   each with why it was rejected
## Revisit triggers          what would reopen this
```

`Accepted` only where the decision follows from something already answered. `Proposed` otherwise.
Add every new ADR to `docs/system/adr/README.md`.

## No filler

If a section has nothing in it, say so and move it to open questions. A section written to look
complete is worse than an admitted gap, because the gap gets fixed and the filler does not.
