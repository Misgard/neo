# Employment — people, relationships and the first week

*Living document. Requirements live in [`../prd.md`](../prd.md).*

**Form factors:** field enrolment and the daily roster are **mobile and offline** (ADR-0006);
completion, bulk load, duplicate resolution and *bajas* are **desktop console**.

Two lifecycles run per person and neither gates the other (ADR-0008): the operational
`RELACION_LABORAL` here, and `AFILIACION_IMSS` in [`imss.md`](imss.md). The gap between them is the
compliance exposure and is the most valuable thing the system computes.

---

## 1. Identity: what makes two records one person

| Key | Strength | Why |
|---|---|---|
| ***CURP*** | **Conclusive** | The universal person identifier, check-digit validated |
| ***NSS*** | **Conclusive** | Within a tenant an *NSS* resolves to at most one person (`INV-101`) |
| Name plus date of birth | **Proposes only** | Resolved by a human comparing the two enrolment photographs |
| A *differing NSS* | **Proves nothing** | One person may legitimately hold two or three (`FR-2300`) |

That last row is the one that surprises people. A worker can hold several *NSS* — less common than
it was, and still present in the workforce — so a mismatch is not evidence of two people. The
asymmetry runs one way: **a match proves identity, a mismatch proves nothing.**

Two consequences worth stating plainly. Affiliation, exposure and the *altas* export are answered
over the **union** of a person's *NSS* (`FR-2301`); a history assembled under one number while the
*alta* was filed under another produces a false *working without an alta* alert, and false alarms
teach people to ignore the alerting subsystem. And the IDSE artifact carries **no *CURP*** — only
the *NSS* — so the *movimiento* match has no second key to corroborate against
([`imss.md`](imss.md) §3).

---

## 2. `RELACION_LABORAL`

```mermaid
stateDiagram-v2
    [*] --> ABIERTA: hire recorded by RH, or field enrolment by a supervisor — FR-330
    ABIERTA --> ABIERTA: assignments, wage records, contract renewals append
    ABIERTA --> BAJA_PROPUESTA: supervisor proposes — FR-2008
    BAJA_PROPUESTA --> ABIERTA: RH declines the proposal
    BAJA_PROPUESTA --> CERRADA: RH disposes. Operational baja recorded — FR-338
    ABIERTA --> CERRADA: RH closes directly
    ABIERTA --> FIN_DE_OBRA_ALCANZADO: the proyecto it is bound to is completed — FR-312
    FIN_DE_OBRA_ALCANZADO --> CERRADA: baja recorded
    FIN_DE_OBRA_ALCANZADO --> FIN_DE_OBRA_ALCANZADO: escalates and breaches — FR-829, INV-027
    CERRADA --> [*]
    note right of FIN_DE_OBRA_ALCANZADO
        Failure state. The end condition has
        occurred and the relationship is still
        open. Never closed automatically —
        the legal consequence is too large
        to trigger by assumption.
    end note
```

Opening one requires a *centro de trabajo* and **never** a *registro patronal* (`FR-339`,
`INV-054`), because the IMSS mints the *registro patronal* when the *obra* is registered and people
are lawfully on site before that happens. Nothing about IMSS state opens, closes or gates it
(`INV-020`).

**A rehire is a new `RELACION_LABORAL` against the same `EMPLEADO`** (`FR-313`), never a reopening.
That is what keeps one person's history on one identity across the rotation that defines
construction, and what makes the duplicate queue load-bearing rather than optional.

---

## 3. Documentation tiers

Four tiers, and *jornada* capture works identically at every one of them (`FR-341`).

```mermaid
stateDiagram-v2
    [*] --> IDENTIDAD_DECLARADA: field enrolment, no document — FR-331
    [*] --> IDENTIDAD: an official ID
    [*] --> IDENTIDAD_Y_FISCAL: ID plus RFC and NSS
    [*] --> COMPLETO: full expediente
    IDENTIDAD_DECLARADA --> IDENTIDAD: a document is produced
    IDENTIDAD --> IDENTIDAD_Y_FISCAL: RFC and NSS captured
    IDENTIDAD_Y_FISCAL --> COMPLETO: expediente completed by RH
    IDENTIDAD_DECLARADA --> IDENTIDAD_DECLARADA: escalates on the document ladder — FR-807
    IDENTIDAD --> IDENTIDAD: same
    IDENTIDAD_Y_FISCAL --> IDENTIDAD_Y_FISCAL: same
    COMPLETO --> IDENTIDAD_Y_FISCAL: a document expires — FR-807
```

The fourth tier — **declared identity**, a name and a photograph with nothing else — is what
`FR-331` permits at the gate when a worker did not bring papers, and the PRD's ladder previously had
no room for it (`FR-2302`). It is the tier that makes duplicate detection matter, because it is the
only one where neither conclusive key exists.

**Each tier reports the consequence, not the missing field** (`FR-342`). No *NSS* means no
*movimiento* can be filed, so the five-*día hábil* clock cannot be stopped. No *RFC* means the
fiscal relationship cannot be formalised. And the gaps are reported **per *centro de trabajo***
(`FR-841`), because a crew hired on identity alone is a concentration of exposure rather than a set
of unrelated omissions.

---

## 4. Field hiring, mid-shift

Trigger: a worker starts today and is not in the system. Offline, with a queue behind him.

```mermaid
sequenceDiagram
    participant S as Supervisor
    participant A as Capture application
    participant W as Worker
    participant RH as Recursos Humanos
    S->>A: add to today's list — FR-2006
    A->>A: not found in the obra's cached roster
    A->>S: continue into field enrolment
    S->>W: name, photograph
    A->>W: aviso de privacidad and consent text, in Spanish, on screen
    W->>A: consents to biometrics, or declines and sets a secret — FR-431
    A->>A: face enrolment on device, no server round trip — FR-334
    S->>A: CURP or NSS if he has the documents. Photograph of the ID either way — FR-2304
    A->>A: provisional EMPLEADO plus open RELACION_LABORAL — FR-333
    A->>W: capture the checada. He is now on the list
    Note over A,RH: at sync
    A->>RH: completion queue — FR-335
    A->>RH: duplicate review queue — FR-336
```

The whole ceremony has to fit inside a shift change, so it collects the minimum that makes a record
attributable and defers everything else. **The photograph of the identity document is asked for even
when no field can be filled from it** (`FR-2304`): it is what resolves this man's identity three
weeks later when a second enrolment appears at another *obra*.

### Failure paths

| Condition | What happens |
|---|---|
| Worker declines biometrics | Baseline path, secret set on the spot, consent refusal recorded (`FR-431`) |
| Worker has no documents at all | Declared-identity tier. Never a refusal (`FR-2302`) |
| Plan capacity exhausted | Enrolment succeeds, metered as overage, reported with the date (`FR-935`, `FR-936`) |
| Device storage near its envelope | Warned at 70% (`NFR-940`); enrolment still succeeds |
| Worker already exists at another *obra* | Recognised if the *obra* roster covers him (`FR-2004`); otherwise a duplicate the queue resolves |
| Consent text version on the device is stale | Consent binds to the version the device held, recorded as such; RH re-consents if the text changed materially |

---

## 5. Provisional employee completion

```mermaid
stateDiagram-v2
    [*] --> PROVISIONAL: created in the field — FR-333
    PROVISIONAL --> EN_COLA_RH: arrives at sync with the age of the provisional state visible — FR-335
    EN_COLA_RH --> COMPLETADO: RH completes the expediente
    EN_COLA_RH --> DUPLICADO_CONFIRMADO: the duplicate queue resolves it into an existing person
    EN_COLA_RH --> ESTANCADO: incomplete beyond the configured interval
    ESTANCADO --> COMPLETADO: worked later
    ESTANCADO --> ESTANCADO: escalates — FR-824
    COMPLETADO --> [*]
    DUPLICADO_CONFIRMADO --> [*]
    note right of ESTANCADO
        Failure state. The worker keeps
        accruing jornada throughout —
        FR-333. Nothing about this
        blocks capture.
    end note
```

A provisional employee accrues *jornada* without restriction throughout (`FR-333`). The escalation
is aimed at the *expediente*, never at the worker.

---

## 6. Duplicate candidate

```mermaid
stateDiagram-v2
    [*] --> DETECTADO: raised at sync — FR-336
    DETECTADO --> CONFIRMADO_POR_CLAVE: CURP or NSS matches. Conclusive — INV-101
    DETECTADO --> PROPUESTO: name and date of birth match. Proposes only
    PROPUESTO --> CONFIRMADO_POR_HUMANO: reviewer compares the two enrolment photographs
    PROPUESTO --> DESCARTADO: reviewer determines two different people
    CONFIRMADO_POR_CLAVE --> FUSIONADO: reviewed merge — FR-2305
    CONFIRMADO_POR_HUMANO --> FUSIONADO
    DETECTADO --> SIN_TRABAJAR: nobody acts beyond the configured interval
    SIN_TRABAJAR --> PROPUESTO: picked up later
    SIN_TRABAJAR --> SIN_TRABAJAR: escalates — FR-825
    FUSIONADO --> [*]
    DESCARTADO --> [*]
    note right of FUSIONADO
        Histories merge. Nothing is deleted.
        The superseded identity remains
        readable pointing at the survivor —
        FR-2305, INV-028.
    end note
```

**Duplicates are never merged automatically** (`FR-336`), and a merge deletes nothing: the surviving
`EMPLEADO` acquires the other's relationships, *checadas*, documents and *NSS* values, and the
superseded identity stays readable pointing at the survivor (`FR-2305`). Biometric similarity is
**not** used — it would require comparing templates outside the device holding them, and the
documented keys settle every case where a document exists. The undocumented case is settled by a
person looking at two photographs, which is cheaper and more defensible than a similarity score
nobody can explain to a *perito*.

---

## 7. Bulk employee load

Desktop, RH. Trigger: an existing workforce arriving as a file at onboarding.

```mermaid
stateDiagram-v2
    [*] --> CARGADO: file uploaded, columns mapped
    CARGADO --> VALIDADO: rows checked. CURP, RFC and NSS format and check digits — FR-302
    VALIDADO --> APLICADO_PARCIAL: valid rows create employees. Invalid rows go to the error queue
    APLICADO_PARCIAL --> EN_COLA_ERRORES: reviewer works the failures
    EN_COLA_ERRORES --> APLICADO_PARCIAL: corrected rows applied
    EN_COLA_ERRORES --> ACEPTADO_CON_AVISO: row accepted with a warning and flagged for correction — FR-302
    EN_COLA_ERRORES --> DESCARTADO: row is not a person we employ
    APLICADO_PARCIAL --> COMPLETO: error queue empty
    COMPLETO --> [*]
    note right of APLICADO_PARCIAL
        A load never aborts. Bad rows queue,
        good rows apply — UJ-02.
    end note
```

Every row that creates a person also enters the duplicate queue (`FR-336`), because a bulk load
against a workforce that has already been field-enrolled is a duplicate generator by construction.
A value failing its check digit is **accepted with a warning and flagged**, never rejected
(`FR-302`) — a worker on site with a mistyped document must not be blocked from working.

---

## 8. The operational *baja*

```mermaid
flowchart TD
    A["Trigger"] --> B{"Origin"}
    B -->|"supervisor: he left"| C["Proposed baja — FR-2008"]
    B -->|"RH: resignation, dismissal, end of contract"| D["Recorded directly — FR-338"]
    B -->|"proyecto completed"| E["End condition reached — FR-312"]
    B -->|"dormancy report"| F["Bulk close, reviewed — FR-934"]
    C --> G["RH disposes"]
    E --> G
    F --> G
    D --> H["RELACION_LABORAL closed"]
    G --> H
    H --> I["Billing stops on this date — FR-932"]
    H --> J["IMSS baja obligation opens — FR-805"]
    H --> K["Roster drops them from the effective date — FR-1353"]
    H --> L["Contract history retained in full — FR-309"]
```

The operational *baja* closes the relationship; **the IMSS *baja* does not, and this one files
nothing with the IMSS** (`FR-338`). They are separate acts on separate lifecycles, and the gap
between them is `FR-805`'s alert.

**A completed *proyecto* does not close anything by itself.** Every contract *por obra determinada*
bound to it reaches its end condition, and each relationship must be closed by an explicit act which
the system escalates until it happens (`FR-312`, `FR-829`). A completed *proyecto* with an open
relationship against it is a breach state, not a tolerable one (`INV-027`).

---

## 9. Cross-cutting: onboarding a construction client, end to end

The riskiest week of every deployment. Sequenced so that **the first check-in happens on day one**
and nothing downstream is a precondition of it (`FR-2440`).

```mermaid
flowchart TD
    D1["Day 1 — Admin, desktop"] --> A1["Company profile, fiscal identity for CFDI 4.0 — FR-962"]
    A1 --> A2["Registro patronal registry rows, evidenced or flagged unevidenced — FR-213"]
    A2 --> A3["Centro de trabajo structure. Type vocabulary and capabilities — FR-217"]
    A3 --> A4["Users and grants. Alert lead times default — UJ-01"]
    A4 --> A5["Aviso de privacidad and consent text published — FR-1107"]
    A5 --> A6["Devices enrolled online, at the office, before they leave — FR-1474"]
    A6 --> B1["Day 1 — first capture at the frente"]
    B1 --> C1["Week 1 — enrolment campaign — FR-2441"]
    C1 --> C2["Week 1 — bulk load of the existing workforce, error queue worked"]
    C2 --> C3["Week 1 — duplicate queue worked as the two populations meet"]
    C3 --> D2["Week 1 — IDSE artifacts uploaded, affiliation timeline populated"]
    D2 --> D3["Ongoing — exposure dashboard becomes meaningful"]
```

**Device enrolment must happen before the devices leave for site** (`FR-1474`, ADR-0012): it is an
online ceremony and a site with no signal cannot commission a replacement. This belongs in the
minimum device specification conversation during the sale, not in the deployment week.

**Enrolment at scale is a campaign, not a queue of individual actions** (`FR-2441`). Several hundred
faces at a site with no connectivity needs a target population, a progress figure, a list of who
remains, resumability across days and across devices, and full offline operation (`FR-334`). Treated
as *enrol each person as you meet them*, it stalls at about sixty and nobody can say who is missing.

**The two populations collide by design.** Field enrolment starts on day one and the bulk load
lands mid-week, so the same people arrive twice — once as declared identities from the gate and once
as complete records from the file. That is why §6 is load-bearing and why `FR-2304`'s ID photograph
is worth the four seconds it costs.

---

## 10. Cross-cutting: a crew hired at identity-only tier on the day an *obra* starts

Common when a client is rushing to start, and it must close over the following days without anybody
being turned away (`FR-341`, `FR-342`).

| Day | What happens | What is visible |
|---|---|---|
| 0 | Crew hired at the gate, declared identity or identity only. *Jornada* capture from the first minute | Tier concentration per *centro de trabajo* (`FR-841`) |
| 0–2 | RH chases documents. Each arrival advances a tier | Per-person tier and what it blocks (`FR-342`) |
| 2–3 | *NSS* captured, so a *movimiento* becomes fileable | The five-*día hábil* clock, per person (`FR-802`) |
| 5 | Deadline. Whoever still has no *NSS* cannot be filed | Breach, with its cause distinguished (`FR-802`) |

The alert **distinguishes its cause**, because the two have different owners: *alta* not yet filed
is RH's to act on today; **no *registro patronal* to file under** is nobody's until the IMSS issues
it, and it is routed to whoever is chasing that (`FR-834`, `FR-840`). Telling RH to file an *alta*
that cannot be filed is how a compliance product teaches people to ignore it.

---

## 11. The work pattern and its assignment

`OQ-039`, resolved. **The pattern is modelled independently of whoever works it**, then assigned —
which is what separates *what the rotation is* from *who is on it*.

| Object | What it holds | What it never holds |
|---|---|---|
| ***Ciclo de turno*** | The rotation: *n* days on, *m* off, or a fixed week, with each position's shift, *jornada* type and break windows (`FR-2500`–`FR-2502`) | Any reference to a person, a crew or a date |
| ***Asignación de ciclo*** | The binding: subject, effective dates, and the **anchor** that fixes day zero (`FR-2503`) | The rotation itself |
| Resolution | Most specific wins, and records **which level answered** (`FR-2504`) | Any inference where nothing is assigned (`FR-2511`) |

A note on naming: *patrón* already means the employer everywhere in this product, so a work pattern
is a ***ciclo*** and never a *patrón*. The PRD's original `PATRON_EXPECTATIVA` read as *employer
expectation* and is renamed for that reason.

```mermaid
stateDiagram-v2
    [*] --> VIGENTE: cycle assigned to a subject, with effective dates and an anchor
    VIGENTE --> VIGENTE: the same cycle assigned to another subject, with its own anchor
    VIGENTE --> SUSTITUIDA: a more specific assignment overrides it for some people — FR-2504
    SUSTITUIDA --> VIGENTE: the more specific one end-dates
    VIGENTE --> TERMINADA: end-dated. Worker moves crews, or the crew's rotation changes
    TERMINADA --> [*]
    VIGENTE --> SIN_ASIGNACION: no assignment at any level for this subject
    SIN_ASIGNACION --> VIGENTE: one is made
    note right of SIN_ASIGNACION
        Legitimate, not an error. Observed time
        is reported with expected unstated and
        NO falta is inferred — FR-2511.
    end note
    note right of TERMINADA
        Never edited. What was expected on a
        past date stays what was expected —
        FR-2506, FR-2509.
    end note
```

### Resolving *expected today*

```mermaid
flowchart TD
    A["Who is expected at this obra today?"] --> B{"Employee assignment in force?"}
    B -->|yes| U["Use it. Level recorded as EMPLEADO"]
    B -->|no| C{"Organisational node — cuadrilla or frente?"}
    C -->|yes| V["Use it. Level recorded as NODO"]
    C -->|no| D{"Centro de trabajo?"}
    D -->|yes| W["Use it. Level recorded as CENTRO"]
    D -->|no| E{"Company default?"}
    E -->|yes| X["Use it"]
    E -->|no| F["No expected state. Report observed only — FR-2511"]
    U --> G["Apply any exception registered against the date — FR-1361"]
    V --> G
    W --> G
    X --> G
```

Resolution happens **per *centro de trabajo*** (`FR-2505`), which is what stops a worker assigned to
two sites concurrently (`FR-206`) from appearing on both rosters and being counted absent at each.

### Failure paths

| Condition | What happens |
|---|---|
| No assignment at any level | No expected state. **No *falta* is inferred** — a configuration gap must not manufacture an absence (`FR-2511`) |
| Worker moves crews mid-cycle | Old assignment end-dates, new one begins under the **receiving crew's anchor**. Two facts, not one edited row (`FR-2507`) |
| Crew's rotation changes | New cycle version and new assignment. Days already classified stay classified under what was in force (`FR-2509`, `FR-072`) |
| Cycle assigned but rule set not | `FR-2512` forbids it — a *12x12* cycle with the statutory default rule set would classify every shift as four hours of overtime |
| Working day falls on a *día de descanso obligatorio* | **Not a conflict.** Time to be classified correctly (`FR-2510`, `FR-1366`) |
| Device dark past any calendar horizon | Resolves locally from the cycle and its anchor. A cycle is a rule, not a calendar (`FR-2508`, `NFR-1111`) |

That last row is the strongest practical argument for expressing rotations as cycles: an enumerated
calendar has an end, and the sites that go dark longest are the ones running *12x12*.

---

## 12. Related

- [`capture.md`](capture.md) — the roster, the gate, and what happens to a worker who is not on it
- [`expediente.md`](expediente.md) — documents, expiry, consent and ARCO
- [`imss.md`](imss.md) — the affiliation lifecycle and the *obra*'s compliance windows
- [`account-and-billing.md`](account-and-billing.md) — metering, which follows this lifecycle exactly
