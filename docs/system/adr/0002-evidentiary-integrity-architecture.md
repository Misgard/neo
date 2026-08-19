# ADR-0002 — Evidentiary integrity architecture

- **Status:** Proposed
- **Date:** 2026-08-18
- **Source:** PRD §2.2, §6.5, §11.1; brief §1, §3
- **Satisfies:** `FR-501`–`FR-534`, `FR-1314`, `FR-1335`, `INV-010`–`INV-017`
- **Related:** ADR-0001 (anchors outside client control), ADR-0003 (trusted time)

## Context

The *jornada* record has to carry *prueba plena*. In practice that means surviving a *peritaje
informático*: a court-appointed expert, given only what we export and a published procedure, must
be able to verify our claims without our cooperation.

The threat model includes the customer (PRD §2.3). The party with the strongest motive to alter a
record is the *patrón*.

Cost is a hard constraint. At the launch envelope the platform produces roughly 22,000 *jornada*
events and 90 *listas de asistencia* per month against modest revenue, so any mechanism priced
per document has to be examined before it is adopted.

## Decision

**1. Append-only everywhere.** No `UPDATE` or `DELETE` path exists against a *jornada* record, a
*lista*, a *movimiento*, a wage record, a *desviación*, an overtime authorisation, or an audit
entry — in any environment, including support and migration tooling. Corrections are new records
referencing what they supersede, and both appear in every export.

**2. Sign at the edge.** Each record is signed on the capture device at the moment of capture with
an ECDSA P-256 key generated in hardware-backed storage at device enrolment and never exportable.
Records also carry a monotonically increasing sequence number and the hash of the preceding record
from that device, so reordering, insertion and deletion are detectable independently of any
claimed timestamp.

**3. Per-tenant hash chain.** Every evidentiary object — *jornada* records, corrections, *listas*,
ingested IDSE artifacts, *expediente* documents, *desviaciones* and their signed scans, overtime
authorisations — is hashed with SHA-256 and linked into a per-tenant append-only chain, sealed at
least daily into a chain root.

**4. Batch the external anchor.** All tenant chain roots sealed in the same period become leaves
of a platform-wide Merkle tree, and **only the tree root is submitted to an external RFC 3161
timestamping authority.** Each object's presence under that root is proven by a Merkle inclusion
path.

This is the decision that makes the economics work. External anchoring becomes a function of time
rather than of tenant count or event volume: tens of anchors per month for the whole platform at
launch, and the same tens of anchors at fifty times the volume.

**5. NOM-151 as an option, not the baseline.** A *constancia de conservación* from a *PSC*
authorised under NOM-151-SCFI-2016 can be issued per *lista de asistencia* as a per-company paid
entitlement, for clients who want the simplest possible story in front of a *junta*. It is not the
default, because at ~90 *listas* per month it is a material recurring cost for a property the
batched chain already provides.

**6. Publish the roots.** Sealed Merkle roots are published to an append-only public log. It costs
almost nothing, lets a client or an opposing expert witness that a root existed before a disputed
date without relying on us, and materially strengthens the story when the TSA is questioned.

**7. Verification bundle as a product.** For any scope, the system emits records, corrections,
chain segment, inclusion paths, TSA tokens, device attestation results and device public keys,
together with a published versioned procedure and an open-source verifier. **Verification must
remain possible after NEO ceases to exist:** no step may depend on an API we control.

**8. WORM at the storage layer.** Uploaded artifacts — IDSE PDFs, *expediente* documents, signed
scans, sealed *listas* — are stored with object retention and holds so that immutability is
enforced by the storage service, not only by application logic.

## Consequences

**Positive.** Anchoring cost is decoupled from growth. Tamper-evidence holds against the tenant,
against NEO staff, and against a DBA. A client that later wants per-document *constancias* gets
them as configuration. The verification story is explainable to a *perito* in one page.

**Negative.** A Merkle inclusion proof demands more of an expert than a single-document
*constancia* does; this is mitigated by the published verifier and by offering per-*lista*
*constancias* to clients who want them. Platform-side signing keys become critical infrastructure
requiring their own custody discipline. Sealing introduces a bounded latency between capture and
"sealed", during which a record is stored but not yet anchored.

**Neutral.** TSA dependency is real but replaceable; the design deliberately admits more than one
anchor per root.

## Alternatives considered

**Per-event external timestamping.** 22,000 anchors a month at launch. Rejected on cost, and it
buys nothing the chain does not already give.

**Per-*lista* NOM-151 for everyone.** The cleanest courtroom artifact, and the option remains
available per company. Rejected as the default on recurring cost against launch revenue.

**Blockchain anchoring.** Would work technically. Rejected: it adds an explanation burden and an
external dependency in front of a Mexican tribunal, where an RFC 3161 token and a NOM-151
*constancia* are the instruments with an established legal footing.

**Application-enforced immutability only, without chaining.** Rejected — it proves nothing to
anyone who does not already trust the application.

## Revisit triggers

- Counsel advises that a Mexican tribunal materially discounts a Merkle inclusion proof relative
  to a per-document *constancia*.
- A *PSC* quote low enough that per-*lista* *constancias* become the sensible default.
- Any TSA reliability problem, which should trigger dual anchoring rather than a redesign.
