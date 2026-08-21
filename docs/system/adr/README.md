# Architecture Decision Records

One record per decision, written after the PRD ([`../prd.md`](../prd.md)) was approved. Each ADR
states the context, the decision, its consequences, the alternatives rejected and why, and the
triggers that would reopen it.

**Status** is `Accepted` where the decision follows from an answer already given, and `Proposed`
where it is a recommendation awaiting sign-off.

| ADR | Title | Status | Settles |
|---|---|---|---|
| [0001](0001-tenancy-and-data-isolation.md) | Tenancy and data isolation | Accepted | Pooled + RLS default, per-tenant connection resolver, dedicated-database tier, anchors always ours |
| [0002](0002-evidentiary-integrity-architecture.md) | Evidentiary integrity architecture | Proposed | Append-only, device signing, per-tenant chain, batched Merkle root, RFC 3161, NOM-151 as an option, verification bundle |
| [0003](0003-offline-trusted-time.md) | Offline trusted time | Accepted | Bound it, detect it, disclose it — anchored interval, monotonic evidence, GNSS |
| [0004](0004-capture-channels-and-device-platform.md) | Capture channels and device platform | Accepted | Supervisor-mediated default, kiosk, terminals as ingest, no NEO hardware, Android v1 |
| [0005](0005-attendance-authentication-factors.md) | Attendance authentication factors | Proposed | Baseline path first, face layered on top, no OTP at check-in, buy the liveness, templates not images |
| [0006](0006-application-shell-and-ui-codebase.md) | Application shell and UI codebase | Proposed | One web codebase, desktop console + native container, container is a v1 requirement |
| [0007](0007-compute-and-data-platform.md) | Compute and data platform for v1 | Proposed | Serverless containers over Kubernetes for now, with named triggers to move |
| [0008](0008-employment-imss-lifecycles-and-metering.md) | Two employment lifecycles, and the metering unit | Accepted | Operational vs IMSS lifecycles, exposure as a product, peak-concurrent billing |
| [0009](0009-idse-pdf-extraction-pipeline.md) | IDSE PDF extraction pipeline | Proposed | Deterministic templates, check digits, cross-footing; AI as a bounded fallback |
| [0014](0014-payments-and-fiscal-invoicing.md) | Payments and fiscal invoicing | Accepted | Stripe for charging, SW sapien as PAC for the whole CFDI 4.0 lifecycle; NEO computes the figure, the processor charges it |
| [0015](0015-erasure-and-retention-in-an-append-only-store.md) | Erasure and retention in an append-only store | Proposed | Chain stored separately, per-worker keys, erasure is key destruction, archival carries its chain |
| [0010](0010-identity-and-authentication.md) | Identity and authentication | Proposed | First-party auth on our own platform, identity in the control plane, MFA where it matters, device holds a signed capability not a session |
| [0011](0011-authorization-and-tenant-context.md) | Authorization and tenant context | Proposed | Atomic permissions and tenant-composed roles, database roles fixed by code, forced RLS against the owner, scope stored at write time, authorization history is evidence |
| [0012](0012-device-identity-and-enrolment.md) | Device identity and enrolment | Proposed | Online enrolment ceremony, device and operator are separate principals, no silent scope inheritance, revocation is time-split |
| [0013](0013-secrets-and-key-management.md) | Secrets and key management | Proposed | Four custodial domains, anchoring keys unreachable from tenant-write paths and tested, rotation retains, per-tenant keys for templates and client credentials |

## Open PRD questions each ADR closes

`OQ-024` → ADR-0007 · `OQ-033` → ADR-0006 · `OQ-004` → ADR-0002 (partially; *PSC* quotes still
outstanding) · `OQ-006` → ADR-0009 (pipeline settled; templates await a sample document) ·
`OQ-012` → ADR-0010 (federation mechanism fixed; whether a client needs it is still open) ·
`OQ-025` → ADR-0010 (identity no longer has a residency dimension; the platform question stands) ·
`OQ-026` → the process and workflows session (both signature models, cumulative)

## Consolidated threat model

[`../threat-model.md`](../threat-model.md) draws ADR-0001 through ADR-0013 together into one view of
adversaries, controls and **residual risk**, with the paying customer modelled as an adversary per
PRD §2.3. It is a living document; the independent security review it feeds (`NFR-106`) is a dated
snapshot and belongs in [`../../assessments/`](../../assessments/).
