# ADR-0004 — Capture channels and device platform

- **Status:** Accepted
- **Date:** 2026-08-18
- **Source:** PRD §8.1, §8.11; brief §4; decision `B1`
- **Satisfies:** `FR-401`–`FR-406`, `FR-475`–`FR-483`
- **Related:** ADR-0005 (authentication factors), ADR-0006 (application shell)

## Context

Construction sites destroy or steal fixed equipment, have no reliable connectivity, and employ
workers with damaged fingerprints and few phones. Offices, clinics and plants have none of those
problems and some already own terminals. The product must serve both without becoming two
products.

The smallest plans exist for practices with a handful of employees, where any hardware cost,
logistics burden or RMA obligation on our side would exceed the account's entire margin.

## Decision

**1. A capture channel is the unit of pluggability.** All channels produce the same evidence
envelope — device signature, factors used, position, time anchors, record class — and differ only
in which factors are available and how much weight each carries. Adding a channel changes no other
part of the system.

**2. Supervisor-mediated capture is the shipping default.** The supervisor's device holds the crew
roster for their org subtree, captures each worker at the *frente*, works fully offline, and syncs
later. Workers need no phone and no account.

**3. Kiosk mode is the answer for fixed locations, and it is the same application.** A wall-mounted
tablet or a retired phone in kiosk mode. The client buys the device once; we ship one codebase. Its
trust profile differs usefully: no per-worker device binding, so the worker factor carries more
weight, but a fixed known location, so position corroboration carries more.

**4. Worker self-service is opt-in and for office staff.** It contradicts the construction
constraints and is never the default there.

**5. Terminals are an ingest contract, not a product.** A network-connected terminal pushes signed
events directly to our API. No file exports, no middleware, no reconciliation landing on the
client. A terminal that cannot meet this is not supported.

**6. NEO does not sell, ship, stock or warranty hardware.** At the smallest plan's revenue a
terminal's capex, logistics and RMA obligations exceed the account. Clients who want a fixed device
use kiosk mode; clients who already own terminals integrate them.

**7. Device capability floor.** A qualifying capture device provides hardware-backed key storage, a
camera adequate for liveness, a monotonic system clock, and a remote-attestation mechanism. This is
a capability floor, not a preference, and it is published as a minimum device specification forming
part of the client contract.

**8. Platform support.** Android is the v1 primary — it meets the floor, exposes raw GNSS, permits
distribution outside an app store, and offers the cheapest qualifying hardware. iOS follows at
v1.x. **KaiOS is excluded** because it provides neither hardware-backed keys nor a camera pipeline
adequate for liveness; this is a capability exclusion, not a cost one. **HarmonyOS NEXT is
excluded** as a distinct build, though older Huawei devices running the Android build are supported
normally.

**9. Attestation happens at sync, not at capture**, because capture is offline. The device key
signs at capture; attestation at sync binds that key to an unmodified application on a genuine
device. Attestation failure flags the batch; it never discards it.

## Consequences

**Positive.** One hardened offline path to build and support. No hardware business. The channel
abstraction means clinics, plants and construction are the same product. A client can change how
they capture without changing anything about how their records are stored or exported.

**Negative.** The supervisor sits inside the trust boundary and is the classic buddy-punching
vector; this is handled by record classes and mandatory *desviaciones*, not by the channel design
(ADR-0005). Requiring a qualifying device pushes a real cost onto clients, which must be said
during the sale rather than discovered at deployment. Excluding KaiOS closes the door on the very
cheapest handsets.

**Neutral.** Terminal support depends on vendors offering a push mechanism; those that cannot are
simply out of scope.

## Alternatives considered

**Worker self-service as the primary channel.** Removes the supervisor from the trust path, and
fails the stated constraints: low-end phones, many workers with no phone, no connectivity.

**NEO-branded terminal.** A differentiator, and a margin and support trap at this ARPU.

**Web-only capture with no device requirement.** Cheapest to deliver and cannot produce
evidence-grade records; see ADR-0006.

## Revisit triggers

- A client segment where a supervisor device is genuinely impossible.
- iOS demand from construction clients, which would move iOS forward from v1.x.
- A terminal vendor with meaningful installed share among target clients.
