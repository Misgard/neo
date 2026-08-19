# Common — context

*Every design session reads this file, `01-method.md` and `02-conventions.md` before its task
prompt. They carry what applies to all design work in this repository; the task prompt carries
only what is specific to its task.*

## What NEO is

A multi-tenant Mexican SaaS *reloj checador digital*. The product it actually sells is **admissible
evidence**: a *jornada* record for every worker that survives an STPS inspection or a challenge
before a *tribunal laboral*, under LFT art. 132 fr. XXXIV. Attendance capture is the mechanism;
evidentiary weight is the deliverable.

Its first clients are construction companies, whose sites impose the binding constraints — no
connectivity, no durable hardware, damaged fingerprints, few phones, and a hiring practice where
people work before any paperwork exists.

Two properties make its design unusual, and most standard patterns fail on one or both:

- **The threat model includes the paying customer.** The party with the strongest motive to alter
  a *jornada* record is the *patrón*. See PRD §2.3.
- **Nothing may ever block a worker from being recorded.** Not a failed match, not an exhausted
  plan, not a delinquent account, not an expired session. Every failure path ends in a record.

## Read before writing

1. `CLAUDE.md` — the working agreement. Auto-loaded, but read it deliberately: the ten invariants
   there are non-negotiable and several are easy to violate by accident.
2. `docs/system/prd.md` — the specification. Numbered, testable, and the source everything derives
   from.
3. `docs/system/adr/README.md` and the ADRs it indexes — decisions already made.
4. `docs/README.md` — where documents go and which are living versus snapshots.
5. Whatever design artifacts your task prompt names.

## This repository is design-first

Specification precedes implementation. Application code, migrations, Terraform and CI
configuration are written by the sessions that have a schema and an API in front of them, not by
design sessions. If your task appears to call for them and no ADR covers it, stop and ask.
