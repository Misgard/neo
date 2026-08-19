# ADR-0008 — Two employment lifecycles, and the metering unit

- **Status:** Accepted
- **Date:** 2026-08-18
- **Source:** PRD §7.3, §6.9.2; decision `B5`
- **Satisfies:** `FR-330`–`FR-338`, `FR-311`–`FR-314`, `FR-802`–`FR-805`, `FR-930`–`FR-938`,
  `INV-020`, `INV-026`–`INV-028`, `INV-040`, `INV-041`
- **Related:** ADR-0009 (IDSE ingestion)

## Context

Construction clients routinely put people to work before any paperwork exists, and file with the
IMSS afterwards. If NEO gates attendance on IMSS status, those workers cannot check in — which is
unacceptable operationally and, worse, pushes exactly the population the law protects back off the
record.

Conversely, if HR registers people who never show up, the client has still used the system to
manage them.

Most construction workers are hired *por obra determinada*. The contract ends when the project
ends, not on a date, and a worker continuing on another project must be given *baja* and rehired.

## Decision

**1. Two independent lifecycles per person, neither derived from nor gating the other.**

- `RELACION_LABORAL` — the operational employment relationship, created by HR or by a supervisor in
  the field. It asserts *this person is working for us*. It drives check-in eligibility, *jornada*,
  the *lista de asistencia*, and billing. It opens on the operational hire date and closes on an
  explicit operational *baja* recorded in NEO.
- `AFILIACION_IMSS` — derived exclusively from ingested IDSE artifacts. It asserts *this person is
  filed with the IMSS under this registro patronal from this date*. It drives the *altas* export,
  the five-day clock and compliance status.

**2. The delta between them is a first-class derived concept — the compliance exposure — and it is
the most valuable thing the system computes.** Four states follow mechanically, three of which are
alerts nobody would specify from a single-lifecycle model: working with no *alta* filed (the
five-day clock running); *alta* filed but never seen at a site; operational *baja* with no IMSS
*baja*; and *jornada* records dated after an IMSS *baja*, which means someone is working uninsured.

**3. Field enrolment is supported offline.** A supervisor can create a provisional employee with
name, photograph, face enrolment or the declared alternative, and biometric consent captured on the
device at that moment. *CURP* and *NSS* are captured if the worker has the documents and are
otherwise deferred. HR completes the *expediente* later; duplicates go to a review queue keyed on
*CURP*, *NSS* and biometric similarity and are never merged automatically.

**4. Contracts *por obra determinada* reference a *proyecto*, and their end condition is that
project's completion, not a calendar date.** Project completion is an explicit dated act, never
inferred from the calendar, because the legal consequence is too large to trigger by assumption. A
completed project with open relationships against it is a breach state. A worker moving to another
project is a new `RELACION_LABORAL` against the same `EMPLEADO`, so the person's history stays on
one identity.

**5. The billable unit is the employee-month, defined as the maximum over any day of the month of
the count of distinct employees with at least one open operational relationship — independent of
IMSS status entirely.** Workers hired on site bill from day one; employees registered and never
seen bill because the client used the system to manage them. An employee contributes at most one on
any day regardless of concurrent *registros patronales*, projects or relationships.

**6. Four anti-dispute safeguards, which are part of the decision rather than polish.** The
relationship closes on the operational *baja*, not the IMSS one, so forgotten records do not bill
forever. A monthly dormancy report surfaces employees with no *jornada* and no *baja*, with a bulk
close. Running billable headcount is visible daily so the invoice is never a surprise. The
duplicate queue prevents one person being billed twice.

**7. Plan capacity never blocks creating an employee**, online or offline; it is measured, billed as
overage and surfaced before invoicing. Seats are hard-enforced; employees are not. A supervisor
200km from signal cannot check a plan limit, and blocking a real worker's record over a billing cap
is a far worse failure than an overage conversation.

## Consequences

**Positive.** The system tells the truth about both realities at once, and the gap between them —
previously invisible — becomes the client's earliest warning and the product's strongest sales
argument. Metering is derivable from one timeline, reproducible for any past month, and auditable
against the client's own IMSS filings. Rotation and rehiring, which are constant in construction,
are ordinary rather than exceptional.

**Negative.** Two lifecycles are more to model, explain and keep consistent than one. An honest
record can evidence the client's own late filing (PRD §10.2); the response is alerting early, not
concealment, and NEO staff are deliberately blind to per-worker exposure. Field enrolment is a
duplicate generator, which is why the review queue is load-bearing rather than optional.

**Neutral.** Billing on operational rather than IMSS status means the numbers will not match a
client's IMSS filings exactly during exposure periods. That difference is the exposure, and showing
it is the point.

## Alternatives considered

**Single lifecycle driven by IMSS filings.** The legally tidy model, and it locks out every worker
during the gap. Rejected on the operational reality and on the product's posture.

**Single lifecycle driven by operational records only.** Simple, and it discards the compliance
alerting that is the largest source of value.

**Billing on IMSS-active employees.** Auditable and creates a direct incentive to delay filing.
Rejected.

**Billing on employees active at least one day in the month.** Yields invoices two to three times
what a rotation-heavy client expects. Peak concurrent matches the "up to N employees" language of
the plans and the number the client intuits.

## Revisit triggers

- Rotation so extreme that peak concurrent materially under-bills relative to system use, which
  would reopen day-prorated metering.
- Counsel guidance that changes what the exposure surface may show or retain.
