# ADR-0003 — Offline trusted time

- **Status:** Accepted
- **Date:** 2026-08-18
- **Source:** PRD §8.7; brief §4; decision `B1`
- **Satisfies:** `FR-445`–`FR-453`, `FR-820`, `INV-011`
- **Related:** ADR-0002 (integrity chain), ADR-0004 (device platform)

## Context

Capture happens offline, sometimes for days. The device clock is settable by whoever holds the
device, and the person holding it works for the party with the motive to change it. A timestamp
presented as authoritative when it came from an attacker-controlled clock is worse than no
timestamp, because it invites the whole record to be discredited in cross-examination.

## Decision

**Offline clock tampering cannot be prevented. It is bounded, detected, and disclosed.** That
framing is the decision; the six mechanisms below implement it.

**1. Anchored interval — the load-bearing mechanism.** Every offline record is bracketed by
`t_lower`, the last server-signed time beacon the device held before losing connectivity, and
`t_upper`, the server-received time at sync. The record is provably within that interval whatever
the device clock says. The device refreshes the beacon opportunistically whenever connectivity
appears, tightening `t_lower`.

**2. Monotonic evidence.** Each record carries the platform's monotonic elapsed-realtime counter,
which the user cannot set, plus a per-boot identifier so power cycles are explicit rather than
silent gaps. Wall-clock deltas that disagree with monotonic deltas mean the clock moved.

**3. GNSS time.** Where a satellite fix exists, the GNSS-derived time is recorded alongside the
device clock. It is atomic-clock-derived, requires no connectivity, and is the strongest offline
source available. It is opportunistic: indoors and in canyons there is no fix, and its absence is
never a failure.

**4. In-app monotonicity.** The application refuses to write a record dated before the last record
it holds, so backdating inside the app is impossible without compromising the device.

**5. Chain ordering.** The per-device hash chain (ADR-0002) makes reordering and insertion
detectable regardless of claimed times.

**6. Cross-device corroboration.** Where several devices operate at one site, their synced
timelines are compared; a device inconsistent with all the others is a review item.

**Disclosure is mandatory.** Both the device-claimed time and the anchored interval appear on the
*lista de asistencia*, in the STPS export and in the verification bundle. A record whose claimed
time falls outside its interval, or whose monotonic evidence is contradictory, carries a permanent
integrity flag. It is never silently corrected and never silently accepted.

## Consequences

**Positive.** Every offline record carries a provable time bound rather than an assertion. A
record that says *"captured offline, device time T, monotonic evidence consistent, GNSS agrees
within 2s, synced T+6h"* is stronger under expert examination than one that simply asserts T,
because it survives the obvious question instead of avoiding it.

**Negative.** Time precision degrades with the length of the offline period, and we must say so
rather than hide it. Some clients will read the disclosure as a weakness; the counter is that the
alternative is a claim that collapses the first time it is challenged. A long-offline device
produces a wide interval, which is a real limitation of the physics, not of the design.

**Neutral.** GNSS availability is site-dependent and cannot be relied on as the primary mechanism,
only as corroboration when present.

## Alternatives considered

**Trust the device clock.** Free, and indefensible. One demonstration of a changed clock in a
hearing discredits every record the product ever produced.

**Refuse to capture while offline until time can be verified.** Would prevent the worker from
being recorded, which violates the product's central posture (PRD §2.1) and is exactly the outcome
the law is trying to prevent.

**Server-side time only, assigned at sync.** Simple and honest, but it throws away the device's
own evidence and makes every offline record's time useless for the purpose it exists for.

**Dedicated hardware secure clock (RTC in a tamper-resistant module).** Strongest, and incompatible
with the no-dedicated-hardware constraint (ADR-0004).

## Revisit triggers

- A *peritaje* or tribunal that rejects an interval-bounded timestamp, which would force a
  hardware conversation.
- Platform APIs exposing a trustworthy attested clock, which would tighten intervals substantially.
