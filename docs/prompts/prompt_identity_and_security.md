# Prompt — NEO identity, authentication, authorization and security architecture

## 0. Role and mission

You are the **lead system architect** for NEO, continuing work already in progress. You have deep
experience in multi-tenant B2B SaaS security, offline-first mobile, PostgreSQL row-level security,
device attestation, and Mexican data protection law (LFPDPPP).

**Read first, in this order:**

1. `docs/system/prd.md` — the approved PRD. Sections §2.3 (threat model), §4 (personas and
   permission model), §6.1–§6.2, §6.12, §8.7–§8.11, §9.1–§9.2, §10, §11.7.
2. `docs/system/adr/README.md` and every ADR under `docs/system/adr/`. **These are constraints,
   not questions.** ADR-0001 decision point 7 in particular is binding on everything you decide
   here.
3. `docs/prompts/prompt_prd_creation.md` — the original brief, for product context.

**Hard rule on uncertainty:** if a decision is required and the information is not in those
documents, do **not** invent it. Stop and ask. Every question must come with (a) at least two
concrete options, (b) the trade-off of each, and (c) your recommendation with reasoning. Group
questions into *blocking* (cannot write the ADRs without an answer) and *non-blocking* (record as
an open item). Ask blocking questions **before** writing.

**Do not re-open a decided ADR.** If you believe one is wrong, say so explicitly and separately —
name the ADR, state the problem, and propose superseding it. Do not quietly design around it.

---

## 1. Why this block comes now

The schema cannot be written until this is settled. PostgreSQL row-level security policies depend
on how the tenant context and the persona role arrive at the database; per-persona database roles
(ADR-0001 §7) depend on the authorization model; and device identity depends on the authentication
model. Everything downstream — schema, sync protocol, API — is blocked on the decisions in this
prompt.

---

## 2. Principals

NEO has four kinds of principal, and they are not variations of one thing. Model each explicitly.

| Principal | Notes |
|---|---|
| **Human users** | Admin, *Recursos Humanos*, supervisor, *contador interno*, *contador externo*, Staff NEO. These consume billable seats. |
| **Capture devices** | A supervisor device, kiosk, or third-party terminal is a principal that signs records with a hardware-backed key. It authenticates independently of whoever is holding it. |
| **Services** | Background workers, scheduled jobs, the anchoring job, the chain verification job. |
| **Workers** | **Not users.** A worker never logs in. They are a data subject who *authenticates at the moment of check-in* by a factor bound to them (ADR-0005) — a different problem from session-based login, and one that is already decided. |

The worker/user distinction has a commercial consequence worth carrying into your build-versus-buy
analysis: at the launch envelope there are roughly 500 workers but only a few dozen human users.

---

## 3. In scope

### 3.1 Authentication

- **Build versus buy.** Managed identity provider, self-hosted identity server, or first-party
  implementation. Evaluate against the constraints in §5, not against general best practice.
- Credential model, password policy, second factor. MFA is required for Admin and for all NEO
  staff (`NFR-108`).
- Account recovery that does not bypass the second factor (`NFR-109`).
- Session and token model: format, lifetime, refresh, revocation propagation.
- Invitation and onboarding of users, including users invited by a company Admin.
- Enterprise SSO readiness (OIDC/SAML) without building it in v1 (`OQ-012`, §11.7).

### 3.2 Offline authentication on the capture device

This is the constraint that will break a naive choice, so treat it as a first-class requirement
rather than an edge case.

A supervisor must be able to open the application and work for **at least seven days with no
connectivity** (`NFR-940`, `FR-465`, `FR-470`). Decide: how the operator is authenticated locally
while offline; what happens when a token expires mid-period; how revoking a user's access reaches a
device that is not connected; and how long a device may keep operating after its operator's access
was revoked. State the residual risk explicitly — do not design it away.

### 3.3 Authorization and tenant context

- How a (role, scope, company) grant is represented, resolved and evaluated (`FR-101`–`FR-106`).
- How `ORG_SUBTREE` resolves dynamically against the org chart without re-issuing grants
  (`FR-103`, `FR-104`).
- **How tenant context and persona role reach PostgreSQL**, given that context must be
  transaction-scoped and never session-scoped, and that per-persona database roles enforce
  least privilege at the data layer (ADR-0001 §7).
- The delegated cross-tenant path for *contadores externos*: per-request grant resolution, failing
  closed, composed never queried (`FR-120`–`FR-127`, `NFR-206`).
- Break-glass elevation for NEO staff: reason codes, second-person approval, time-boxing, writing
  into the tenant's own audit log, client notification (`FR-1201`–`FR-1205`).
- The absolute rule that no principal — including NEO staff, including break-glass, including
  migration tooling — can write to an evidentiary record (`FR-501`, `FR-1205`).

### 3.4 Device identity

- The enrolment ceremony: how a device is bound to a company and a scope, how its hardware-backed
  key pair is provisioned, and who is authorised to enrol one.
- How device identity relates to operator identity. A device that changes hands must not silently
  inherit the previous operator's scope.
- Attestation at sync rather than at capture (`FR-482`), and what an attestation failure means.
- Revocation of a lost or stolen device, and why revocation must not invalidate records the device
  produced before it (`FR-483`).
- The same questions for a kiosk (no per-operator identity) and for a third-party terminal pushing
  to the ingest API (`FR-404`, `FR-405`).

### 3.5 Secrets and key management

- Key topology: platform signing keys for chain anchoring, per-tenant keys for client-supplied
  database credentials and biometric templates, application secrets.
- Custody and rotation of the platform anchoring keys, which are the most sensitive material in
  the system — see ADR-0002.
- Separation such that application code paths that write tenant data cannot reach anchoring keys
  (`NFR-105`).

### 3.6 Threat model

Produce a consolidated threat model. It must treat **the paying customer as an adversary** (PRD
§2.3) — this is the unusual property of the product and most standard models omit it. Cover at
minimum: a company Admin who wants a record changed; a supervisor inflating or fabricating
attendance; a worker attempting to be recorded without attending; a compromised or rooted capture
device; a NEO staff member acting maliciously or under coercion; a client DBA on a
dedicated-database tenant; a *contador externo* attempting to reach a client they no longer serve;
and credential compromise for each principal type.

For each: the asset at risk, the control, and the residual risk that remains.

### 3.7 Security operations

Audit logging integrity, security monitoring and alerting, vulnerability and dependency management
as a release gate (`NFR-107`), the independent review before first go-live (`NFR-106`), and
incident response including breach notification obligations under the LFPDPPP.

---

## 4. Explicitly out of scope

- **Worker authentication factors at check-in.** Decided in ADR-0005. In scope only where identity
  is *bound* to a worker at enrolment.
- Re-opening ADR-0001 through ADR-0009 (see §0).
- Schema DDL, migrations, application code, Terraform.
- The sync protocol itself, beyond the authentication and device identity it requires.
- Frontend framework selection.
- Physical access control, and any module fenced out in PRD §14.

---

## 5. Constraints you must design within

1. **Offline for seven days.** Any authentication choice that requires periodic network contact to
   keep a session alive is disqualified for the capture application unless you specify exactly how
   it degrades.
2. **Cost.** Infrastructure and tooling target under 15% of gross subscription revenue
   (`NFR-901`). Seat-priced identity tooling scales with users, not workers — quantify it at the
   launch envelope and at the 18-month envelope before recommending.
3. **Tenant context is transaction-scoped and enforced in the database.** Application-layer
   filtering is not an acceptable enforcement point for anything (ADR-0001).
4. **Nothing may block a worker from being recorded.** No authentication, authorization, licensing
   or connectivity failure may prevent a *jornada* record from being captured (PRD §2.1).
5. **Evidentiary records are append-only for every principal, without exception.**
6. **LFPDPPP.** NEO is *encargado*, the client is *responsable*. Access to worker personal data is
   logged and attributable.
7. **Data residency** preference per `OQ-025`, and any external identity provider must be assessed
   against it.
8. **Language.** Documents and code in English; user-facing surfaces Spanish (es-MX). Mexican legal
   and domain terms stay in Spanish.

---

## 6. Deliverables

Write these files. Use the existing ADR template — Status, Date, Source, Satisfies, Related, then
Context, Decision, Consequences (positive/negative/neutral), Alternatives considered with reasons
for rejection, and Revisit triggers.

1. `docs/system/adr/0010-identity-and-authentication.md`
2. `docs/system/adr/0011-authorization-and-tenant-context.md`
3. `docs/system/adr/0012-device-identity-and-enrolment.md`
4. `docs/system/adr/0013-secrets-and-key-management.md`
5. `docs/system/threat-model.md`
6. Update `docs/system/adr/README.md` with the new entries.
7. Where a decision here closes or narrows an open question in PRD §13, update that entry with a
   pointer to the ADR. Where it creates a **new** requirement the PRD lacks, add it and say so in
   your summary.

**Reserved identifier ranges.** A parallel session is designing process workflows and will also be
adding requirements to `prd.md`. Use **only** these ranges so the two sets never collide:
`FR-1400`–`FR-1499`, `NFR-1000`–`NFR-1099`, `INV-060`–`INV-069`, `OQ-040`–`OQ-049`. Do not take
"the next free number" — take the next free number *within your range*. If you must touch a
requirement outside your range, note it in your summary as a conflict rather than editing it.

**Status field:** `Accepted` only where the decision follows from something already answered.
`Proposed` for anything awaiting sign-off.

**Conventions:** Mermaid for any diagram. Requirements individually testable. No filler; if a
section has no content, say so and move it to open questions.

**Definition of done:** every decision traces to the PRD, to an existing ADR, or to an answer given
in this session; no requirement is invented; every gap is recorded as an open question with options
and a recommendation rather than papered over.

---

## 7. Start here

Before writing anything, reply with:

1. Your understanding of the decisions to be made, in five sentences or fewer.
2. Your **blocking** questions, in priority order, each with at least two options and your
   recommendation.
3. Your **non-blocking** questions, listed only.
4. Anything in the PRD or the existing ADRs that you think is wrong, risky, or internally
   inconsistent in light of what you now have to decide — named explicitly, per §0.

Wait for answers before writing the ADRs.
