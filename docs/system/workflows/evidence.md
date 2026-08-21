# Evidence — the *lista*, the *periodo*, and proving it to a third party

*Living document. Requirements live in [`../prd.md`](../prd.md).*

**Form factor:** desktop console. The one field-side act is the supervisor collecting autographs on
paper, which needs no device at all.

This is where the product is delivered. Everything in [`capture.md`](capture.md) exists so that the
artifacts here survive a *peritaje*: **an independent expert, given only what NEO exports and a
published procedure, must be able to verify NEO's claims without NEO's cooperation** (§2.2).

---

## 1. Two signatures, and why both

The PRD holds both models and they are **cumulative rather than alternatives** (`OQ-026`, resolved):

| | What it is | What it carries |
|---|---|---|
| **Electronic** | The authenticated check-in *is* the worker's signature (`FR-522`) | The evidentiary weight. Attributable through the factor, the device key and the recorded consent |
| **Autograph** | Each worker signs their own row on the printed *lista* (`FR-523`, `FR-524`) | What an inspector expects to be shown, the worker's acceptance of the period, and remote auditability |

The consequence that matters operationally: **a worker declining to autograph is benign**
(`FR-2196`). The refusal is written on the document as a fact, the electronic record stands
untouched and fully attributable, and nothing escalates. What escalates is the digitised document
never arriving (`FR-2199`) — because without the paper there is nothing to show.

---

## 2. `LISTA_ASISTENCIA`

```mermaid
stateDiagram-v2
    [*] --> COMPUESTA: periodo closes. Derived from the records held — FR-520
    COMPUESTA --> PROVISIONAL: a device in scope still holds unsynced records — FR-2191
    PROVISIONAL --> COMPUESTA: that device syncs
    COMPUESTA --> EMITIDA: issued for signature, document hash fixed
    EMITIDA --> IMPRESA: printed carrying its hash and verification reference — FR-2192
    IMPRESA --> AUTOGRAFIADA: each worker signs their own row — FR-2193
    AUTOGRAFIADA --> DIGITALIZADA: scanned or photographed to PDF and uploaded
    DIGITALIZADA --> SELLADA: hashed, bound to this version, entered in the chain — FR-2195
    SELLADA --> ANCLADA: included in the next external anchor — FR-525
    EMITIDA --> SIN_DIGITALIZAR: configured interval passes with no scan
    IMPRESA --> SIN_DIGITALIZAR: same
    AUTOGRAFIADA --> SIN_DIGITALIZAR: same
    SIN_DIGITALIZAR --> DIGITALIZADA: it arrives late
    SIN_DIGITALIZAR --> SIN_DIGITALIZAR: escalates and breaches — FR-2199, FR-814
    ANCLADA --> REEMITIDA: a correction lands after sealing — FR-526
    REEMITIDA --> COMPUESTA: a new version, referencing its predecessor
    ANCLADA --> [*]
    note right of PROVISIONAL
        Says so on its face. Sealing a
        document missing records it should
        attest to is worse than issuing it
        late — INV-014.
    end note
    note right of SIN_DIGITALIZAR
        The failure state of the cycle, and
        the only one that escalates.
    end note
```

**A *lista* is never regenerated in place** (`FR-526`). A correction approved after sealing issues a
**new version** referencing the prior one, and both remain retrievable and exportable. Each version
records the rule set version and the software version that produced it (`FR-527`).

### What the printed document carries

Per worker per day: the recorded times, the *jornada* they compose, the record class, every
integrity flag, the *desviaciones* attached, the *incidencias*, and the device-claimed time beside
its anchored interval where the record was captured offline (`FR-452`, `FR-521`). Plus the document
hash and verification reference, printed on the page (`FR-2192`).

**And no monetary amount of any kind** (`FR-723`, `FR-2192`). What the worker accepts by signing is
the **attendance record their payment is computed from**, not an amount. NEO classifies time; the
client's accountant prices it, pays it and issues the CFDI (§1.3, §14.1).

### The rows that are not a signature

| Row state | How it appears |
|---|---|
| Signed | The autograph |
| **Declined** | Stated as a fact, with the worker's reason where given. Nothing escalates (`FR-2196`) |
| **Absent from the signing session** | Stated with its reason. Never signed by anyone else (`FR-2197`) |
| **Left the company mid-*periodo*** | Same |
| **Disputed** | The worker's written discrepancy, countersigned by both — see §3 |

A row is never left blank. A blank is indistinguishable from an omission, and the whole point of the
document is that it accounts for everybody.

---

## 3. The worker's written discrepancy

The most important thing on the paper, and the PRD had no object for it.

```mermaid
sequenceDiagram
    participant W as Worker
    participant S as Supervisor
    participant RH as Recursos Humanos
    participant P as Platform
    W->>S: disagrees with a row on the printed lista
    S->>S: writes the discrepancy on the document
    W->>S: both sign it
    S->>P: uploads the digitised document
    P->>P: transcribed, bound to the rows it disputes — FR-2194
    P->>RH: routed as a correction request — FR-502
    RH->>P: approves. A new checada references the original — FR-505
    P->>P: lista reissued — FR-526. Incidencias delta — FR-727
```

It is retained with the scanned page it came from (`FR-2194`), so the worker's own handwriting
survives alongside the transcription. This is the worker's voice in the record, and it is the thing
a *tribunal laboral* looks for first: a *lista* where somebody objected and the objection was
handled reads very differently from one where every row is clean.

Where a discrepancy is raised and **never resolved**, it stays open and escalating on the correction
ladder (`FR-2160`). It is never closed by the *periodo* moving on.

---

## 4. *Periodo* close and the payroll hand-off

```mermaid
stateDiagram-v2
    [*] --> ABIERTO
    ABIERTO --> CERRADO: periodo closed — FR-727
    CERRADO --> ENTREGADO: incidencias report delivered on schedule — FR-728
    ENTREGADO --> DELTA_EMITIDO: a correction affecting the period is approved
    DELTA_EMITIDO --> DELTA_EMITIDO: further corrections, further deltas
    DELTA_EMITIDO --> [*]
    ENTREGADO --> [*]
    note right of ENTREGADO
        Does not wait for the digitised
        lista — FR-2198. Payroll runs on
        its own rhythm.
    end note
```

**The hand-off does not wait for the paper** (`FR-2198`). Collecting fifty autographs and scanning
them takes days; payroll runs weekly in construction. The signed *lista* is evidence, not a gate,
and whatever the signing turns up arrives as a delta (`FR-727`).

Delivery is scheduled and pushed without anyone requesting it (`FR-728`), and it states its
**coverage window and version** so a later correction produces a delta rather than a silently
different file under the same name (`FR-729`).

**Delivery is a notification with a link, never the file itself.** No worker personal data leaves
NEO through email or a messaging channel; the recipient follows the link into the console where the
report, the *desviación* and the underlying records are all reachable from the surface they are
already on. That also keeps paid messaging inside `NFR-903`.

### What the report must not do

An employee-day where expected and observed disagree is reported **as the conflict it is**, with
both statements visible, never flattened into whichever one the report happens to favour
(`FR-1368`). The accountant is about to pay those days; resolving it inside the report would hide
the one thing they need to see.

---

## 5. The integrity chain, operationally

```mermaid
flowchart LR
    C["Checadas, listas, desviaciones, autorizaciones,<br/>IDSE artifacts, grants, device events, audit entries"] --> TC["Per-tenant append-only chain — FR-512"]
    TC --> R["Daily chain root — FR-513"]
    R --> M["Platform-wide Merkle tree, one period, all tenants — FR-514"]
    M --> T["External RFC 3161 timestamp, optionally a NOM-151 constancia — FR-516"]
    T --> B["Verification bundle — FR-530"]
    TC -.->|"scheduled incremental verification"| V["Against signed checkpoints — NFR-602, NFR-609"]
    V -.->|"break"| K["FR-518, FR-821. Critical, permanent, never silently repaired"]
```

**The chain is a structure of its own and the rows reference it** (`FR-2410`, `INV-108`). The
consequence: a row removed directly in the database leaves a sealed hash pointing at nothing, and
verification detects it. Had the chain been columns on the row, the same removal would be silent.
That is what `NFR-1108` tests, beside `NFR-943`'s mutation case.

Verification is **incremental against signed checkpoints** (`NFR-609`), because a full end-to-end
run is proportional to accumulated history and would get slower every day for the life of the
system. A full re-verification from origin runs on a slow schedule and **on demand before a
verification bundle is produced for a dispute** — which is exactly when the cost is worth paying.

---

## 6. The verification bundle

```mermaid
stateDiagram-v2
    [*] --> SOLICITADO: scope and date range chosen. The request is itself audited — FR-534
    SOLICITADO --> VERIFICANDO: full chain re-verification over the range — NFR-609
    VERIFICANDO --> FALLIDO: a break is found
    FALLIDO --> [*]: FR-821 raised. The bundle is not issued over a broken segment
    VERIFICANDO --> GENERANDO: asynchronous, streamed, observable progress — NFR-505
    GENERANDO --> LISTO: bundle assembled
    LISTO --> [*]
    note right of LISTO
        Records and corrections, the listas
        covering them, the chain segment,
        Merkle inclusion paths, timestamp
        tokens, attestation results, device
        public keys, and the published
        procedure — FR-530, FR-531, FR-1487.
    end note
```

Three properties are non-negotiable and each is a design constraint rather than a feature: the
procedure is executable **by hand**, without NEO's utility (`FR-532`); verification must work
**after NEO has ceased to operate**, so no step may depend on an API NEO controls (`FR-533`); and a
bundle over an **archived** period is producible from the archive alone (`NFR-1109`, `FR-2415`).

Where a period has been erased under ARCO (`FR-2412`), the bundle still verifies. What it shows is
the **shape** of the record — that a row existed, when, on what device, in what class, in what chain
position — and not its subject. That is the honest outcome and it should be stated in the procedure
rather than discovered by a *perito*.

---

## 7. Cross-cutting: an STPS inspection arrives on site

Unannounced, at the gate, asking a supervisor for records.

```mermaid
sequenceDiagram
    participant I as Inspector
    participant S as Supervisor
    participant A as Admin or RH
    participant P as Platform
    I->>S: asks for the jornada records for this obra
    S->>S: has the paper listas for closed periodos on site
    S->>A: notifies. Everything else comes from the console — decided, never from the device
    A->>P: STPS export for the named scope and range — FR-710
    P->>A: machine-readable plus a human-readable document — FR-710, FR-712
    A->>I: hands over, with corrections, classes, flags and anchored intervals intact — FR-704
    opt inspector challenges the record
        A->>P: verification bundle for the same scope — FR-713
        P->>A: bundle plus the published procedure — FR-530, FR-531
    end
```

**The supervisor device never produces an inspector-facing artifact.** It holds one crew's partial
view, and an artifact assembled from a partial view is exactly what would be handed over under
pressure. Everything comes from the console, where the scope, the rule set version and the export
mapping version are recorded on the artifact and written to the audit log (`FR-701`).

What the supervisor does hold on site is the **printed, autographed *listas*** for closed *periodos*
— which is the artifact an inspector recognises, and the reason `FR-523` and `FR-524` default on for
construction.

---

## 8. Cross-cutting: a labour dispute

```mermaid
flowchart TD
    A["Claim arrives, or counsel requires records"] --> B["Legal hold placed on the worker's records — FR-1112"]
    B --> C["Hold suspends key destruction — FR-2414"]
    C --> D["STPS export plus per-worker constancia de jornada — FR-710, FR-714"]
    D --> E["Full chain re-verification over the range — NFR-609"]
    E --> F{"Chain intact?"}
    F -->|no| G["FR-821. The break is disclosed, never repaired, and the bundle says so"]
    F -->|yes| H["Verification bundle — FR-530"]
    H --> I["Handed to the tribunal or the perito with the published procedure — FR-531"]
    I --> J["Perito verifies without NEO's cooperation — FR-533"]
```

**Place the legal hold first.** It is the step most easily forgotten and the only one that is
irreversible if missed: a retention window lapsing mid-dispute would destroy the key to the very
records under examination (`FR-2414`).

What the bundle contains that a spreadsheet cannot: both the original and every correction with
their relationship explicit (`FR-505`); the record class of each event, so *the supervisor asserted
this* is visibly distinct from *the worker verified this* (`FR-521`); the anchored interval beside
the device-claimed time, so an offline gap is disclosed rather than hidden (`FR-452`); every
*desviación* explaining a departure from the ordinary process, which is **evidence in the client's
favour** and is never suppressed (`FR-1337`); and the *desviación* timelines from any *incapacidad*
sequence, which read as a *patrón* who identified a problem and acted (`FR-1377`).

---

## 9. The exports

| Export | For | Notes |
|---|---|---|
| STPS *jornada* export | An inspector or counsel | Versioned mapping held as configuration, so a prescribed format is a new mapping and not a release (`FR-712`) |
| *Constancia de jornada* | One worker, over a range | The closest thing to a worker self-service surface at v1 (`FR-714`, `OQ-014`) |
| *Incidencias* report | Payroll | Classified time only. Never money (`FR-723`) |
| *Altas ante el IMSS* | A supervisor proving their crew is insured | Exactly their `ORG_SUBTREE`, no wider (`FR-615`) |
| Verification bundle | A *perito* | §6 |
| Audit log | The company Admin only | (`FR-1106`) |

All of them: reproducible byte-for-byte for the same scope and versions (`FR-703`), carrying a
verification reference (`FR-702`), never omitting corrections, flags or classes (`FR-704`), in
Spanish with Mexican conventions (`FR-705`), and audited (`FR-701`). Generation is always an
asynchronous streamed job with observable progress, never a request-response (`NFR-505`).

---

## 10. Related

- [`capture.md`](capture.md) — where every record here comes from
- [`alerting.md`](alerting.md) — chain break, missing scan, unresolved discrepancy
- [`support-and-access.md`](support-and-access.md) — who may produce these, and what is logged
- [`../adr/0002-evidentiary-integrity-architecture.md`](../adr/0002-evidentiary-integrity-architecture.md)
