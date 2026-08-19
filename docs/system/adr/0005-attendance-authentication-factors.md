# ADR-0005 — Attendance authentication factors

- **Status:** Proposed
- **Date:** 2026-08-18
- **Source:** PRD §8.2–§8.6; brief §4; decision `B1`
- **Satisfies:** `FR-410`–`FR-440`, `FR-1333`, `INV-050`, `INV-051`
- **Related:** ADR-0004 (channels and devices), ADR-0003 (trusted time)

## Context

The mechanism must guarantee one thing: **that the employee genuinely showed up to work.** The law
prescribes no method, so the design is method-agnostic with a working default.

Fingerprints are impractical — most workers in the target population have scarred or injured hands.
Cards and tags are unacceptable because they are trivially handed to someone else. Face recognition
works but crews are outdoors under unreliable lighting. Verification codes require both
connectivity and a phone, and remote sites have neither.

Biometric data is a *dato personal sensible* under the LFPDPPP, requiring express written consent
and an equally valid alternative for anyone who declines. Consent obtained inside an employment
relationship is exposed to a coercion argument wherever the alternative is materially worse.

## Decision

**1. The non-biometric baseline is specified first, and the biometric path is layered on top.**
This inverts the intuitive ordering deliberately. Because the refusal path must be *equally valid*,
it carries the same evidentiary weight requirement and cannot be a degraded fallback — so it is
built as the baseline, and consent to biometrics becomes a genuine choice rather than a formality.

The baseline is: a worker-held secret entered on the capture device, corroborated by the device
key, the position evidence, and a photograph captured at the moment of the event.

**2. Face recognition is the primary factor where consent exists**, matched **on-device and
offline** against a locally cached template, with liveness. Threshold and near-threshold behaviour
are per-company configuration; a near-threshold result produces a lower-confidence record class,
never a refusal. Outdoor and low-light operation is a functional requirement, supported by device
torch or an attached lamp, with the operator told when conditions are inadequate.

**3. Verification codes are excluded from routine check-in.** They are used only for enrolment-time
identity binding, account recovery and alert delivery. Two independent reasons: they require
connectivity the site does not have, and at launch volume — roughly 22,000 events a month —
per-message cost would consume a large fraction of platform revenue.

**4. Buy the liveness, do not build it.** Presentation-attack detection is the hard part of this
problem and the part an inspector or opposing expert will probe. The intent is to license a
commercial on-device SDK meeting: fully offline operation, independently certified presentation-
attack detection, Android and iOS, and template-only output. It sits behind the pluggable interface
so it can be replaced, and the liveness method version is recorded on every record so historical
records remain attributable to the method that produced them. Vendor selection and licensing cost
require quotes and are not settled here.

**5. Templates, never images.** A template is non-reversible and adequate only for matching.
Templates are cached on-device solely for workers currently in that device's scope, encrypted under
a hardware-backed key, and removed when a worker leaves scope. They are never exported, never
shared across companies, and never leave the tenant boundary. A raw check-in image is retained only
where a company explicitly enables it for dispute resolution, under a stated period visible to the
Admin and disclosed to the worker; the default is not to retain.

**6. Nothing ever blocks a worker from being recorded.** A liveness failure, a failed match, a
missing fix, an unenrolled worker — each falls through to a lower record class or to a supervisor
attestation with a mandatory *desviación*. Refusal to record is not an available outcome.

**7. Record class carries the difference.** `VERIFICADO_BIOMETRICO`, `VERIFICADO_SECRETO`,
`VERIFICADO_DEGRADADO` and `ATESTIGUADO` are assigned by the system from the factors actually
collected, never chosen by a user, and are visible on the *lista* and in every export. An
`ATESTIGUADO` record requires an associated *desviación*. Concentrations of weak classes by
supervisor or site are reported and reviewed — this, not the factor design, is what addresses
buddy punching by the person holding the device.

## Consequences

**Positive.** The LFPDPPP refusal path is a first-class path rather than an afterthought, which
removes the coercion argument. Evidence quality is graded and disclosed rather than averaged. No
worker is ever turned away. Messaging cost stays inside its target.

**Negative.** Two capture paths to build, test and support. A commercial SDK is a recurring
per-device or per-worker licence and a supply-chain dependency, and its cost is unquoted. Workers
who both decline biometrics and forget their secret fall to `ATESTIGUADO`, which is the weakest
class — an operational reality to manage, not a defect to hide.

**Neutral.** Face match quality outdoors will vary; the graded record class is how that variation
is expressed rather than suppressed.

## Alternatives considered

**Face plus SMS/WhatsApp OTP plus password**, the original working preference. The OTP factor is
inconsistent with the offline mandate and unaffordable at volume, so it is retained only for
enrolment and recovery.

**Fingerprint.** Excluded on the population.

**Cards, tags, QR badges.** Excluded — transferable by design, which defeats the single guarantee.

**Building face matching and liveness in-house.** Matching is tractable; certified liveness is not,
and an uncertified anti-spoofing claim is one that will be tested in a hearing.

## Revisit triggers

- SDK licensing that proves unaffordable at the small-plan price point.
- STPS *disposiciones generales* prescribing or prohibiting a method.
- A materially higher refusal rate than assumed, which would make the baseline path the common one
  and change where optimisation effort goes.
