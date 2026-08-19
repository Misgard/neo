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

**3. Extract with a declarative template per layout version** — anchored labels and column
boundaries over the PDF's text layer — held as configuration, not code. A new IMSS layout is a new
template, on the same principle as the versioned STPS export mapping.

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

## Open dependency

One redacted sample of each artifact type. It settles four things, none of which changes this
pipeline: whether the PDF has an extractable text layer (`A-015`); how many distinct layouts exist;
whether there is a count or total to cross-foot against; and whether a *sello* or verification
reference is present to capture. Template authoring is blocked on it. The pipeline is not.

## Revisit triggers

- The sample showing scanned rather than generated PDFs, which promotes the fallback from
  exceptional to routine and changes the review-queue staffing assumption.
- IMSS publishing a structured export, which would make most of this ADR obsolete in the best way.
