# ADR-0007 — Compute and data platform for v1

- **Status:** Proposed
- **Date:** 2026-08-18
- **Source:** PRD §9.7, `NFR-901`–`NFR-905`, `OQ-024`; brief §6
- **Satisfies:** `NFR-901`, `NFR-902`, `FR-006`, `NFR-203`
- **Related:** ADR-0001 (tenancy), ADR-0002 (integrity anchoring)

## Context

Cloud is GCP. The stated stack prior is Terraform, Kubernetes, ArgoCD, Docker, PostgreSQL, Alembic
and Python, offered as a strong prior rather than a constraint.

The binding fact is revenue. At the launch envelope — around 10 clients and 500 employees —
subscription revenue is on the order of tens of thousands of pesos per month. Infrastructure has to
fit inside 15% of that. A minimum viable managed-Kubernetes footprint with a regional HA database
plausibly consumes a quarter to a third of launch revenue before a single feature ships.

Load is small and bursty rather than sustained: roughly 22,000 *jornada* events a month, with the
real peak being many devices reconnecting at once after days offline.

## Decision

**1. Serverless containers for v1, not managed Kubernetes.** Services run as containers on a
serverless compute service with scale-to-low, and scheduled work — chain sealing, external
anchoring, alert evaluation, chain verification, metering rollups — runs as scheduled container
jobs. Everything is containerised and stateless, so the eventual move is a deployment change rather
than a rewrite.

**2. Managed PostgreSQL, single instance, point-in-time recovery enabled.** Sized for the launch
envelope, not the 18-month one. High availability is added when the availability target rather than
the fear of an outage requires it.

**3. The durable ingest queue is a database-backed outbox plus object storage, not a message bus.**
Uploaded batches are written to object storage and recorded in an ingest table; a worker projects
them into the tenant database. Ordering is per-device and already enforced by the record chain, the
volume is trivial, and replayability matters more than throughput. A message bus would add ordering
and dead-letter complexity for a problem this size does not have.

**4. Object storage with retention policies and holds** for IDSE PDFs, *expediente* documents,
signed *desviación* scans and sealed *listas*, so immutability is enforced by the storage service
and not only by application code.

**5. Secret Manager plus a key management service**, with per-tenant customer-managed keys for
client-supplied database credentials and biometric templates.

**6. Terraform for infrastructure. Alembic for migrations, with an orchestrator that applies the
same revision sequence across the pooled database and every dedicated-database tenant, recording
per-tenant applied state.** GitOps via ArgoCD is deferred with Kubernetes; deployment to serverless
containers goes through the CI pipeline directly.

**7. Python is the right choice for the backend, and is kept.** It is strong for the two hardest
backend jobs here — PDF parsing and extraction, and the cryptographic chain and verification tooling
— and the ecosystem for both is mature. Three components are explicitly not Python: the mobile
capture application (ADR-0006), on-device face matching and liveness (a licensed native SDK,
ADR-0005), and the web front end.

**8. Region: the Mexican GCP region, subject to a service-availability check** for every service
this ADR names, with the nearest alternative and a disclosed choice if any required service is
absent. Residency is the first question a Mexican compliance buyer asks even where no law compels
it.

**9. Named triggers for moving to managed Kubernetes**, so the move is a planned event rather than
an argument: sustained concurrency that makes always-warm serverless instances more expensive than
nodes; a service count beyond roughly 20–25; a need for private network paths to many
dedicated-tenant databases that serverless connectors serve awkwardly; or the point where a
platform engineer exists to operate a cluster. Any one of these opens the ADR that supersedes this
one.

## Consequences

**Positive.** Infrastructure cost lands inside target at launch, with cost scaling roughly with
use rather than with fixed footprint. The operational surface is small enough for a team without a
platform engineer. Nothing about the application changes when the migration comes.

**Negative.** Cold starts on low-traffic paths — mitigated by minimum instances on the ingest
endpoint only, which is the path with the availability target. Long-running jobs need to fit
serverless execution limits, which constrains how chain sealing and large exports are chunked. A
single database instance is a single failure domain until HA is added. Deferring GitOps means
deployment tooling gets rebuilt when Kubernetes arrives.

**Neutral.** The team's Kubernetes and ArgoCD experience goes unused for a period. It is the
destination, not the starting point.

## Alternatives considered

**Managed Kubernetes with GitOps from day one.** Matches the stack prior and is where this ends up.
Rejected for v1 on the cost share alone, at a stage where the alternative is one deferred
migration.

**Managed Kubernetes but minimal.** Reduces the gap without closing it and gives up serverless
scale-to-low while keeping cluster operations.

**Fully managed application platform with less container control.** Cheaper to operate and gives up
the container portability that makes the deferred migration safe.

**A message bus for ingest.** Better at a volume the system does not have; worse at the ordering
and replay properties it does need.

## Revisit triggers

Any of the four triggers in decision point 9, or infrastructure cost crossing 20% of gross
subscription revenue for two consecutive months.
