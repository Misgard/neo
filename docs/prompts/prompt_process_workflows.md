# Prompt — NEO process and user workflows

## 0. Role and mission

**Read `docs/prompts/common/` in full before anything else** — `00-context.md`, `01-method.md`,
`02-conventions.md`. They carry the product context, the working method and the conventions that
apply to every design session in this repository, including the rule on uncertainty, the
blocking/non-blocking question format, the reserved requirement identifier ranges and the ADR
template. This prompt carries only what is specific to this task.

You are the **lead product architect** for this block. You are designing the processes and user
workflows that the PRD describes only in prose.

**Read closely for this task:** PRD §5 (the sixteen user journeys), §4 (permission model), §6 in
full, §8 (capture), and ADR-0004, ADR-0005 and ADR-0006.

---

## 1. The gap this fills

PRD §5 contains seventeen user journeys written as prose happy paths, of which `UJ-00` — the life
of an *obra*, from contract through the five-*día hábil* window to closure — is the one every other
sits inside. They establish *what* happens. They do not establish:

- **State machines.** Most objects in this system have a lifecycle that the PRD names but never
  enumerates — it says "enters a review queue" without saying what states the queue has, who moves
  an item between them, or what happens when nobody does.
- **Failure and exception paths.** The PRD's central posture is *never block, always record, always
  document the deviation* (§2.1). That posture is only real if every failure path is designed. An
  undesigned failure path becomes a blocked worker.
- **Offline transitions.** What each flow looks like when connectivity disappears halfway through,
  and what the operator sees.
- **Queue and hand-off design.** Who sees what, in what order, with what escalation, and what the
  queue looks like when it has two hundred items in it.
- **Throughput.** See §3.

---

## 2. Objects whose lifecycle must be specified

Produce an explicit state machine for each, with states, transitions, the actor authorised for each
transition, and the terminal states. Where a transition can fail, say what the failure state is.

**Employment and people.** `RELACION_LABORAL` · documentation tier progression, identity-only
through complete *expediente* (`FR-341`) · provisional employee completion · duplicate candidate ·
document expiry.

**The *obra*.** `CENTRO_TRABAJO` through **both** compliance windows — the opening window from
*fecha de inicio físico* and the dependency-ordered closing cascade (`FR-227`, `FR-228`) ·
`REGISTRO_PATRONAL` registry row from unevidenced to evidenced to end-dated · SIROC registration
from pending through registered to closed (`FR-653`).

**Capture and the day.** `JORNADA` record and its corrections · correction request · overtime
authorisation · *desviación* · the daily roster, including a worker present but not on it
(`FR-1354`) · **expected/observed conflict** from raised through verification to disposition
(`FR-1366`–`FR-1375`) · the **active-*incapacidad* sequence** specifically: check-in, verification
requested, either outcome, check-out or escalation (`FR-1376`–`FR-1380`).

**IMSS artifacts.** `ARCHIVO_IDSE` ingestion · *movimiento* match · `MOVIMIENTO_RECHAZADO`
(`FR-633`, `FR-647`) · *alta de registro patronal* ingestion.

**Reporting and platform.** `LISTA_ASISTENCIA` including reissue after late corrections · *periodo*
close and delta reporting · alert from raised through acknowledged, escalated, breached and
resolved · CFDI from issued through cancellation and receiver acceptance (ADR-0014) · referral ·
ARCO request · break-glass session · device from enrolled through active, unsynced, stale and
revoked.

---

## 3. The throughput problem — quantify it before designing the flow

Nobody has yet stated how long a check-in may take. It is a hard product constraint and it governs
the entire capture flow.

A crew of 200 through one device at shift change: at eight seconds per worker that is 27 minutes of
queue. Establish the target seconds-per-worker with the client, then design the capture loop
against it. Specifically:

- What the supervisor does while a queue of workers is waiting.
- What happens when one worker fails verification — the queue must not block; they are set aside
  and handled after, not in front of an audience.
- Whether several workers can be captured in one continuous flow without returning to a menu.
- Whether a second device at the same gate is supported, and how the two reconcile.
- Mid-flow interruptions: an unenrolled worker appearing, a *desviación* needing registration, a
  battery warning, a phone call.

---

## 4. The worker's experience

The worker is not a user, but they stand in front of the device and the record is about them.
Design what they see and hear, given: low literacy is common, the site is noisy, there is sun
glare, hands may be gloved or dirty, and the worker may be sceptical that the system is fair to
them.

Cover the confirmation that a check-in succeeded — it must be unmistakable without reading —
the refusal path for a worker declining biometrics (ADR-0005), consent capture at field enrolment,
and what a worker is told when their check-in produces a flagged or `ATESTIGUADO` record.

---

## 5. Workflows to design, by persona

**Supervisor (mobile, offline).** The daily roster and who is missing (`FR-1350`–`FR-1354`) ·
daily capture loop · field hiring mid-shift · break and check-out · **an expected/observed
conflict at the gate**, including the active-*incapacidad* verification sequence, which is the
hardest flow in the product and must be designed for an offline site with RRHH unreachable
(`FR-1380`) · registering a *desviación* and attaching signed documentation · capturing an
*incidencia* at source (`FR-1355`) · requesting overtime authorisation · requesting a correction ·
signing the *lista* · the *altas ante el IMSS* export for a crew · sync, including a sync that
partially fails.

**Recursos Humanos (desktop).** Bulk employee load and its error queue · completing a provisional
employee and advancing its documentation tier · resolving duplicates · uploading an IDSE PDF and
working the match review queue, including a document refused as another *patrón*'s (`FR-646`) ·
supplying the data for a SIROC submission the client will file (`OQ-036`) · managing the
*expediente* and expiry alerts · registering and correcting absence exceptions, including a
correction over a day that already carries a conflict (`FR-846`) · **responding to a supervisor's
verification request** (`FR-1380`) · approving corrections · working the IMSS exposure
dashboard.

**Admin (desktop).** Company onboarding, from signature to first check-in on the same day,
including the fiscal identity CFDI 4.0 requires before the first invoice (`FR-962`) · the
*registro patronal* registry and its evidencing documents · `CENTRO_TRABAJO` structure and its
type vocabulary and capabilities (`FR-217`) · **opening an *obra***: physical start, then the
dependency-ordered window of *registro patronal*, SIROC and IDSE (`FR-226`) · **closing an
*obra***: the cascade of operational *bajas*, IMSS *bajas* and SIROC closure as one checklist
(`FR-228`) · users and grants · alert lead times and escalation ladders · billing, entitlement
overage and the referral surface · producing an STPS export and a verification bundle under time
pressure.

**Contador interno and externo (desktop).** *Periodo* close · the *incidencias* hand-off · the
external accountant's portfolio switcher, which must never merge two clients into one view.

**Staff NEO (desktop).** Tenant health monitoring · break-glass elevation with second-person
approval · supporting a client without the ability to write to any evidentiary record.

For each: the trigger, the preconditions, the steps, the decision points, the exception paths, what
is logged, and what the user sees when it goes wrong.

---

## 6. Cross-cutting flows

- **Onboarding a construction client end to end**, including enrolling several hundred faces at a
  site with no connectivity. This is the riskiest week of every deployment and the PRD does not
  design it.
- **A labour dispute**, from the claim arriving to handing over the verification bundle.
- **An STPS inspection** arriving on site, unannounced, asking a supervisor for records.
- **A worker revoking biometric consent** and the transition to the baseline path.
- **A crew hired at the identity-only tier** on the day an *obra* starts, and how the gaps close
  over the following days without anyone being turned away (`FR-341`, `FR-342`).
- **The *registro patronal* arriving** after a fortnight of work, and the reviewed bulk assignment
  that backdates every employee to their start at that *centro de trabajo* (`FR-220`).
- **A device lost on site** with unsynced records on it.
- **A client falling delinquent** — capture continues, administrative surfaces degrade.

---

## 7. Out of scope

- Visual design, mockups, wireframes, colour, typography. **Screen inventories and flow diagrams
  only** — the PRD forbids mockups and that still holds.
- Frontend framework selection.
- Re-opening any decided ADR.
- Anything fenced out in PRD §14.

---

## 8. Constraints

1. **Nothing blocks a worker from being recorded.** Every exception path ends in a record, at worst
   a lower class with a mandatory *desviación*.
2. **Offline-first.** Every supervisor flow must be designed for zero connectivity as the normal
   case, not the exception.
3. **Append-only.** No flow may edit an evidentiary record in place.
4. **Two form factors.** Admin, HR and accountants on desktop web; supervisors on mobile
   (ADR-0006). Do not design one responsive flow for both.
5. **Spanish (es-MX) for everything a user reads**; this document and any identifier in English.
6. Alerts never auto-dismiss and always escalate (`FR-813`, `FR-814`).

---

## 9. Deliverables

1. `docs/system/workflows/README.md` — index and reading order.
2. One file per domain under `docs/system/workflows/`: `capture.md`, `employment.md`,
   `expediente.md`, `imss.md`, `evidence.md`, `alerting.md`, `account-and-billing.md`,
   `support-and-access.md`.
3. `docs/system/screens.md` — the screen inventory per persona and per form factor, in prose, with
   the purpose and the primary action of each screen. No mockups.
4. Where a workflow surfaces a requirement the PRD lacks — and it will — **add it to the PRD** in
   this track's reserved ranges and list every addition in your summary. Where it contradicts an
   existing requirement, raise it rather than resolving it silently.

**Additional definition of done for this task:** every object in §2 has a state machine showing its
failure states; every flow in §5 has its exception paths designed, not only its happy path.

---

## 10. A note on method

This is the part of the design that benefits most from contact with reality. A day spent at an
*obra* watching a supervisor run a shift change, and an hour with the HR person who will actually
work the IDSE review queue, will produce better workflows than any amount of desk design — and
will surface the throughput number in §3 immediately. Recommend that before you finalise the
capture loop.

---

## Start here

Open as `docs/prompts/common/01-method.md` specifies: your understanding in five sentences or
fewer, your blocking questions with options and recommendations, your non-blocking questions
listed only, and anything in the PRD or the ADRs that looks wrong or inconsistent in light of what
you now have to decide.

On the fourth item: tracing a prose journey through its actual states and failure paths is what
finds contradictions in a specification. Look hard — it is the most valuable thing this session
produces.

Wait for answers before writing.
