# NEO — working agreement

NEO is a multi-tenant Mexican SaaS *reloj checador digital*. The product it actually sells is
**admissible evidence**: a *jornada* record for every worker that survives an STPS inspection or a
challenge before a *tribunal laboral*, under LFT art. 132 fr. XXXIV. Attendance capture is the
mechanism; evidentiary weight is the deliverable.

## Read these before writing anything

1. [`docs/system/prd.md`](docs/system/prd.md) — the approved requirements. Numbered, testable.
2. [`docs/system/adr/README.md`](docs/system/adr/README.md) and the ADRs it indexes — architecture
   decisions. `Accepted` means settled. `Proposed` means awaiting sign-off, so treat it as the
   working assumption and flag if you need it firm.

3. [`docs/README.md`](docs/README.md) — the documentation architecture: where each kind of
   document lives, and which are living documents versus dated, immutable snapshots.

The PRD and the ADRs are the specification. If something is not in them, it is not decided.

**Design sessions additionally read [`docs/prompts/common/`](docs/prompts/common/)** — context,
working method and conventions shared by every design prompt. Task prompts carry only what is
specific to their task.

## Non-negotiable invariants

Violating any of these is a defect regardless of what a task appears to ask for. If a task seems to
require it, stop and say so.

1. **Evidentiary records are append-only.** *Jornada* records, corrections, *listas de asistencia*,
   *movimientos*, wage records, *desviaciones*, overtime authorisations and audit entries have no
   `UPDATE` and no `DELETE` path — not in the application, not in support tooling, not in
   migrations, not in test cleanup. A correction is a new row referencing what it supersedes, and
   both appear in every export. (`FR-501`, `FR-505`, `INV-012`)
2. **Tenant isolation is enforced in the database.** Row-level security, not an application `WHERE`
   clause. Application-layer filtering is never the enforcement point. (`FR-001`, `NFR-201`)
3. **Tenant context is exactly one company, and it is transaction-scoped.** `SET LOCAL`, never
   `SET`. There is no set-valued tenant context. Cross-tenant views are composed from N
   single-tenant queries above the data layer. (ADR-0001 §7, `FR-126`, `INV-001`)
4. **Nothing ever blocks a worker from being recorded.** Not a failed face match, not a missing GPS
   fix, not an exhausted plan capacity, not an unfiled IMSS *alta*, not a delinquent account, not
   an expired session. Every failure path ends in a record — at worst a weaker record class with a
   mandatory *desviación*. (`FR-935`, `FR-944`, `FR-455`, `INV-020`)
5. **Integrity anchors live in NEO's infrastructure for every tenant**, including
   dedicated-database ones. (`INV-003`)
6. **NEO staff never write to an evidentiary record**, break-glass included. (`FR-1205`)
7. **Device-claimed time is never presented as authoritative.** Every offline record carries its
   anchored interval, and the offline gap is disclosed rather than hidden. (`FR-452`)
8. **Biometric templates never leave the tenant boundary**, and raw facial images are not retained
   by default. (`FR-439`, `INV-051`)
9. **Timestamps** are stored in UTC with the originating IANA zone retained; *jornada* is classified
   in the workplace's local zone. (`FR-011`, `FR-012`)
10. **Money** is MXN minor units as integers. No floating-point money anywhere. (`FR-015`)

## Conventions

- **English** for code, identifiers, comments, documentation, commit messages and logs.
- **Spanish (es-MX)** for every string a user reads: UI, notifications, documents, exports.
- **Spanish domain nouns stay Spanish in code and schema** — `registro_patronal`, `jornada`,
  `incidencia`, `movimiento`, `expediente`, `desviacion`, `lista_asistencia`. Do not translate them;
  `employer_registration` invents a term nobody uses and desynchronises the code from the statute
  and the UI.

## Traceability

Every change implements something. Reference the requirement it satisfies (`FR-###`, `NFR-###`,
`INV-###`) in the commit message.

If you need behaviour the PRD does not specify: **raise it and add the requirement to the PRD**,
then implement it. Do not implement unspecified behaviour and leave the spec behind — that is the
failure mode this rule exists to prevent.

If a decision is genuinely open, it is in PRD §13 as an `OQ-###` with options and a recommendation.
**Never resolve an `OQ` silently by picking one in code.** Ask.

## Not yet decided — ask, do not invent

As of this file's last update, these have no ADR and no requirements beyond what the PRD sketches:

- **Identity, authentication, authorization mechanics** — ADR-0010 to 0013 pending. How tenant
  context and persona role reach PostgreSQL is *undecided*; do not invent a session or token model.
- **Database schema and migrations** — PRD §7 is prose. No DDL exists.
- **API surface and the device sync protocol** — undecided.
- **Frontend framework and design system** — ADR-0006 deliberately left the framework open.
- **Testing and telemetry tooling** — see `docs/prompts/prompt_testing_and_telemetry.md`.

> Extend this section as ADRs land, and delete entries as they are decided.

## Gates

| Gate | Status |
|---|---|
| Documentation integrity — no dangling or duplicate requirement identifiers, no ADR index drift (`scripts/check_docs.py`) | **live** |
| Traceability — every non-documentation commit cites a requirement that exists in `prd.md` | specified, not built |
| Database invariants — no `UPDATE`/`DELETE` grants on evidentiary tables (`NFR-944`); every tenant table has RLS enabled *and* policied (`NFR-945`) | specified, blocked on schema |
| Tenant isolation suite, including the delegated cross-tenant path (`NFR-202`, `NFR-206`) | specified, blocked on schema |
| Tamper detection — mutate a *jornada* row directly in the database, assert chain verification catches it (`NFR-943`) | specified, blocked on schema |
| Offline device harness (`NFR-946`), sync burst load test (`NFR-947`), temporal assertions (`NFR-948`) | specified, blocked on schema |

The tamper-detection gate is the most important test in this codebase. It proves the product's
central claim, and it is the one that silently stops mattering the day an `UPDATE` path is added.

**On why most of these are not built yet.** This repository is deliberately design-first: the
specification precedes the implementation, and CI configuration and test tooling are implementation.
Everything above is specified — in `prd.md` §9.9 and in this table — and gets built by the session
that has a schema and an API in front of it, per
[`docs/prompts/prompt_testing_and_telemetry.md`](docs/prompts/prompt_testing_and_telemetry.md).
`check_docs.py` is the exception because it guards the design artifacts themselves, which exist now.

Do not take the current shape of this repository as licence to start implementing. If a task seems
to call for application code, migrations, Terraform or CI configuration and no ADR covers it, stop
and ask.
