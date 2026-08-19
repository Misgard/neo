# ADR-0001 — Tenancy and data isolation

- **Status:** Accepted
- **Date:** 2026-08-18
- **Source:** PRD §5, §6.1, §9.2; brief §5; decision `B4`
- **Satisfies:** `FR-001`–`FR-010`, `NFR-201`–`NFR-205`, `INV-001`, `INV-003`
- **Related:** ADR-0002 (integrity anchoring), ADR-0007 (compute and data platform)

## Context

Isolation by company is mandatory. The only sanctioned cross-tenant paths are the *contador
externo* portfolio surface, scoped to explicit per-company grants, and NEO's non-personal
control plane.

Some clients will want their data in a database they own, and a future Mexican data-localisation
rule could make that a requirement rather than a preference. No client has contractually demanded
it yet.

The complication is that a client-controlled database appears to destroy *prueba plena*: if the
*patrón*'s DBA can `UPDATE` a *jornada* row, tamper-evidence collapses into "trust the employer,"
which is the failure the law exists to correct (PRD §2.3).

## Decision

**1. Pooled multi-tenant with PostgreSQL row-level security is the default.** Isolation is
enforced in the database, not in application code. Every tenant table carries a company
identifier and an RLS policy; the application connects as a non-superuser role and sets the
tenant context per transaction. A query issued with no tenant context returns zero rows, not all
rows.

**2. Every data access goes through a per-tenant connection resolver from day one**, even while
every tenant resolves to the same pooled database. This is the cheap decision that makes the rest
possible: adding a dedicated-database tenant later becomes a routing-table entry plus a migration
target rather than a refactor.

**3. A dedicated-database tier exists**, in which the tenant's data lives in a PostgreSQL database
the client owns, reached with credentials the client supplies and we hold encrypted under a
per-tenant key. Schema and migration sequence are identical to the pooled tier.

**4. The enabling condition: integrity anchors always live in NEO's infrastructure.** Per-tenant
chain roots and their external timestamps are computed and retained by us for every tenant,
including dedicated-database ones. A tenant that edits a row in their own database breaks the
chain, and the break is provable. This converts the tier from "trust the *patrón*" into "the
*patrón* cannot alter this undetectably." A configuration where a tenant's anchors exist only in
client-controlled storage is invalid.

**5. Ingestion always lands in NEO first.** Attendance writes to a durable queue in our
infrastructure and is then projected into the tenant database. A tenant database that is
unreachable delays projection; it never loses a *jornada* record. This means we transiently hold
data for every tenant including dedicated ones, which must be disclosed in the contract and the
*aviso de privacidad*.

**6. Non-personal metering and health metrics replicate to the control plane** for every tenant,
so billing, entitlements and monitoring work identically across tiers. Personal data does not
replicate.

**7. Cross-tenant access is composed in the application, never expressed as a cross-tenant query.**

The *contador externo* portfolio is the only routine multi-company surface and it is the riskiest
path in the system, because it is the one place where a scoping defect produces a leak between two
tenants the same authenticated user is legitimately entitled to reach. It therefore fails silently
rather than throwing a permission error, and generic isolation testing does not catch it. Five
rules govern it.

- **The tenant context is always exactly one company.** There is no set-valued tenant context and
  the database never sees a query spanning tenants. A portfolio view is built by iterating: one
  tenant-scoped transaction per granted company, composed above the data layer. This keeps
  `INV-001` absolute rather than carved out — and the tenancy model forces it anyway, since an
  accountant holding one pooled client and one dedicated-database client cannot be served by a
  single query, because the rows are in different databases.
- **Grants live in the control plane and are resolved per request, failing closed.** The set of
  (accountant, company, role) grants is never tenant data. A grant is re-checked on every request
  rather than baked into a session token, so revocation and time-box expiry take effect on the next
  request. If grant resolution is unavailable, access is denied — never defaulted.
- **Tenant context is transaction-scoped, never session-scoped.** `SET LOCAL` inside the
  transaction, never `SET`. Under connection pooling a session-scoped context can carry one
  tenant's identity into the next request on the same pooled connection, and for this user that is
  a leak between two tenants they are allowed to see: the case least likely to be noticed in
  testing or in production.
- **The accountant connects under a narrower database role.** Least privilege inside the grant —
  *jornada*, *listas*, *incidencias* and the payroll identity fields, but not the *expediente* — is
  enforced by table-level grants on a per-persona database role, not by application code. Same
  philosophy as decision 1: the database refuses, rather than the application remembering to.
- **Composed views stay partitioned.** Data from two companies is never merged into one table,
  chart or total. The portfolio is a switcher, not a consolidation, and the accountant works one
  client at a time. The sole exception is the accountant's own billing data, which is theirs.

The portfolio landing page needs no cross-tenant data access at all: the list of companies an
accountant may open, with names and grant state, is control-plane data.

**The isolation test suite covers this path explicitly**, because a generic "tenant A cannot read
tenant B" test proves nothing here — this user is *supposed* to reach more than one tenant. The
release gate requires proving that an accountant granted A and B cannot reach C; that a revoked
grant fails on the next request; that an expired time-boxed grant fails; and that a request whose
grant lookup errors is denied rather than served.

## Consequences

**Positive.** One codebase, one migration sequence, one incident-response procedure. Metering and
the NEO staff dashboard work uniformly. The dedicated tier is available on demand without a
rewrite, and a data-localisation mandate becomes a deployment exercise rather than a crisis. The
portfolio surface introduces no second isolation mechanism — it reuses the single-tenant path N
times, so there is exactly one code path to prove correct.

**Negative.** Composing N single-tenant queries is slower than one cross-tenant query, and it
degrades as a *despacho*'s portfolio grows; a portfolio dashboard over dozens of clients needs
cached control-plane summaries rather than a fan-out on every page load. RLS discipline has to be
absolute: one table without a policy is a cross-tenant leak. This is mitigated by making the isolation test suite a release gate (`NFR-202`) rather than
by review discipline. Connection pooling interacts with per-transaction tenant context and
constrains pooler configuration. The dedicated tier adds migration orchestration across N
databases with version skew, and it cannot be sold at the pooled per-employee rate.

**Neutral.** The connection resolver is dead weight until the first dedicated tenant. It is worth
carrying: retrofitting it into a live system with tenant data in flight is the expensive version.

## Alternatives considered

**Schema-per-tenant.** Migration fan-out and connection-pool pressure for a marginal isolation
gain over RLS correctly applied. Rejected — it takes on the operational cost of separation
without the property clients actually ask for, which is "my data, my database."

**Database-per-tenant on our infrastructure, for everyone.** Real blast-radius isolation and
per-tenant PITR, but the per-tenant cost floor is incompatible with the smallest plans, where a
client may have five employees.

**Application-layer tenant filtering.** Rejected outright. It fails open — a forgotten `WHERE`
clause is a breach — and it cannot be proven correct to an auditor the way a database policy can.

**A set-valued tenant context for delegated users.** One query serves the whole portfolio and
performance is better. Rejected: it makes multi-tenant queries a supported state of the system, so
every query written thereafter inherits the risk, and it moves grant correctness onto the hot path
of every read. It also cannot serve a portfolio spanning both tenancy tiers.

**Client-hosted with client-held anchors.** Rejected. It is the one configuration that would make
the product's central claim false.

## Revisit triggers

- The first contractual demand for a dedicated database, which turns the tier from readiness into
  a delivery commitment with an SLA.
- A localisation rule requiring client-side or in-country-only storage.
- Pooled database contention that RLS-compatible read replicas cannot relieve.
- A *despacho* portfolio large enough that fan-out composition becomes the bottleneck. The answer
  is cached control-plane summaries, not a widened tenant context; that path is closed by decision
  point 7 and reopening it requires superseding this ADR.
