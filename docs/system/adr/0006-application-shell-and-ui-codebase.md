# ADR-0006 — Application shell and UI codebase

- **Status:** Proposed
- **Date:** 2026-08-18
- **Source:** PRD §8.10; decision `B6`; `OQ-033`
- **Satisfies:** `FR-484`–`FR-490`
- **Related:** ADR-0004 (device platform), ADR-0003 (trusted time)

## Context

There are two audiences with different form factors. Admin, *Recursos Humanos* and both accountant
roles do seated keyboard-and-screen work — *expediente* management, IDSE review queues, reports,
dashboards, billing. Supervisors work one-handed, outdoors, in a hurry, offline.

The stated approach is to build a progressive web application first and package it into native iOS
and Android containers. That sequencing is right for the UI. The question this ADR settles is
whether the container is a later packaging step or a v1 requirement.

## Decision

**1. One web UI codebase, two shells.** A desktop-oriented web application for administrative
users, and a native container for the capture application.

**2. The native container is a v1 requirement for the supervisor application, not a packaging step
at the end.** Five requirements in the PRD are unreachable from a browser:

| Requirement | Why a browser cannot satisfy it |
|---|---|
| Hardware-backed signing key, attestation | Web Crypto keys are non-extractable but not hardware-backed and not attestable; Play Integrity and App Attest have no web equivalent |
| GNSS time, mock-location detection | The Geolocation API returns a fix and nothing else — no satellite time, no raw measurements, no mock flag |
| Boot-scoped monotonic clock | `performance.now()` resets on reload, so cross-restart clock tampering becomes undetectable |
| Durable 7-day offline retention | Browser storage is evictable under pressure and, on iOS, cleared after disuse. **Losing unsynced *jornada* records is the one unrecoverable failure in this product** |

**3. Security-critical capabilities are native plugins, not web APIs.** Key storage, attestation,
camera and liveness, geolocation and GNSS, monotonic clock, and record storage.

**4. The camera, liveness and match screen is a native view, not a webview screen.** It is the hot
path, it runs many times a minute at shift change, and webview camera performance on low-end
Android is the predictable failure. Everything else — rosters, forms, queues, confirmation — is
shared web UI.

**5. Unsynced records and cached templates live in application-owned native storage** that the
operating system will not evict. Never in browser-managed storage.

**6. A browser-only progressive web application remains supported for online-only surfaces**:
worker self-service on office networks and kiosks with permanent connectivity where records sync
immediately. Records captured there lack hardware key binding and attestation and are classified
accordingly; they are never presented as equivalent. **The browser-only path must not be used for
offline capture.**

**7. Container framework selection favours wrapping the same web build with native plugin access**
over a framework that would require reimplementing the UI. The specific framework and plugin set
are to be chosen against the constraints above, together with the distribution path for Android
sites with no app-store access.

## Consequences

**Positive.** One UI codebase and one design system across every surface. Administrative screens
get the desktop treatment they need. The capture application gets the native capabilities its
evidence claims depend on. Sequencing survives: the web build genuinely comes first and the
container wraps it.

**Negative.** The plugin layer is real native work on two platforms and is not a thin wrapper.
Webview performance on low-end Android needs measuring early, and the native camera view is the
mitigation. App store review becomes a release dependency for the mobile surface, so a fix that is
instant on the web takes days on mobile — offline behaviour must therefore degrade safely without
an update (`NFR-402`).

**Neutral.** The browser-only path exists but is deliberately second-class, which needs to be said
plainly in sales conversations rather than discovered later.

## Alternatives considered

**Browser-only PWA for everything.** Cheapest and fastest, and it cannot produce evidence-grade
records. Rejected on the table above — in particular storage eviction, which loses data rather than
merely weakening a claim.

**Separately written native mobile application.** The best mobile result, at the cost of a second
UI codebase. Not affordable at this team size and revenue.

**Thin trusted-web-activity wrapper.** Ships the browser's limitations inside an app icon and
provides none of the native capabilities. Rejected.

## Revisit triggers

- Webview performance measurements on the target low-end device failing the shift-change throughput
  the supervisor flow needs.
- Web platform APIs delivering attestable hardware keys and non-evictable storage, which would
  reopen the browser-only question for offline capture.
