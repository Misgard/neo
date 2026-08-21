# Screen inventory

*Living document. Requirements live in [`prd.md`](prd.md); the flows these screens serve are
designed in [`workflows/`](workflows/).*

**Scope.** Screen inventory only — purpose and primary action per screen, per persona, per form
factor. **No mockups, no wireframes, no visual design, no framework choice**; those are fenced out
by PRD §14.3 and by ADR-0006, which deliberately leaves the framework open (`OQ-033`).

**Two form factors, not one responsive layout** (§8.10, ADR-0006):

| Surface | Users | Form factor |
|---|---|---|
| **Capture application** | Supervisors in the field, workers at a kiosk | Mobile, offline-first, native container |
| **Administrative console** | Admin, RH, both accountant roles, NEO staff | Desktop-oriented web |

**Every string a user reads is Spanish (es-MX)** (`FR-013`). Screen names below are English
identifiers for this document, not UI copy.

**One rule governs the capture application's layout and is worth stating before the inventory:** a
screen the supervisor needs during a shift change must be reachable **without leaving the capture
flow** (`FR-2060`). Anything that returns them to a menu costs the gate its throughput, so the
exception paths below are surfaces layered over the capture screen rather than destinations away
from it.

---

## 1. Capture application — supervisor

### The shift

| Screen | Purpose | Primary action |
|---|---|---|
| **Unlock** | Release the operator capability and the device signing key, offline (`FR-1423`) | Unlock |
| **Session start** | Declare the *centro de trabajo* from the device's scope (`FR-2001`) | Confirm the *obra* |
| **Daily list** | See who is expected and **who is missing** (`FR-1351`) — the screen the supervisor works from | Start capturing |
| **Capture** | The hot path. Camera, liveness, match, position, sign (`FR-2060`) | Capture the next worker |
| **Confirmation** | Tell the worker, unmistakably and without reading, that they were recorded (`FR-2094`) | Auto-advance to the next worker |
| ***Pendientes*** **lane** | Everyone set aside, worked after the queue (`FR-2061`, `FR-2062`) | Resolve or register a *desviación* |
| **Session close** | Show everyone still checked in or on break before the day ends (`FR-2038`) | Close, or leave open deliberately |

The **daily list** carries the live state per person and the count in each — not yet seen, checked
in, on break, checked out, set aside (`FR-2005`) — and states plainly that it is a working tool
(`FR-2000`). Adding somebody is one entry point that resolves into a list action or into field
enrolment without the supervisor choosing (`FR-2006`); removing somebody asks why, and the answer
decides whether it is a list action or a proposed *baja* (`FR-2007`).

### Exceptions, layered over the capture flow

| Screen | Purpose | Primary action |
|---|---|---|
| **Field enrolment** | Create a worker at the gate: name, photograph, face or secret, consent (`FR-330`, `FR-331`) | Enrol and capture |
| **Consent and *aviso*** | Show the versioned texts and take the affirmative action, offline (`FR-332`) | Consent, or decline |
| **Conflict warning** | Name the expected state — *this worker is recorded as on vacaciones* (`FR-1365`) | Proceed; both facts are kept |
| ***Incapacidad*** **sequence** | Type, dates, source, the stakes both ways, and the *patrón*'s standing instruction verbatim (`FR-2095`, `FR-2096`) | Request verification |
| **Verification status** | Who was contacted, by what means, when, with what result (`FR-2097`) | Record the decision and its basis |
| **Presence record** | A person with no open relationship is here (`FR-2090`) | Capture anyway; route to RH |
| **Duplicate or re-entry** | A second *checada* in the same direction on this device (`FR-2068`) | Say which it is |
| ***Desviación*** | Type, cause in the reporter's own words, witness block, evidence (`FR-1332`, `FR-2130`) | Register and link to the records it explains |
| **Witness capture** | Name the witness and their mode; capture a signature or attach contact evidence (`FR-2133`, `FR-2134`) | Attach |
| **Correction request** | Raise a correction from the field, queued offline (`FR-2163`) | Submit |
| **Overtime request** | Request authorisation at the moment it is needed (`FR-1310`, `FR-1313`) | Submit |
| ***Incidencia*** **at source** | Record what happened to a worker, with what the responsible role must now do (`FR-1355`, `FR-1357`) | Record and notify |

### Between shifts

| Screen | Purpose | Primary action |
|---|---|---|
| **Sync status** | Unsynced count, oldest record age, time offline (`NFR-405`) | Sync now |
| **Sync result** | What was accepted, what carries a flag and why, what now waits (`FR-469`) | Open the item |
| **My queue** | Scope reviews, unlinked *desviaciones*, open *jornadas*, unresolved conflicts | Work the top item |
| **Reminders** | Approaching break, end of *jornada*, *jornada máxima* — evaluated on the device (`FR-1302`, `FR-1303`) | Acknowledge |
| ***Altas ante el IMSS*** | Prove this crew is hired and insured, for exactly this subtree (`FR-615`) | Export |
| **Operator handover** | End the outgoing capability, authenticate the incoming operator (`FR-1430`) | Hand over |
| **Device status** | Storage envelope, battery, capability age, last contact (`NFR-940`) | — |

---

## 2. Capture application — kiosk and worker self-service

A kiosk has **no operator identity at all** (`FR-1477`), so it has no session screen, no queue and no
supervisor surfaces. It has four screens and a named *responsable* who receives everything it cannot
resolve (`FR-2093`).

| Screen | Purpose | Primary action |
|---|---|---|
| **Idle** | Invite the next person. Large, legible across a room | Present |
| **Capture** | Face or secret, with position corroborating a fixed known location | Capture |
| **Confirmation** | Unmistakable success or failure without reading (`FR-014`) | Auto-return to idle |
| **Exit kiosk mode** | Authenticate a principal holding that permission (`FR-1478`) | Authenticate |

Where no worker-bound factor succeeds and nobody is present to attest, the record is
`AUTODECLARADO` and the platform raises the *desviación* to the *responsable* (`FR-2092`). The worker
sees the ordinary confirmation; the exception is somebody else's screen.

---

## 3. What the worker sees

The worker is not a licensed user at v1 (`OQ-014`) and has no account, but three surfaces are theirs.

| Surface | Purpose |
|---|---|
| **Confirmation at capture** | A full-screen state, their own photograph and name, a sound audible on a site, and a haptic pulse. Distinguishable across two metres in glare by somebody who reads nothing (`FR-014`). It says **nothing** about record class, flags or conflicts (`FR-2094`) |
| ***Aviso de privacidad*** **and consent** | The versioned texts, before the affirmative action, in Spanish, offline (`FR-1107`, `FR-332`) |
| **The printed *lista*** | Their whole *periodo*, row by row, which they sign or dispute in writing (`FR-2192`, `FR-2194`) |

The third is where a worker actually reviews their record. The gate is deliberately not that place:
a queue of two hundred is the wrong setting to contest a day, and a badge reading `ATESTIGUADO` in
front of an audience helps nobody.

---

## 4. Console — *Recursos Humanos*

| Screen | Purpose | Primary action |
|---|---|---|
| **Work queue** | Every RH queue in one place, ordered by breach proximity (`FR-2232`) | Work the top item |
| **Employee list** | Find a person; see tier, assignment, affiliation and exposure at a glance | Open a person |
| **Employee record** | One person's whole history: relationships, contracts, wages, assignments, *NSS* values (`FR-314`, `FR-2300`) | Edit the *expediente* |
| ***Expediente*** | Documents by category and version, with expiry and sensitivity (`FR-303`–`FR-306`, `FR-1448`) | Upload a version |
| **Bulk load** | Map columns, apply valid rows, queue the rest (`UJ-02`) | Apply |
| **Bulk load errors** | Work failed rows without re-uploading | Correct and apply |
| **Provisional completion** | Field-enrolled people awaiting an *expediente*, with the age of each (`FR-335`) | Complete |
| **Duplicate review** | Two records, side by side, with both enrolment photographs (`FR-336`) | Merge, or dismiss |
| **IDSE upload** | Upload the artifact the portal returned (`FR-601`) | Upload |
| **IDSE file detail** | Classification, cross-foot result, *Patrón* blocks, parsed rows and rejections (`FR-624`, `FR-633`) | Commit, or hold |
| **Match review** | Unmatched and proposed *movimientos* (`FR-608`) | Confirm, or attach a further *NSS* (`FR-2382`) |
| **Held constancias** | Documents failing the tenant check, with the path that clears each (`FR-646`) | Add the registry row, or refuse |
| **Rejected *movimientos*** | Workers the IMSS refused, with their clocks still running (`FR-833`) | Mark cured, or record a reason |
| **Exposure dashboard** | Every worker whose two lifecycles disagree, with days elapsed and escalation state (`UJ-09`) | Open the person |
| **Absence exceptions** | Register and correct *vacaciones*, *incapacidades*, *permisos* (`FR-1361`) | Register |
| **Conflicts** | Employee-days where expected and observed disagree (`FR-1366`) | Dispose, with a reason |
| **Verification requests** | A supervisor at a gate is waiting on an answer, now (`FR-1380`) | Answer |
| **Corrections** | Requests awaiting approval, with what each one changes (`FR-502`) | Approve, or reject |
| **SIROC data** | What each notice needs, as an export the client files (`OQ-036`) | Export |
| **ARCO requests** | Requests against their response deadline (`FR-1105`) | Resolve |

**Verification requests** is the one screen on this surface with a human standing at the other end of
it. It is surfaced with more urgency than anything else RH holds, because the alternative outcome is
a supervisor deciding alone at a gate (`FR-2097`).

---

## 5. Console — Admin

| Screen | Purpose | Primary action |
|---|---|---|
| **Company dashboard** | Headcount against capacity, running billable count, exposure, breaches, adoption (`FR-901`–`FR-908`) | Open a breach |
| **Onboarding checklist** | What remains and what each item blocks (`FR-2440`) | Complete an item |
| **Company profile** | Legal identity, and the fiscal identity CFDI 4.0 requires (`FR-962`) | Save |
| ***Registro patronal*** **registry** | One row per *registro patronal*, evidenced or flagged (`FR-210`, `FR-213`) | Add a row |
| ***Centro de trabajo*** **structure** | The tree, its type vocabulary and each type's declared capabilities (`FR-201`, `FR-217`) | Add or edit a node |
| ***Obra*** **opening checklist** | The dependency-ordered window rooted at the *registro patronal* (`FR-2341`) | Record an artifact |
| ***Obra*** **closing checklist** | The cascade as one unit, listing who remains outstanding by name (`FR-2342`) | Record a *baja* or a closure |
| **Org chart** | Supervision, which resolves `ORG_SUBTREE` (`FR-103`) | Move a node |
| **Users and grants** | Who holds what, where (`FR-101`) | Invite, or revoke |
| **Roles** | System role templates and the tenant's clones (`FR-1441`, `FR-1442`, `OQ-046`) | Clone and edit |
| **Delegated access** | *Contador externo* grants, with the affirmation the *expediente* requires (`FR-1467`) | Grant, or revoke |
| **Device fleet** | Enrolled, active, unsynced, stale, purged, revoked, with the age of each (`FR-2471`) | Enrol, or revoke |
| **Device revocation** | On revoking, the size of the residual exposure at that moment (`FR-2472`) | Confirm |
| **Alert configuration** | Lead times, routing, escalation ladders, channels, per type (`FR-810`–`FR-815`) | Save |
| **Rule sets** | *Jornada* rules by assignment level, with the declared legal basis of any non-default one (`FR-077`, `FR-078`) | Assign |
| ***Instrucción permanente*** | The *patrón*'s own standing instruction, shown verbatim to an offline supervisor (`FR-2095`) | Publish a version |
| **Compliance file** | Third-party agreements, *aviso* versions, consent texts (`FR-1468`) | Upload |
| ***Listas de asistencia*** | Every *periodo*'s document and its state in the signature cycle (`FR-2190`) | Issue, or upload the scan |
| **Exports** | STPS, *incidencias*, audit log, verification bundle (`FR-710`, `FR-530`) | Generate |
| **Audit log** | The company's own log, readable and exportable (`FR-1106`) | Export |
| **Billing** | Subscription, invoices, CFDIs, referrals (`FR-904`–`FR-906`) | Pay, or download |
| **Legal hold** | Place and release a hold, with a reason (`FR-1112`, `OQ-030`) | Place |
| **Break-glass notices** | Sessions opened against this tenant and what was touched (`FR-1203`) | Review, or revoke |

---

## 6. Console — *contador interno*

Deliberately small. Read-only against *jornada* and *incidencias*, no *expediente* beyond the
identity fields payroll needs (§4.2.4).

| Screen | Purpose | Primary action |
|---|---|---|
| ***Periodo*** **list** | Periods, their close state, and any deltas issued (`FR-727`) | Open a *periodo* |
| ***Incidencias*** **report** | Classified time, with conflicts shown as conflicts (`FR-1368`) | Export |
| **Deltas** | What changed after the hand-off, and why (`FR-729`) | Export |
| **Attendance detail** | The records behind a line, traceable back (`FR-726`) | Trace |
| **Conflicts for this *periodo*** | Days about to be paid where the two statements disagree (`FR-844`) | Raise to RH |

---

## 7. Console — *contador externo*

| Screen | Purpose | Primary action |
|---|---|---|
| **Portfolio** | Every company that has granted access, and nothing about any other (`FR-122`) | Enter a company |
| **Company workspace** | Whatever the granting Admin's chosen role permits (`FR-1459`) | — |
| **My billing** | Their own subscription and partner fees. The only permitted combined view (`FR-122`) | Download |
| **Referrals** | Funnel state and cumulative earnings, and nothing else (`INV-030`) | Invite |

Entering a company is a **context switch, never a merge** (`FR-122`, `INV-001`). The portfolio is
composed from one single-tenant request per company above the data layer (`FR-126`), and every access
is written into that company's own audit log where its Admin can see it (`FR-124`).

---

## 8. Console — NEO staff

| Screen | Purpose | Primary action |
|---|---|---|
| **Tenant health** | Accounts, plan, seats, metered employees, billing state, sync health, accounts at risk (`FR-950`) | Open an account |
| **Account detail** | Control-plane data only. No worker personal data (`FR-951`) | — |
| **Break-glass request** | Reason from a controlled list, bounded window, target company (`FR-1201`) | Request |
| **Break-glass approval** | Approve a colleague's request, or route it to the client's Admin (`FR-1461`) | Approve |
| **My action history** | The staff member's own actions, from the control-plane mirror (`FR-1463`) | — |
| **Platform health** | Ingest, sync, anchoring, chain verification runs, alert subsystem health (`NFR-602`–`NFR-604`) | — |
| **Referral attribution** | Fees owed, and conflicting claims for review (`FR-1008`) | Resolve a conflict |
| **Reconciliation exceptions** | Charges without a CFDI, or the reverse (`FR-961`) | Resolve |

**There is no screen here that reports per-worker IMSS compliance across clients**, and its absence
is a requirement rather than an omission (`FR-952`). No screen on this surface issues a query
spanning tenants (`INV-001`).

---

## 9. What is deliberately absent

| Not built | Why |
|---|---|
| A worker portal | `OQ-014`, deferred at v1. The *constancia de jornada* (`FR-714`) serves the need through RH |
| Any screen that edits a *jornada* record | The permission does not exist (`FR-1445`, `INV-062`) |
| A NEO staff view of per-worker compliance | `FR-952` |
| An inspector-facing surface on the device | Console only, decided in session. A partial view is what would get handed over under pressure |
| A responsive layout serving both form factors | `FR-484`, ADR-0006 — two shells over one codebase |
| Custom role editor at v1 | `OQ-046`. NEO configures on request in the interim |
