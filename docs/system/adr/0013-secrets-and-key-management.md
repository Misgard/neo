# ADR-0013 — Secrets and key management

- **Status:** Proposed
- **Date:** 2026-08-19
- **Source:** PRD §6.14.8, §9.1 (`NFR-102`, `NFR-103`, `NFR-105`), §6.1 (`FR-005`), §8.6;
  ADR-0002, ADR-0007 decision 5
- **Satisfies:** `FR-1488`–`FR-1497`, `NFR-102`, `NFR-103`, `NFR-105`, `NFR-1010`, `INV-069`
- **Related:** ADR-0001 (dedicated tier, client-supplied credentials), ADR-0002 (anchoring),
  ADR-0005 (templates not images), ADR-0007 (KMS and Secret Manager)

## Context

ADR-0002 makes the platform's signing keys the root of the product's central claim: they sign the
chain roots that go to an external timestamping authority, and anyone holding one can forge the
evidence NEO sells. `NFR-105` requires them to be unreachable from application code paths that write
tenant data. Nothing yet says how.

Three other classes of material sit alongside them and have genuinely different threat profiles.
**Client-supplied database credentials** (`FR-005`) unlock an entire dedicated-database tenant.
**Biometric templates** are *datos personales sensibles* that `FR-439` says never leave the tenant
boundary — a sentence that becomes ambiguous in the tier where the tenant boundary is a database the
client owns. **Ordinary application secrets** are the least sensitive and the most numerous.

## Decision

**1. Four custodial domains, kept separate, and no principal holds all four** (`FR-1488`).

| Domain | What it protects | Reachable from |
|---|---|---|
| **Anchoring keys** | The chain roots — the product's claim | The sealing and anchoring jobs only |
| **Tenant data keys** | Client DB credentials, biometric templates | The connection resolver; the template path |
| **Application secrets** | Everything ordinary | The services that need them, individually |
| **Device public keys** | Nothing — they are public | Anyone; they travel in the bundle |

The fourth is listed because it is routinely confused with the others. Device *public* keys are
published deliberately: `FR-533` requires a bundle to be verifiable after NEO has ceased to exist,
and a verifier that needs a key from us fails that test.

**2. The anchoring keys are reachable only from the sealing and anchoring jobs, which run under a
deployment identity holding no grant on any tenant table** (`FR-1489`). ADR-0007 decision 1 already
runs scheduled work as separate container jobs, so this costs nothing: it is a matter of giving
those jobs their own service identity and not giving it to anything else. **The property is
directional and worth stating both ways** — the jobs that can sign cannot read tenant rows, and the
services that write tenant rows cannot sign. Neither half is useful alone.

**3. The separation is asserted by test, not by review** (`FR-1490`, `NFR-1010`, `INV-069`).
A gate attempts to obtain an anchoring key from every code path that writes tenant data and fails
the build if any succeeds. This is the same reasoning as `NFR-943`: a property that matters this
much and is invisible in ordinary operation stops being true the day someone adds a convenient
import, and nothing tells you.

**4. Anchoring keys are HSM-protected in the cloud KMS, with dual control deferred and scheduled**
(`OQ-044`). Hardware protection costs little more than software protection and removes the class of
compromise where the key material itself is exfiltrated. Dual control on rotation and on access-
policy changes is the right end state and is not real at two staff — the same headcount fact that
drives `FR-1461`. Recording it as a scheduled change makes it a planned event rather than an audit
finding.

**5. Rotation retains everything it signed** (`FR-1491`, `FR-1492`). A rotated anchoring key is kept
for verification, and every chain root records the identifier and version of the key that signed it.
A verification bundle must stay checkable for the life of the record (`FR-533`), which is longer
than any key's sensible service life, so **key retirement is never key destruction**. A *perito*
reading a root learns which key to check without asking.

**6. Client-supplied database credentials are per-tenant encrypted and readable only by the
connection resolver** (`FR-1493`). ADR-0001 decision 2 routes all tenant access through that
resolver, which makes it the natural and only holder. Credentials are never logged, never in an
error message, and rotatable without downtime — a client who suspects exposure must be able to act
without scheduling an outage.

**7. Biometric templates are encrypted under a per-tenant key held by NEO** (`FR-1494`). This is the
decision that keeps `FR-439` true in the dedicated tier: the client's own database holds template
**ciphertext the client cannot read**. Templates therefore do not leave the tenant boundary, and
they also do not become readable to the client's DBA merely because the storage is theirs.

This is a defensible position under `A-010` — NEO is *encargado*, the client is *responsable*, and
the client's access to their own workers' biometric templates is not something the LFPDPPP requires
to be direct — but it is a place where the dedicated tier's promise ("my data, my database") and the
product's biometric commitments genuinely pull apart, and the client should be told which way it
was resolved rather than discovering it.

**8. Application secrets are injected at runtime and never baked in** (`FR-1495`). No secret in an
image, none in source control, and the deploy pipeline holds no long-lived key it does not need.

**9. Key and secret access is logged, attributable and alertable** (`FR-1496`, `NFR-1015`). An
anchoring key used outside a sealing window is the highest-severity signal this platform has, and it
is only visible if access is logged.

**10. Nothing sensitive reaches a support surface, a backup or an export** (`FR-1497`, `NFR-103`).
Credential verifiers, second-factor secrets, recovery-code verifiers, client database credentials,
template plaintext and anchoring key material are excluded from every export and hand-off,
**including the verification bundle** (`FR-1417`). The bundle needs public keys and proofs; it needs
no secret, and a bundle that leaked one would be handed to an opposing expert in a hearing.

## Consequences

**Positive.** The key that forges evidence and the code that writes evidence cannot reach each
other, and that is continuously tested rather than asserted. The dedicated tier no longer creates a
biometric exposure it was never meant to. Anchoring survives NEO: retained keys plus key identifiers
on every root mean a bundle stays verifiable long after a key leaves service.

**Negative.** Four custodial domains is more key-management machinery than a platform this size
would otherwise carry, and rotation of the anchoring keys becomes a procedure someone must actually
own. Dual control is deferred, so today two people can between them do anything to the most
sensitive material in the system — stated plainly because it is the honest position at this
headcount, and it is why `OQ-044` carries a date rather than an intention. Per-tenant keys for
templates and credentials mean per-tenant key operations to monitor and per-tenant failure modes.

**Neutral.** Holding template keys ourselves is right on the security merits and is a talking point
the dedicated tier's buyer will raise. Better raised in the sale than found in an audit.

## Alternatives considered

**One key domain with fine-grained IAM.** Fewer moving parts and cheaper to operate. Rejected:
`NFR-105` asks for a structural separation, and a single domain makes that a policy statement — one
misconfigured binding away from an application service holding the anchoring key, with nothing
failing visibly.

**Software-protected anchoring keys.** Marginally cheaper. Rejected on the asymmetry: these keys do
not leak data if compromised, they let someone manufacture *prueba plena*, and hardware protection
is a small line item against that.

**Letting the client hold the key to their own biometric templates in the dedicated tier.** The
purest reading of "my data, my database". Rejected: it makes templates readable by the client's
DBA, which contradicts `FR-439` and `INV-051`, and it puts template custody with the party §2.3
names as the adversary.

**Destroying rotated anchoring keys.** Standard hygiene in most systems. Rejected here — it would
make every bundle signed under that key unverifiable, which is the one outcome `FR-533` forbids.

**Client-held anchoring keys for dedicated tenants.** Rejected by ADR-0001 decision 4 and repeated
here because it is the request that will actually be made: it is the single configuration that makes
the product's central claim false, and `INV-003` names it invalid.

## Revisit triggers

- NEO staff headcount making dual control real, which closes `OQ-044` at option (c).
- A client contractually requiring custody of the keys protecting their own tenant data, which is a
  commercial and legal question before it is a technical one.
- Any anchoring key access outside a sealing window — an incident, not a revisit, but it would
  reopen decision 4 immediately.
- A cloud KMS regional availability gap in whichever region `OQ-025` settles on, which could force
  key material and tenant data into different jurisdictions and would need to be disclosed.
