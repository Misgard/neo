# ADR-0014 — Payments and fiscal invoicing

- **Status:** Accepted
- **Date:** 2026-08-20
- **Source:** PRD §6.9.3, §11.9; `OQ-016`
- **Satisfies:** `FR-940`–`FR-946`, `FR-960`–`FR-968`, `INV-040`
- **Related:** ADR-0008 (the metering unit), ADR-0002 (replaceable trust integrations)

## Context

NEO bills its own clients for subscription revenue: tiered plans with included employee capacity,
graduated per-employee bands above it, separate admin/supervisor seat entitlements, and referral
discounts applied against invoices.

Two separate obligations sit behind that sentence and are easy to conflate. **Collecting money** is
a payments problem. **Issuing a fiscal invoice** is a Mexican tax problem: a CFDI 4.0 stamped by an
authorised *PAC*. A processor's invoice PDF is not a CFDI and does not discharge the obligation.

The metered figure is unusual. `FR-930` defines the billable unit as the peak, across the calendar
month, of distinct employees with an open operational employment relationship — not a sum of usage
events, and not a headcount at a moment.

## Decision

**1. Stripe for payment processing.** Charges, subscription state, payment methods and dunning for
NEO's subscription revenue.

**2. SW sapien as the CFDI *PAC*, for the whole lifecycle.** Not stamping alone: issuance,
cancellation with its *motivo* and the receiver-acceptance flow the post-2022 rules require, status
queries against a CFDI's *vigente* or cancelled state, *notas de crédito* as CFDI de egreso related
to the document they correct, *complementos de pago* where a client is billed on terms, and XML
retrieval. It also covers the receiving side, because NEO is issued CFDIs by its partners and must
answer cancellation requests against them (`FR-969`, `FR-970`).

The XML is the fiscal document and the PDF is a representation of it. NEO retains the XML, the
*acuses* and the status responses; a retained PDF is not a retained invoice (`FR-967`).

**3. NEO computes the billable figure; the processor only charges it.** The employee-month is
derived from NEO's own employment timeline and is reproducible for any past month (`FR-937`,
`INV-040`). It is submitted as a computed amount and never delegated to the processor's usage
aggregation.

This is the same boundary the rest of the product already draws — NEO computes and the client
files with the IMSS; NEO classifies time and payroll prices it; here NEO computes the charge and
Stripe collects it. The reason is the same each time: a number NEO cannot re-derive from its own
records is a number it cannot defend when challenged, and a peak-concurrent metric expressed
through a third party's aggregation semantics is exactly that.

**4. A charge and a CFDI are two artifacts that reconcile one-to-one.** Every settled charge
produces exactly one CFDI; every refund its *nota de crédito*. Either without the other is a
reconciliation exception raised to staff, not a variance tolerated in a report.

**5. Fiscal identity is collected and validated at onboarding.** *RFC*, *razón social*, *régimen
fiscal*, *domicilio fiscal* postal code and *uso de CFDI*. CFDI 4.0 validates these against SAT
records, so a wrong value yields no invoice rather than a wrong one. An account failing validation
is flagged before the billing run and never suspended for it.

**6. Card data never reaches NEO.** Hosted elements only, keeping NEO out of the handling scope
that would otherwise apply.

**7. The *PAC* is replaceable.** Every operation in decision 2 is a standardised SAT process, so
the interface is shaped by what the SAT requires rather than by one provider's API. No requirement
may depend on a single *PAC* remaining available — the same rule ADR-0002 applies to the
timestamping authority, for the same reason.

**8. Delinquency never suppresses capture.** Stripe's dunning drives the delinquency states in
`FR-944`; administrative surfaces degrade and the *jornada* keeps being captured and sealed.
Suppressing a statutory record over a payment dispute would create a violation NEO caused.

## Consequences

**Positive.** Subscription mechanics, payment methods and dunning are bought rather than built,
which at this team size is most of the billing work. Fiscal compliance is bought too, from a
provider whose only job it is. The authoritative number stays in NEO, so a client dispute is
answered from the employment timeline that produced it.

**Negative.** Two systems must be kept in agreement, and the reconciliation exception path is real
work that is easy to defer and expensive to add later. Fiscal identity becomes an onboarding
blocker with a validation that fails outside NEO's control — a client with a stale *régimen fiscal*
at the SAT cannot be invoiced until they fix it, and NEO can only report why. CFDI cancellation
after 2022 requires the receiver's acceptance in defined cases, which makes correcting a mistaken
invoice a negotiation rather than an action.

**Neutral.** Partner fee payouts run the other way — the partner issues a CFDI to NEO (`FR-968`).
It shares none of this flow's mechanics and is governed by `OQ-022`.

## Alternatives considered

**A processor that also stamps CFDIs.** Fewer integrations, and it couples fiscal compliance to the
payments vendor. Given decision 7, that is the coupling most worth avoiding.

**Delegating the metered figure to the processor's usage aggregation.** Less code. Rejected under
decision 3: it puts the number NEO must defend inside a system NEO cannot re-derive it from.

**Manual invoicing and SPEI reconciliation.** Viable for the first handful of clients and does not
survive the stage 2 envelope, and `FR-944`'s delinquency states are not automatable without a
processor.

**Building the CFDI lifecycle directly against the SAT.** Requires becoming or contracting the
certification role NEO has no reason to hold — and the cost would land in the cancellation and
acceptance flows, not in stamping, which is the part that looks hardest and is not.

## Revisit triggers

- Stripe's Mexican coverage or pricing changing materially against the cost target in `NFR-901`.
- A *PAC* failure or an obligation the interface in decision 7 cannot absorb.
- Clients requiring payment rails Stripe does not serve, which would make the processor a
  constraint on who can buy.
