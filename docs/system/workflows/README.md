# Process and user workflows

*Living documents. Requirements live in [`../prd.md`](../prd.md) and decisions in
[`../adr/`](../adr/); these files design the **states, transitions, actors and failure paths** that
satisfy them, and never restate a requirement in their own words.*

PRD §5 contains seventeen user journeys written as prose happy paths. They establish *what*
happens. These documents establish what the states are, who moves an item between them, what
happens when nobody does, and what every one of those flows looks like with no connectivity.

**The organising principle:** the happy path is four screens and takes a paragraph. The exceptions
are the product. Every state machine here shows its failure states, because a diagram with only the
happy path is the diagram that hides the work.

---

## Reading order

1. **[`capture.md`](capture.md)** — the day at the *frente*. Start here: it is where the evidence is
   made and where most of the design pressure sits.
2. **[`employment.md`](employment.md)** — people, relationships, tiers, duplicates, and the first
   week of a deployment.
3. **[`imss.md`](imss.md)** — the affiliation lifecycle, IDSE ingestion, SIROC, and the *obra*'s two
   compliance windows.
4. **[`evidence.md`](evidence.md)** — the *lista de asistencia*, the signed paper cycle, the
   *periodo*, exports and the verification bundle.
5. **[`expediente.md`](expediente.md)** — documents, consent, ARCO, retention and erasure.
6. **[`alerting.md`](alerting.md)** — the alert and queue models, including the two the PRD did not
   cover.
7. **[`account-and-billing.md`](account-and-billing.md)** — onboarding, metering, delinquency, CFDI,
   referrals.
8. **[`support-and-access.md`](support-and-access.md)** — break-glass, the *contador externo*,
   post-revocation adjudication.

Then **[`../screens.md`](../screens.md)** for the screen inventory per persona and form factor.

---

## Where each object's lifecycle is designed

| Object | File | Terminal states |
|---|---|---|
| Capture session | [`capture.md`](capture.md) §2 | `CERRADA`, `BLOQUEADA` after handover |
| Daily list, per person | [`capture.md`](capture.md) §3 | `FUERA`, `ABIERTA_SIN_CIERRE` |
| `CHECADA` | [`capture.md`](capture.md) §4 | `ANCLADA`, `CORREGIDA` |
| `JORNADA` | [`capture.md`](capture.md) §5 | `CLASIFICADA`, `SIN_CIERRE` |
| Employee-day and its disposition | [`capture.md`](capture.md) §6 | `DISPUESTO`, `SIN_RESOLVER` |
| Expected/observed conflict | [`capture.md`](capture.md) §6, §7 | `DISPUESTO`, `SIN_RESOLVER` |
| Active-*incapacidad* sequence | [`capture.md`](capture.md) §7 | Both outcomes of `FR-1379`, plus the escalating failure |
| `DESVIACION` | [`capture.md`](capture.md) §10 | `DOCUMENTADA`, `CERRADA_CON_RAZON` |
| Correction request | [`capture.md`](capture.md) §11 | `APROBADA`, `RECHAZADA`, `RETIRADA`, `ESTANCADA` |
| `AUTORIZACION_HE` | [`capture.md`](capture.md) §12 | `AUTORIZADA`, `AUTORIZADA_RETROACTIVA`, `DENEGADA` |
| Sync | [`capture.md`](capture.md) §13 | `RECONCILIADO` |
| `DISPOSITIVO`, operationally | [`capture.md`](capture.md) §14 | `REVOCADO`, `PURGADO` |
| `RELACION_LABORAL` | [`employment.md`](employment.md) §2 | `CERRADA`, `FIN_DE_OBRA_ALCANZADO` |
| Documentation tier | [`employment.md`](employment.md) §3 | `COMPLETO`, and regression on expiry |
| Provisional employee | [`employment.md`](employment.md) §5 | `COMPLETADO`, `DUPLICADO_CONFIRMADO`, `ESTANCADO` |
| Duplicate candidate | [`employment.md`](employment.md) §6 | `FUSIONADO`, `DESCARTADO`, `SIN_TRABAJAR` |
| Bulk load | [`employment.md`](employment.md) §7 | `COMPLETO` |
| Cycle assignment | [`employment.md`](employment.md) §11 | `TERMINADA`, `SIN_ASIGNACION` |
| `CENTRO_TRABAJO` and both windows | [`imss.md`](imss.md) §1, §2 | `CERRADO`, `CASCADA_ABIERTA` |
| `ARCHIVO_IDSE` | [`imss.md`](imss.md) §3 | `COMPROMETIDO`, `RECHAZADO_AJENO`, `RETENIDO`, `INCOMPLETO` |
| `MOVIMIENTO` match | [`imss.md`](imss.md) §4 | `APLICADO`, `AJENO`, `SIN_EMPAREJAR` |
| `MOVIMIENTO_RECHAZADO` | [`imss.md`](imss.md) §5 | `SUBSANADO`, `CERRADO_CON_RAZON` |
| `REGISTRO_PATRONAL` registry row | [`imss.md`](imss.md) §6 | `TERMINADO`, `SIN_EVIDENCIA` |
| SIROC registration | [`imss.md`](imss.md) §7 | `CERRADA`, `SIN_CERRAR` |
| `ARCHIVO_ALTA_RP` | [`imss.md`](imss.md) §3, §6 | Same as `ARCHIVO_IDSE` |
| `LISTA_ASISTENCIA` and its reissue | [`evidence.md`](evidence.md) §2 | `ANCLADA`, `REEMITIDA`, `SIN_DIGITALIZAR` |
| Worker's written discrepancy | [`evidence.md`](evidence.md) §3 | Resolved as a correction, or escalating |
| *Periodo* close and deltas | [`evidence.md`](evidence.md) §4 | `ENTREGADO`, `DELTA_EMITIDO` |
| Verification bundle | [`evidence.md`](evidence.md) §6 | `LISTO`, `FALLIDO` |
| `DOCUMENTO` | [`expediente.md`](expediente.md) §1 | `SUPERSEDIDO`, `VENCIDO` |
| `CONSENTIMIENTO` | [`expediente.md`](expediente.md) §2 | `PLANTILLA_ELIMINADA`, `RECHAZADO` |
| ARCO request | [`expediente.md`](expediente.md) §3 | Four resolutions, `BORRADA`, `VENCIDA` |
| `ALERTA` | [`alerting.md`](alerting.md) §1 | Two resolutions, `INCUMPLIDA`, `NO_ENTREGABLE` |
| Queue item | [`alerting.md`](alerting.md) §4 | `DISPUESTO`, `ENVEJECIDO` |
| Company onboarding | [`account-and-billing.md`](account-and-billing.md) §1 | `FACTURABLE` |
| Delinquency | [`account-and-billing.md`](account-and-billing.md) §3 | `AL_CORRIENTE`, `DEGRADADO` |
| CFDI | [`account-and-billing.md`](account-and-billing.md) §4 | `VIGENTE`, `CANCELADO`, `SIN_TIMBRAR` |
| Referral | [`account-and-billing.md`](account-and-billing.md) §5 | `REWARD_EXPIRED`, `REJECTED`, `EXPIRED_UNCONVERTED` |
| Break-glass session | [`support-and-access.md`](support-and-access.md) §1 | `EXPIRADA`, `REVOCADA`, `DENEGADA`, `CADUCADA` |
| Delegated cross-tenant grant | [`support-and-access.md`](support-and-access.md) §3 | `REVOCADO`, `EXPIRADO` |
| Post-revocation adjudication | [`support-and-access.md`](support-and-access.md) §5 | The three outcomes of `FR-1437` |

---

## Cross-cutting flows

| Flow | Designed in |
|---|---|
| Onboarding a construction client, end to end | [`employment.md`](employment.md) §9 |
| A crew hired at identity-only tier on the day an *obra* starts | [`employment.md`](employment.md) §10 |
| The *registro patronal* arriving after a fortnight of work | [`imss.md`](imss.md) §9 |
| A worker revoking biometric consent | [`expediente.md`](expediente.md) §2 |
| An STPS inspection arriving on site | [`evidence.md`](evidence.md) §7 |
| A labour dispute, claim to verification bundle | [`evidence.md`](evidence.md) §8 |
| A device lost on site with unsynced records | [`capture.md`](capture.md) §14 |
| A client falling delinquent | [`account-and-billing.md`](account-and-billing.md) §3 |

---

## By persona

| Persona | Form factor | Primary files |
|---|---|---|
| Supervisor | Mobile, offline | [`capture.md`](capture.md); [`employment.md`](employment.md) §4 |
| *Recursos Humanos* | Desktop | [`employment.md`](employment.md), [`imss.md`](imss.md), [`expediente.md`](expediente.md) |
| Admin | Desktop | [`imss.md`](imss.md) §1–§2, [`evidence.md`](evidence.md), [`account-and-billing.md`](account-and-billing.md) |
| *Contador interno* | Desktop | [`evidence.md`](evidence.md) §4, [`support-and-access.md`](support-and-access.md) §4 |
| *Contador externo* | Desktop, cross-tenant | [`support-and-access.md`](support-and-access.md) §3 |
| Staff NEO | Desktop, control plane | [`support-and-access.md`](support-and-access.md) §1–§2 |
| The worker | Subject, not a user | [`capture.md`](capture.md) §15, [`evidence.md`](evidence.md) §3 |

---

## Conventions

- **Mermaid only.** `stateDiagram-v2` for lifecycles, `sequenceDiagram` for multi-actor flows,
  `flowchart` for decision trees. State identifiers are ASCII and unaccented; prose keeps the
  accents.
- **Requirements are referenced, never restated** (`docs/README.md` rule 1). Where a document
  appears to state a rule, it is describing how the flow satisfies a cited requirement.
- **English document, Spanish domain nouns**, and every string a user reads is es-MX (`FR-013`).
- **Screen inventories only.** No mockups, no wireframes, no visual design (PRD §14.3).

---

## What these documents assume, and what is still open

Design proceeds against ADR-0010 to ADR-0013 as the working assumption; all four are `Proposed`.

Open questions raised by this work and recorded in PRD §13: `OQ-070` (*jornada máxima*, elapsed or
worked), `OQ-071` (the split threshold default), `OQ-072` (daily list retention), `OQ-073` (evidence
for remote witnessing), `OQ-074` (the duplicate-*checada* window), `OQ-075` (how long an issued
*lista* may go undigitised), `OQ-076` (whether a device may hold more than one *obra*), `OQ-077` and
`OQ-078` (billing a presence record), `OQ-079` (site access control over subcontracted crews).

`OQ-039` — how a work pattern is authored for rotating and *12x12* crews — was **resolved during
this session**: the pattern is a first-class *ciclo de turno* modelled independently of whoever works
it, bound by an assignment carrying its own anchor, resolved most specific first
([`employment.md`](employment.md) §11, `FR-2500`–`FR-2513`).
