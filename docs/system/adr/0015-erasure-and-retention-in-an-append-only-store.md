# ADR-0015 — Erasure and retention in an append-only store

- **Status:** Proposed
- **Date:** 2026-08-20
- **Source:** PRD §2.7, §6.5.1, §6.5.2, §6.11, §6.15.13; the process and workflows session
- **Satisfies:** `FR-2410`–`FR-2415`, `FR-1104`, `FR-1111`, `FR-1112`, `INV-107`, `INV-108`,
  `INV-109`, `NFR-1107`, `NFR-1108`, `NFR-1109`
- **Related:** ADR-0002 (integrity chain), ADR-0013 (key management), ADR-0001 (tenancy)

## Context

Two requirements in this product are both non-negotiable and, as written, incompatible.

`FR-501` and `INV-012` say that no `UPDATE` and no `DELETE` path exists against an evidentiary
record **in any environment**, and the guarantee is enforced in the database rather than in code:
no role holds the privilege (`NFR-944`, `NFR-1002`), an unconditional trigger raises on both
(`FR-1458`), and a release gate asserts all of it. This is the mechanism the product's central
claim rests on, and `NFR-943` proves it by mutating a row directly and asserting the chain notices.

`FR-1104` says an ARCO *cancelación* against a record inside its statutory retention window is
honoured by *bloqueo* and the record is **destroyed when the window lapses**. `FR-1111` says
personal data is retained on a per-category schedule, which implies the same destruction without
anybody asking for it.

So the system must destroy personal data on a schedule, using a mechanism that does not exist and
must not be created. Building the door is the whole problem: once a privileged deletion path
exists, `NFR-943` can no longer distinguish an authorised erasure from tampering, and every client
loses the property they are paying for so that one worker's request can be honoured.

A second question sits underneath it. If the chain is stored as columns on the evidentiary rows —
`hash`, `prev_hash`, `seq` — then removing a row removes its link and the removal is invisible. If
the chain is a structure of its own, a hash with no row behind it is a **detected gap**. That is a
storage decision with an evidentiary consequence, and it has not been made anywhere.

## Decision

**1. The integrity chain is a structure of its own; evidentiary rows reference it.** The chain is
not columns on the tables it seals (`FR-2410`, `INV-108`). The consequence that matters: a row
removed directly in the database leaves a sealed hash pointing at nothing, which verification
detects. Storing the chain on the row would make the same removal silent.

**2. Personal fields on evidentiary records are encrypted under a per-worker key**, held in the key
management service outside the row it protects (`FR-2411`), within the tenant-data custodial domain
of ADR-0013 decision 1 and separate from the anchoring keys.

**3. Erasure destroys the key and nothing else** (`FR-2412`, `INV-107`). The row is untouched, its
hash still matches, the chain still verifies end to end, and the plaintext is unrecoverable by
anyone including NEO. **This is the only erasure that requires neither an `UPDATE` nor a `DELETE`**,
and therefore the only one compatible with `FR-501`. The door is never built.

**4. What survives erasure is the shape of the record, not its subject.** The record's existence,
its time anchors, its class, its device, its chain position and its *desviaciones* remain; the
identity of the person it describes does not. A *lista de asistencia* covering an erased period
still verifies and still shows that a row existed, marked as erased under its obligation. This is
the honest outcome: the evidentiary structure is preserved and the personal data is gone.

**5. Erasure is an audited, attributable act whose record outlives the data** (`FR-2413`): what was
erased, under which obligation, on whose authority, when, and when the requester was told. `FR-1103`
already retains audit entries independently of the objects they describe, and this is the case that
requirement exists for.

**6. A legal hold suspends key destruction** (`FR-2414`). A key under hold is destroyed on no
schedule, and the hold is disclosed on every artifact covering the held period. Where a hold and a
lapsed retention window collide, the hold wins and the requester is told why — which is the same
resolution §2.7 already reaches between statutory retention and *cancelación*.

**7. Archival carries the chain with it** (`FR-2415`, `INV-109`). Moving a period to separate
storage for cost or performance moves its chain segment, its roots and its external timestamp
tokens too, and a verification bundle over an archived period is producible from the archive alone.
A claim about 2027 arrives in 2032; an archive that cannot be verified without the live database is
an archive that fails at exactly the moment it is needed.

**8. Three tests, treated as release gates.** Erasure destroys only the key and leaves chain
verification succeeding (`NFR-1107`); a row removed directly in the database is detected
(`NFR-1108`); a verification bundle over an archived period is producible from the archive alone
(`NFR-1109`).

## Consequences

**Positive.** The append-only guarantee stays absolute and testable — there is no privileged path
to argue about, and `NFR-943` keeps meaning what it says. A worker's *cancelación* is honoured
genuinely rather than by a policy promise, and NEO can demonstrate the erasure occurred. Removal of
a row by anyone, for any reason, becomes detectable rather than invisible, which strengthens the
threat model against the customer (§2.3). Archival becomes available as a cost lever without
weakening any evidentiary claim.

**Negative.** A key per worker is a real key-management burden: key count grows with the workforce
rather than with the tenant count, and every read of a personal field is a key resolution. It has
to be designed into the schema from the start — retrofitting it is a migration across every
evidentiary row in the system, which is precisely the cost this ADR exists to avoid paying later.
Losing a key by accident is indistinguishable from erasing it deliberately, so key custody becomes
as load-bearing as the chain itself. And an erased record is genuinely unreadable afterwards,
including to a *perito* examining an adjacent dispute — which is the correct outcome and will be
uncomfortable the first time it happens.

**Neutral.** Erasure by key destruction is cryptographic erasure, and its strength is the strength
of the cipher rather than the strength of physical destruction. That is a well-understood position
and is defensible; it is worth stating plainly in the verification procedure (`FR-531`) rather than
leaving a *perito* to discover it.

## Alternatives considered

**Delete the row and record an authorised chain break.** The obvious answer, and it destroys the
product. After the first authorised break, verification can no longer distinguish a lawful erasure
from a *patrón* removing an inconvenient day, and `FR-518` has to stop treating a break as critical.
Rejected.

**Never erase; make *bloqueo* permanent.** Honest, defensible, and it requires telling a worker that
their data is kept for as long as the system exists. It also leaves `FR-1104`'s promise and
`FR-1111`'s schedules as text that describes nothing. Rejected, though it remains the fallback if
per-worker key management proves unaffordable.

**Encrypt under a per-tenant key and destroy that.** Far cheaper in key count, and it erases every
worker in the tenant at once. Useless for an individual request. Rejected.

**Tombstone the row: keep the hash, blank the fields.** Requires an `UPDATE` on an evidentiary
table, which is the door this ADR exists not to build. Rejected.

**Store personal fields in a separate, mutable table the chain does not seal.** Would allow ordinary
deletion — and it removes the personal data from the sealed set, so the *lista de asistencia* could
no longer prove which worker a record described. That is the one thing the record has to say.
Rejected.

## Revisit triggers

- Counsel under `OQ-001` reading the statutory retention period, or the LFPDPPP *cancelación*
  obligation, in a way that changes what must be destroyed and when.
- A key management service cost or quota that makes per-worker keys unaffordable at the stage 3
  envelope (`NFR-506`), which would reopen the per-tenant alternative for a narrower field set.
- A *peritaje* or tribunal treating cryptographic erasure as insufficient destruction, which would
  force the permanent-*bloqueo* fallback.
