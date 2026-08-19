# Prompt — NEO PRD

## 0. Role and mission

You are acting as the **lead system architect** for a greenfield product. You have deep
experience in multi-tenant B2B SaaS, regulated data, GCP, and Mexican labor/social-security
compliance (LFT, IMSS, Infonavit, STPS, LFPDPPP).

Your only deliverable in this session is `docs/system/prd.md`. Do not write code, Terraform,
migrations, or schema DDL yet. The PRD is the artifact everything else will be derived from.

**Hard rule on uncertainty:** if a decision is required and the information is not in this
brief, do **not** invent it. Stop and ask. Every question must come with (a) at least two
concrete options, (b) the trade-off of each, and (c) your recommendation with reasoning.
Group your questions into *blocking* (cannot write the PRD without an answer) and
*non-blocking* (can be written as an open item). Ask blocking questions **before** writing.
Record non-blocking ones in a dedicated section of the PRD.

---

## 1. Product

**Name:** NEO — *nómina en obra*.
**Repo:** clean GitHub repo, Python `.gitignore`, nothing else yet.

**What it is:** a commercial SaaS digital time clock (*reloj checador digital*) sold to
Mexican companies, designed from day one as the compliance substrate for the recent LFT
reform.

**Regulatory anchor — the reason the product exists:**

> Art. 132, fr. XXXIV LFT — obligación central: registrar electrónicamente la jornada de
> cada persona trabajadora con horario de inicio y finalización, y proporcionarlo a la
> autoridad cuando lo requiera. Incluye la regla de **prueba plena** y la facultad de la
> STPS para emitir disposiciones generales.

Two consequences you must treat as first-class product requirements, not implementation
details:

1. **Prueba plena.** The jornada record is intended to carry full evidentiary weight in a
   labor dispute or STPS inspection. The PRD must state what makes a record trustworthy
   (tamper-evidence, trusted time source, chain of custody, non-repudiation, exportability
   in a form an inspector or a junta will accept) and what would destroy that trust.
2. **Reglamentación pendiente.** The STPS may issue disposiciones generales that change the
   required fields, retention, or export format. The design must isolate "what the law
   currently demands" from "how we capture and store it," so a future NOM/acuerdo is a
   configuration and export change, not a rewrite.

**First clients:** construction companies, about to sign. Their operating reality drives the
hardest constraints (see §4).

---

## 2. Personas and access model

Design a role model that covers these, including how roles are scoped (company-wide, by
registro patronal, by ubicación/proyecto, by org-chart subtree):

| Persona | Needs |
|---|---|
| **Admin (company)** | Configure the company profile; full access to contracted modules; manage users and roles. |
| **Recursos Humanos** | Upload and manage contracts; full employee expediente and history (previous contracts with that company, IMSS/Infonavit files, ID, visas, etc.). |
| **Supervisor** | Register attendance for the employees under their responsibility. **Nested hierarchy** — supervisors of supervisors. Must be able to download the *altas ante el IMSS* for workers assigned to a given área or proyecto, as proof the workers are legally hired and insured. |
| **Contador interno** | Consume attendance lists to compute payroll. |
| **Contador externo** | Not an employee of any client. Serves multiple companies. Needs a **distinct UI** to manage all their client companies, employees, and attendance lists. This is the one role that legitimately crosses tenant boundaries. |
| **Staff NEO (internal)** | Our own operations/support users, to monitor system health and assist clients. Define what they can and cannot see in client data, and how that access is logged. |

For each persona, the PRD must specify: what they can read, write, approve, export, and what
is logged. Treat "who may edit a jornada record after the fact, and under what audit trail"
as a named, explicit decision — it is the single biggest threat to *prueba plena*.

---

## 3. Functional scope

Cover at minimum:

1. **Registro de jornada** — check-in/check-out, breaks, corrections, approvals.
2. **Employee authentication at check-in** (see §4).
3. **Expediente del empleado** — contracts history, ID, profile data, passport, visa copies
   (for travel), IMSS registration documents, Infonavit documents, any other document
   relevant to the employment relationship. Photo of each employee for ID badge and profile.
   Documents and contracts carry expiry semantics: anything with an end date — visa,
   passport, ID, work permit, certification, and any contrato **por tiempo determinado** —
   must raise an alert before it lapses, on a lead time the company configures per document
   type. A determinado contract that reaches its término with no renewal and no baja is a
   live legal exposure, so these alerts escalate rather than appearing once and being
   dismissed. Specify who is notified, at what intervals, and what happens when nobody acts.
4. **Estructura organizacional** — each company defines its own ubicaciones de trabajo,
   proyectos, divisiones, departamentos, and organizational chart, as they please.
5. **Registros patronales** — a company can hold several. Construction requires a local
   registro patronal per obra.
6. **Movimientos ante el IMSS** — altas, bajas, modificaciones. Under IMSS law the patrón
   has **5 days** to register a change. The system must always be able to answer, for any
   employee at any point in time: are they currently hired, under which registro patronal,
   assigned to which workplace, from what date to what date (or open-ended).
7. **Historial salarial** — one employee, many wages, each with a start timestamp and an end
   timestamp (null/undefined while active).
8. **Exports and hand-offs** — the STPS-facing export of jornada records, the
   supervisor-facing *altas ante el IMSS* export, the signed *lista de asistencia*, and the
   *incidencias* report that feeds the client's payroll system.
9. **Alerting** — the duplicate-registration rule below, the document and contract expiry
    alerts in item 3, and whatever else the jornada and IMSS rules imply. Design this as one
    subsystem with configurable lead times, routing by role, and escalation — not as
    notifications scattered across modules.
10. **Dashboards y administración de la cuenta** — two distinct surfaces, not one shared
    screen with a permission flag:
    - *Company admin:* headcount and active users against what was contracted, usage broken
      down by registro patronal / proyecto / ubicación, subscription status and module
      entitlements, invoices and payment history, any referral discounts currently applied
      and when they expire, and adoption signals (which sites are checking in and which have
      gone silent).
    - *NEO staff:* the same picture across all tenants — accounts, seats in use, billing
      state, delinquency, consumption trends, referral attribution and fees owed, system
      health, and which clients look at risk. Anything this surface exposes about client data
      is governed by the internal-access rule in §2 and must be logged.

    Metering is the part that bites later: define the billable unit (active employee per
    month, check-ins registered, named seats, or something else) and confirm the jornada data
    model can produce that number cleanly under whichever tenancy model we pick. Also settle
    who is billed when an external accountant serves several companies — the accountant, each
    company, or a mix — and raise it as a question if the answer isn't obvious.
11. **Programa de referidos** — one referral graph, two different reward mechanics:
    - *Clients* — companies, and independent professionals who are clients in their own
      right — earn a **time-limited discount** for each referred client that buys an annual
      license.
    - *Contadores externos* earn a **fee** for each client they effectively referred.

    Both groups need a surface to manage their referidos: register or invite a prospect,
    follow its state (invited → registered → annual license paid → reward active → reward
    expired), and see what they have earned or saved to date. Rewards feed billing, so this
    is not a marketing bolt-on — model it alongside subscriptions, not beside them.

    Decisions to raise here: what "effectively referred" means and how long the attribution
    window stays open; what happens when two referrers claim the same prospect; whether a
    reward survives the referred client cancelling, downgrading, or falling delinquent;
    whether multiple discounts stack, cap, or extend in sequence; how accountant fees are
    actually paid out and what invoicing and withholding that triggers on our side in Mexico;
    and whether anyone outside these two groups is allowed to refer at all.

**Explicit modeling instruction (do not simplify away):** the *altas/bajas del IMSS* files
get their own table. **One file may contain many employees**, and **one employee may have
many movimientos**. An employee may legitimately be under two or more registros patronales
of the same company at the same time. When that happens, raise an alert for HR/Admin to
review whether it is a reporting-window overlap or a genuine duplicate registration.

**Payroll boundary — already decided, do not re-open.** NEO stops at *incidencias*. It does
not calculate payroll and does not timbrar CFDI de nómina. Most of our target clients already
run payroll software linked to their accounting system; NEO feeds it.

In scope:

- **Lista de asistencia.** The system produces the attendance list that the employees sign.
  It has to survive being challenged in a labor dispute or an STPS inspection, which means
  its content must be provably unaltered since signing, its existence at a given moment must
  be provable, and each signature must be attributable to the worker who made it. This is the
  operational core of *prueba plena* — treat it as a first-class deliverable, not a report.
  **How** those properties are achieved is yours to decide. Hashing the digitalized document
  and certifying the hash against a trusted timestamp is one route I have considered, not a
  requirement; if something else is stronger, cheaper, or simpler to operate, say so.
- **Reporte de incidencias.** The hand-off artifact to the client's payroll system:
  vacaciones, incapacidades (there are several distinct types — model the taxonomy, do not
  collapse it into one), horas extra, faltas, retardos, permisos, and anything else the
  jornada record implies.

Out of scope: payroll calculation, withholding, CFDI 4.0 timbrado, accounting postings.

Decisions you must raise on this (options plus recommendation, per §0):

- **How employees sign the lista** — manuscript signature captured on a device, the
  authenticated check-in event itself standing as the signature, e.firma/FIEL, or a
  print-and-scan hybrid for sites with no usable device.
- **How the lista's integrity and date are proven** — candidate mechanisms include a
  constancia de conservación issued by a PSC authorized under NOM-151-SCFI-2016, a generic
  RFC 3161 timestamping authority, an internal append-only hash chain anchored periodically
  to an external authority, or a combination. Propose others if they fit better. Include cost
  per document at our expected volume and what each actually buys us in front of a junta or
  an STPS inspector.
- **The shape of the incidencias hand-off** — file export, API, or per-vendor connectors —
  and which payroll systems the first clients are actually running.

---

## 4. Employee authentication at check-in

The law is currently silent on biometrics or any specific method. The design must therefore
be **method-agnostic and pluggable**, while shipping with a working default.

What the mechanism must guarantee: **that the employee genuinely showed up to work.**

Constraints from the construction sites:

- **Dedicated hardware is optional, never required.** On construction sites workers destroy
  or steal equipment, so the product has to work with no fixed device at all. But some clients
  do have the conditions for a physical terminal — offices, plants, controlled access points,
  indoor and outdoor — and they should be able to use one. Any supported terminal must talk to
  NEO directly over the network and push its records itself: no file exports, no middleware,
  no reconciliation work landing on the client. Treat a terminal as one interchangeable
  capture channel among several, not as a separate product.
- **Fingerprint is impractical** — most workers have scarred or injured hands.
- **Cards/tags are not acceptable** — trivially handed to someone else.
- **Face recognition can work**, but crews often work outdoors and lighting is unreliable (a
  lamp or flash may mitigate this).
- **Internet is intermittent or absent.** Some sites are far from any city with no
  connectivity unless Starlink is installed. Offline capture is mandatory, with later
  reconciliation.
- **Phones are low-end.** A verification code should work for most workers, but not all will
  have a phone with them.

**Working preference (challenge it if you disagree):** face recognition as the primary
factor, SMS/WhatsApp verification code as the second, and an optional password fallback for
workers without their phone.

The PRD must address, at minimum:
- **Liveness / anti-spoofing** — a photo of a photo, or a coworker holding up a phone, must
  not pass.
- **Buddy punching** and what corroborating signals (device identity, GPS/geofence, supervisor
  attestation) are recorded alongside.
- **Where the biometric template lives** — on-device vs server, template vs raw image, and
  whether raw face images are ever retained.
- **The refusal path.** Under LFPDPPP, biometric data is a *dato personal sensible* requiring
  express, informed, written consent. There must be a compliant, equally valid alternative
  for a worker who declines, and the PRD must say what it is.
- **Trusted time.** If the device is offline and its clock is wrong or deliberately changed,
  what protects the integrity of the timestamp?

---

## 5. Data, tenancy, and security

Security is a stated top priority; treat it as a design driver, not a checklist appendix.

- **Isolation by company is mandatory.** Each company's data is private. The only sanctioned
  cross-tenant view is the external accountant, scoped to companies that have granted them
  access.
- **Some clients will want their data in their own database.** The PRD must present the
  tenancy fork as an explicit decision with a recommendation: pooled multi-tenant with
  row-level isolation, schema-per-tenant, database-per-tenant, or a bring-your-own-database /
  single-tenant deployment tier — including what each costs us operationally (migrations,
  backups, incident response, per-tenant pricing floor).
- **Data protection:** aviso de privacidad, ARCO rights, consent capture and revocation,
  encryption at rest and in transit, key management, data residency, retention and deletion
  schedules. Note that jornada and employment records carry statutory retention obligations
  that may conflict with a deletion request — state how that conflict is resolved.
- **Auditability:** append-only audit log for anything touching a jornada record, an IMSS
  movimiento, or a wage record. Say who can read the audit log and whether it is exportable.

---

## 6. Technical constraints and preferences

- **Cloud:** GCP.
- **My usual stack:** Terraform, Kubernetes, ArgoCD, Docker, PostgreSQL, Alembic, Python.
- You are the architect: if Python is not the best fit for some component, **recommend
  something better and justify it**. Same for any other element of the stack. Treat my list
  as a strong prior, not a constraint.
- The PRD should include a *Technical constraints and assumptions* section, but **not** lock
  in the architecture. Concrete stack decisions go into ADRs under `docs/system/adr/`, one
  per decision, after the PRD is approved.

---

## 7. Explicitly out of scope for this document

- Implementation code, schema DDL, Terraform, CI/CD config.
- Final UI design. Describe screens and flows in prose; no mockups.
- Commercial price points and packaging tiers. Billing *mechanics* — metering, entitlements,
  invoicing, delinquency — are in scope per §3.10; what we charge is not.
- `[DECIDIR: anything else you want fenced off — e.g. control de acceso físico, comedor,
  EPP, capacitación DC-3, NOM-035]`

---

## 8. Deliverable specification

Write `docs/system/prd.md` with this structure:

1. Purpose and problem statement
2. Regulatory context and compliance obligations (with the *prueba plena* requirement made concrete)
3. Target market, buyer, and users
4. Personas and permission model
5. Core use cases / user journeys, per persona
6. Functional requirements, numbered `FR-###`, each testable
7. Data model requirements — entities, relationships, temporal semantics, and the invariants
   that must always hold (stated in prose; no DDL)
8. Attendance capture and authentication requirements
9. Non-functional requirements — security, tenancy and isolation, availability, RPO/RTO,
   offline behavior, scale envelope, observability, cost targets
10. Compliance and audit requirements (LFT, IMSS, Infonavit, STPS, LFPDPPP)
11. Integrations — IMSS IDSE, Infonavit, whatever external trust or certification service the
    chosen evidentiary approach requires, network-connected attendance terminals (indoor and
    outdoor), hand-off to the client's payroll/accounting system (export only — see the
    payroll boundary in §3), SSO, notifications
12. Assumptions
13. Open questions and decisions pending, each with options and my recommendation
14. Out of scope
15. Glossary of Mexican legal/domain terms (registro patronal, alta, baja, movimiento,
    jornada, expediente, etc.) — written so a non-Mexican engineer can work from it

**Conventions:** written in `[DECIDIR: English / Spanish / English prose with Spanish legal
terms preserved]`. Legal and domain terms stay in Spanish regardless. Requirements are
numbered and individually testable. Mermaid for any diagram. No filler; if a section has no
content yet, say so and move it to open questions.

**Definition of done:** every requirement is traceable to something in this brief or to an
answer I gave you; no requirement is invented; every gap appears in §13 rather than being
papered over.

---

## 9. Start here

Before writing anything, reply with:

1. Your understanding of the product in five sentences or fewer.
2. Your **blocking** questions, in priority order, each with ≥2 options and your
   recommendation.
3. Your **non-blocking** questions, listed only.
4. Anything in this brief you think is wrong, risky, or internally inconsistent.

Wait for my answers before drafting the PRD.