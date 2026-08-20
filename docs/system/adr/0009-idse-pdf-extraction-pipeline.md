# ADR-0009 — IDSE PDF extraction pipeline

- **Status:** Proposed
- **Date:** 2026-08-18
- **Source:** PRD §6.6, §6.6.1, §11.2; decision `B3`; `OQ-006`
- **Satisfies:** `FR-601`–`FR-615`, `FR-620`–`FR-629`, `INV-024`, `INV-025`
- **Related:** ADR-0008 (two lifecycles), ADR-0002 (custody and sealing)

## Context

The IDSE filing itself is outside NEO's boundary: whoever holds the client's IMSS portal access
files there and receives an artifact back. That artifact is a **PDF**, and the client uploads it.
NEO parses it, matches each *movimiento* to an employee, populates the affiliation timeline, and
keeps custody.

A *movimiento* is an assertion about a person's legal status that starts a five-day statutory clock
and appears in evidence. Getting one wrong is not a data-quality issue; it is a compliance alert
that fires against the wrong person, or fails to fire at all.

The initial suggestion was to use a model to extract the fields. The decisive observation is that
every key field carries a check digit: *NSS* (11 digits, Luhn), *CURP* (18 characters, published
check digit), *RFC* (12 or 13, check digit). The problem has a built-in correctness oracle, which
makes it a parsing problem rather than an inference problem.

A real sample document is not yet available. This ADR settles the pipeline; the sample settles the
templates, which are configuration.

## Decision

**1. The uploaded file is authoritative; parsed rows are a derived, re-derivable index.** The PDF
is stored intact, hashed, and sealed into the tenant integrity chain. A parser defect is a reparse,
never a data loss, and a challenged *movimiento* is answered with the original IMSS document rather
than our interpretation of it.

**2. Classify before parsing.** Confirm the document is an IMSS artifact and match it to a known
layout version by invariant header text and structural fingerprint. The layout version is recorded
on the file.

**3. Extract with a declarative template per layout version**, held as configuration, not code. A
new IMSS layout is a new template, on the same principle as the versioned STPS export mapping.

**3a. Templates address fields positionally, not by label proximity.** This is a correction forced
by the first real sample. The constancia's text layer emits every field label as one run and every
value as another, in a different order, so a label-then-next-token parser silently swaps *folio*
with *lote* and *RFC* with *registro patronal*. Separately, the movement table carries three
distinct columns all headed `Tipo` — movimiento, salario and trabajador — identifiable only by
ordinal position. A text-flow parser is not merely less robust here; it is wrong (`FR-630`,
`FR-631`).

**4. Validate every field structurally before accepting it.** *NSS*, *CURP* and *RFC* check digits;
date parseability and plausibility; movement type within the enumerated set; *SBC* numeric and
inside a sane band. A field that fails validation is never silently accepted — its row carries the
failure and goes to review.

**5. Cross-foot the parse against the document itself.** Where the artifact states a *movimiento*
count, a total, or a folio range, the parsed rows must reconcile to it. **A parse that does not
reconcile is rejected as incomplete, never accepted as partial.** This is the highest-value check in
the pipeline: it makes parse completeness verifiable rather than assumed, which is precisely the
question an expert would ask.

**6. Capture any *folio*, *cadena original*, *sello digital* or verification reference verbatim** as
independent corroboration of the artifact.

**7. Match deterministically: exact *NSS*, then exact *CURP*.** Unmatched rows fall to a
deterministic stage on normalised name plus date of birth, which *proposes* and never commits.
Anything unresolved by an exact key enters a human review queue, and the confirmation records the
actor and the method.

**8. Automated extraction is a bounded fallback, not the ordinary path.** It is permitted only where
the layout is unrecognised or the PDF carries no text layer. Whatever it proposes must pass the same
structural validation; a proposed value failing a check digit is discarded rather than offered as a
suggestion. It never commits a value or a match.

**9. Every field records its extraction provenance** — `template`, `template_low_confidence`, or
`automated_proposed_human_confirmed` — and provenance travels with the *movimiento* wherever it is
displayed or exported.

**10. Golden-file regression fixtures.** Every real sample becomes a fixture with its expected
parse, and template changes are gated on the whole set passing. This is what makes template
maintenance safe over years of IMSS layout drift.

## Consequences

**Positive.** The path that decides what a *movimiento* says is deterministic, explainable and
testable. Correctness is checkable per field by check digit and per document by cross-footing.
Layout drift is absorbed by configuration. If the sample confirms a text layer — which a
portal-generated PDF normally has — the automated fallback is not needed in v1 at all and the model
disappears from the critical path entirely.

**Negative.** Templates need authoring and maintaining per layout, and an unrecognised layout stops
the deterministic path and falls to review. A scanned or photographed document degrades to the
fallback with a human confirming every row. Cross-footing only works if the artifact states
something to foot against; if it does not, completeness is asserted rather than proven, and that
limitation must be stated rather than glossed.

**Neutral.** Python is a good fit for this work and is the reason the backend language choice in
ADR-0007 is comfortable rather than merely acceptable.

## Alternatives considered

**A model as the primary extractor.** Fast to build, no templates, tolerant of layout change. It is
wrong four times in a thousand and the four are undetectable — and a *perito* can be shown a
template and a check digit but cannot be shown why a model was confident. Rejected for the happy
path; retained as a bounded fallback.

**OCR-first regardless of the text layer.** Introduces character-recognition error into fields that
are already present as text.

**Manual entry with the PDF as an attachment.** Perfectly accurate and unworkable at any volume;
also loses the five-day clock's timeliness to keying delay.

**Requiring clients to upload a structured file instead.** They receive what the IMSS portal gives
them. Not our decision to make.

## What the first sample settled

A real *Constancia de presentación de movimientos afiliatorios* was examined on 2026-08-20. It
confirmed the pipeline's premises and corrected one of its decisions.

**Confirmed.** The PDF carries an extractable text layer (`A-015`), so automated extraction leaves
the critical path. The *Concentrado General* supports two independent cross-foots — `recibidos =
operados + rechazados`, and the operados total against the parsed row count (`FR-624`). Corroborating
values are richer than assumed: *folio*, *número de lote*, certificate serial, *sello digital*, and a
*huella digital* that is the IMSS's own hash of the lote — an integrity value produced outside NEO
and therefore evidentially worth more than any hash NEO computes over the same bytes (`FR-625`). The
document states its own legend of enumerations, which doubles as a layout fingerprint (`FR-641`). The
observed *NSS* validates under Luhn, confirming `FR-622`.

**Corrected.** I asserted above that the sample would settle nothing that changed the pipeline. That
was wrong: positional addressing (decision 3a) is a material change, and a template set built on
label proximity would have field-swapped silently rather than failing.

**Newly discovered, none of it inferable from the PRD.** A constancia carries up to three distinct
*registro patronal* values of which exactly one — the `Patrón` block's — is authoritative, and using
either of the others would silently misfile movements (`FR-634`). One document may hold several
`Patrón` blocks (`FR-635`). *Registro patronal* lengths differ within a single document, so a format
assertion would reject valid IMSS output (`FR-636`). Two date formats coexist in one document
(`FR-637`). Rejected *movimientos* are reported and mean the filing did not take effect, leaving the
five-day clock running (`FR-633`, `FR-833`). Rows carry an *extemporáneo* flag — the IMSS's own
lateness assessment — and a *tipo de trabajador* class specific to construction (`FR-638`, `FR-639`).

**Still outstanding.** One layout is verified. Samples of an *alta*, a *baja*, a *modificación de
salario*, and a document with `rechazados > 0` remain needed — the last because it is unknown whether
rejected rows are itemised or only counted. `OQ-035` asks whether the five-day window runs in calendar
or working days.

## Fixture handling

The sample is **not anonymised**. It contains a real *NSS*, *RFC*, worker name and *razón social*.
Golden fixtures under `FR-628` must therefore be either held outside the public repository or
synthesised — and a synthetic fixture has to reproduce the **coordinate layout**, not merely the text,
or it will not exercise the positional templates that decision 3a requires. A fixture that a
text-flow parser passes is a fixture that proves nothing.

## Revisit triggers

- The sample showing scanned rather than generated PDFs, which promotes the fallback from
  exceptional to routine and changes the review-queue staffing assumption.
- IMSS publishing a structured export, which would make most of this ADR obsolete in the best way.
