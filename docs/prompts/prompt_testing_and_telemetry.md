# Prompt — NEO testing strategy and telemetry architecture

> **Run this after the schema and API exist.** You cannot design a test strategy for interfaces
> that have not been defined. If `docs/system/adr/0010`–`0013` are not written and no schema or
> migrations exist in the repository, stop and say so rather than designing against assumptions.

## 0. Role and mission

You are the **lead system architect** for NEO, continuing work already in progress.

**Read first:** `CLAUDE.md`, then `docs/system/prd.md` — especially §9.6 (observability), §9.7
(cost targets) and §9.9 (verifiability and release gates) — then `docs/system/adr/README.md` and
every ADR, then whatever schema, migrations and API definitions exist.

**Hard rule on uncertainty:** if a decision is required and the information is not in those
documents, do not invent it. Stop and ask, with at least two options, the trade-off of each, and
your recommendation. Separate *blocking* from *non-blocking* questions and ask the blocking ones
before writing.

**Do not re-open a decided ADR.** If one is wrong, name it and propose superseding it.

---

## 1. What already exists, and what you are adding

**One gate is implemented**: `scripts/check_docs.py`, which guards the design documents against
dangling or duplicate requirement identifiers and ADR index drift. It exists because the design
artifacts exist.

**Everything else is specified and deliberately unbuilt**, because this repository is design-first
and test tooling is implementation. You are the session that builds them:

| Gate | Specification |
|---|---|
| Traceability | Every commit touching anything outside `docs/`, `CLAUDE.md` and `README.md` must cite an `FR-`/`NFR-`/`INV-` identifier that exists in `prd.md`. A commit citing nothing, or citing an identifier that does not exist, fails. This is what keeps an implementation anchored to the specification; behaviour no requirement describes is either a defect or a missing requirement. |
| Database invariants | `NFR-944` — no database role holds `UPDATE` or `DELETE` on an evidentiary table (`jornada`, `lista_asistencia`, `movimiento`, `archivo_idse`, `salario`, `desviacion`, overtime authorisations, `audit_log`), asserted against the live schema via `information_schema.role_table_grants`. `NFR-945` — every table carrying a company identifier has row-level security enabled *and* at least one policy; RLS without a policy and a policy without RLS are both silent defects. |
| Tenant isolation | `NFR-202`, `NFR-206` — including the delegated cross-tenant path, which generic isolation tests do not cover. |
| Tamper detection | `NFR-943` — the most important test in the codebase. |
| Offline harness, burst load, temporal assertions | `NFR-946`, `NFR-947`, `NFR-948`. |

**CI configuration is yours to write.** None exists. Decide the platform, what runs on every push
versus nightly, and the runtime budget (§2.4).

Observability is specified in `NFR-601`–`NFR-609`. No tooling has been chosen.

You are producing the strategy that turns those requirements into an implemented system, and the
technology decisions they imply.

---

## 2. Testing strategy — what makes this project unusual

Do not produce a generic test pyramid. Three properties make NEO's testing problem specific, and
the strategy must be built around them.

### 2.1 The product's central claim is falsifiable, so test it as such

NEO sells tamper-evidence. That is not a feature to unit-test; it is a claim that must survive
active attack. The strategy must include **adversarial tests written from the threat model** (PRD
§2.3, `docs/system/threat-model.md`), where the attacker is the paying customer:

- Mutate a *jornada* row directly in the database and assert the chain breaks and alerts
  (`NFR-943`).
- Attempt to grant `UPDATE` on an evidentiary table and assert the gate fails the build
  (`NFR-944`).
- Replay a device batch, reorder it, drop a record from the middle, and assert each is detected.
- Present a record whose device-claimed time falls outside its anchored interval and assert the
  integrity flag and the alert.
- Forge a device signature with a key not enrolled and assert rejection.
- Reach a tenant through a revoked cross-tenant grant and assert denial (`NFR-206`).

Decide where these live, how often they run, and which are release gates versus scheduled.

### 2.2 The hardest surface to test is offline and on someone else's hardware

The capture application runs for days without connectivity on low-end devices at remote sites. The
strategy must cover: the offline harness in `NFR-946`; device-farm or emulator strategy and which
real devices are in the supported matrix (ADR-0004 `FR-480`); how face matching and liveness are
tested without shipping real biometric data into CI; and how a released mobile build is validated
when the fix cycle is days rather than minutes because of app-store review (ADR-0006).

### 2.3 Correctness is temporal

Most defects in this system will be "what was true on date D" defects. Decide how the temporal
model is tested (`NFR-948`), how fixtures representing a year of employment history are built and
maintained, and whether property-based testing earns its place for the interval invariants
(`INV-021`, `INV-022`, `INV-026`).

### 2.4 Also decide

Test taxonomy and where the boundaries sit; frameworks; how RLS is tested (application-level tests
under a tenant role, not as a superuser, or the tests prove nothing); how migrations are tested,
including reversibility and the multi-database fan-out for dedicated tenants (`NFR-203`); fixture
and factory strategy; what coverage means here and where a number is meaningful versus theatre;
CI runtime budget and what runs on every push versus nightly; and how the IDSE golden-file suite
(`FR-628`) is maintained as IMSS layouts drift.

---

## 3. Telemetry architecture

### 3.1 Constraints first

Cost is binding. `NFR-901` caps infrastructure at 15% of gross subscription revenue and `NFR-608`
counts observability inside it. Per-host and per-ingested-gigabyte pricing models are the ones most
likely to break that ceiling at launch volume. **Quantify the monthly cost of each candidate at the
launch envelope and at the 18-month envelope before recommending one.**

`NFR-605` forbids personal data in logs, metrics and traces. That is a design constraint on
instrumentation, not a review checklist item — decide how it is enforced rather than hoped for.

### 3.2 Decide

- Logs, metrics and traces: managed platform, the cloud provider's native stack, or self-hosted.
  Cost, operational burden and data residency (`OQ-025`) all bear on this.
- Correlation by request and by tenant without leaking tenant identity into a shared plane.
- **Mobile crash and error telemetry** (`NFR-607`) — the gap that matters most, because the
  application runs offline for days and a crash at a remote *obra* is otherwise invisible or lost
  entirely. Decide buffering, upload-at-sync, payload scrubbing and retention.
- Evidence-system telemetry as a first-class signal: record-class distribution, integrity flag
  rate, *desviación* rate per supervisor and per site, chain verification lag, anchoring lag.
  These are already partly required (`FR-413`, `FR-1339`, `NFR-602`, `NFR-603`); decide how they
  are surfaced and to whom, respecting `FR-952`.
- Alerting on the telemetry itself, and what pages a human at this team size.
- Retention per signal class, and its cost.

---

## 4. Out of scope

- Re-opening decided ADRs.
- Product analytics for marketing purposes.
- The client-facing alerting subsystem in PRD §6.8, which is a product feature, not telemetry.
  Its *health* monitoring (`NFR-604`) is in scope; its behaviour is not.
- Anything fenced out in PRD §14.

---

## 5. Deliverables

1. `docs/system/adr/0014-testing-strategy.md`
2. `docs/system/adr/0015-telemetry-and-observability.md`
3. `docs/system/testing.md` — the practical guide: how to run the suites, how to add a test to each
   layer, how fixtures work, what the gates are and what to do when one fails.
4. Implement the gates that are specified but not built, or state explicitly which you are deferring
   and why.
5. Update `docs/system/adr/README.md`, and update the gates table in `CLAUDE.md` as gates go live.
6. Where a decision closes an open question in PRD §13, point that entry at the ADR. New
   requirements use `NFR-1200`–`NFR-1299` and `INV-080`–`INV-089`, reserved for this track.

**Status field:** `Accepted` only where the decision follows from something already answered;
`Proposed` otherwise.

**Definition of done:** every candidate technology carries a costed comparison at both envelopes;
every gate in `CLAUDE.md` is either implemented or has a stated reason for deferral; the
adversarial suite in §2.1 exists; and every gap is an open question with options and a
recommendation rather than an assumption.

---

## 6. Start here

Before writing anything, reply with:

1. Your understanding of the task in five sentences or fewer.
2. Your **blocking** questions, in priority order, each with at least two options and your
   recommendation.
3. Your **non-blocking** questions, listed only.
4. Anything in the PRD, the ADRs or the implemented code that looks untestable as specified.
   A requirement that cannot be tested is a requirement that will not hold, and finding those is
   the most valuable thing this session can do.

Wait for answers before writing.
