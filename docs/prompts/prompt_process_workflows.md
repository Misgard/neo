# Prompt — NEO process and user workflows

## 0. Role and mission

You are the **lead product architect** for NEO, continuing work already in progress. You are
designing the processes and user workflows that the PRD describes only in prose.

**Read first:** `docs/system/prd.md` in full, then `docs/system/adr/README.md` and every ADR under
`docs/system/adr/`. **The PRD and the ADRs are constraints, not questions.** Where you believe one
is wrong, say so explicitly and separately; do not quietly design around it.

**Hard rule on uncertainty:** if a decision is required and the information is not in those
documents, do **not** invent it. Stop and ask, with at least two options, the trade-off of each,
and your recommendation. Separate *blocking* from *non-blocking* questions and ask the blocking
ones before writing.

---

## 1. The gap this fills

PRD §5 contains sixteen user journeys written as prose happy paths. They establish *what* happens.
They do not establish:

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

`RELACION_LABORAL` · `JORNADA` record and its corrections · correction request · overtime
authorisation · *desviación* · `ARCHIVO_IDSE` ingestion · *movimiento* match · duplicate candidate ·
provisional employee completion · `LISTA_ASISTENCIA` including reissue after late corrections ·
*periodo* close and delta reporting · alert from raised through acknowledged, escalated, breached
and resolved · document expiry · `PROYECTO` from active to complete · referral · ARCO request ·
break-glass session · device from enrolled through active, unsynced, stale and revoked.

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

**Supervisor (mobile, offline).** Daily capture loop · field hiring mid-shift · break and check-out
· registering a *desviación* and attaching signed documentation · requesting overtime authorisation
· requesting a correction · signing the *lista* · the *altas ante el IMSS* export for a crew ·
sync, including a sync that partially fails.

**Recursos Humanos (desktop).** Bulk employee load and its error queue · completing a provisional
employee · resolving duplicates · uploading an IDSE PDF and working the match review queue ·
managing the *expediente* and expiry alerts · approving corrections · working the IMSS exposure
dashboard.

**Admin (desktop).** Company onboarding, from signature to first check-in on the same day ·
*registros patronales*, org chart, *ubicaciones* and *proyectos* · users and grants · alert lead
times and escalation ladders · project completion and its consequences · billing, entitlement
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
4. Where a workflow surfaces a requirement the PRD lacks — and it will — **add it to the PRD** and
   list every addition in your summary. Where it contradicts an existing requirement, raise it
   rather than resolving it silently.

**Reserved identifier ranges.** A parallel session is designing identity and security and will also
be adding requirements to `prd.md`. Use **only** these ranges so the two sets never collide:
`FR-1500`–`FR-1599`, `NFR-1100`–`NFR-1199`, `INV-070`–`INV-079`, `OQ-050`–`OQ-059`. Do not take
"the next free number" — take the next free number *within your range*. If you must touch a
requirement outside your range, note it in your summary as a conflict rather than editing it.

**Conventions:** Mermaid `stateDiagram-v2` for lifecycles, `sequenceDiagram` for multi-actor flows,
`flowchart` for decision trees. Every state machine must show its failure states.

**Definition of done:** every object in §2 has a state machine; every flow in §5 has its exception
paths designed, not just its happy path; every gap is an open question with options and a
recommendation rather than an assumption.

---

## 10. A note on method

This is the part of the design that benefits most from contact with reality. A day spent at an
*obra* watching a supervisor run a shift change, and an hour with the HR person who will actually
work the IDSE review queue, will produce better workflows than any amount of desk design — and
will surface the throughput number in §3 immediately. Recommend that before you finalise the
capture loop.

---

## 11. Start here

Before writing anything, reply with:

1. Your understanding of the task in five sentences or fewer.
2. Your **blocking** questions, in priority order, each with at least two options and your
   recommendation.
3. Your **non-blocking** questions, listed only.
4. Anything in the PRD or the ADRs that looks wrong, risky, or internally inconsistent once you
   trace it through an actual flow — this is what detailed workflow design is best at finding, so
   look hard.

Wait for answers before writing.
