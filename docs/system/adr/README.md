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

## Open PRD questions each ADR closes

`OQ-024` → ADR-0007 · `OQ-033` → ADR-0006 · `OQ-004` → ADR-0002 (partially; *PSC* quotes still
outstanding) · `OQ-006` → ADR-0009 (pipeline settled; templates await a sample document)
