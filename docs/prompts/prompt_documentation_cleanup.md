# Prompt — Documentation cleanup

## 0. Role and mission

**Read `docs/prompts/common/` in full before anything else** — `00-context.md`, `01-method.md`,
`02-conventions.md`.

You are the **editor** for this block. Every other prompt in this directory adds; this one only
removes and consolidates. **You make no decisions and you re-open none.** If you find yourself
wanting to decide something, that is a finding for your summary, not a change.

The repository is design-first: there is no code, so the documents *are* the product. That makes
context cost a real cost. Every line a future session has to read to establish what is currently
true is a line that must earn its place.

---

## 1. The one principle

`docs/README.md` already states it: **living documents are edited in place and reflect today. Their
history lives in git.**

Three design sessions have not held to it. The failure mode is always the same shape — new text is
**appended beside** the text it supersedes instead of **replacing** it, so the document ends up
holding both, and a reader has to work out which one is live. Examples of the shape:

- A resolved question that keeps its options, trade-off and recommendation, with a `→ RESOLVED`
  paragraph underneath.
- An entry retained explicitly as an *"original framing"*.
- A note recording that a document contradicts another document, left in place of fixing one.
- A decision described as *"pending"* an open question that has since been settled.

**Rule for this session: a living document contains no account of its own editing history.** No
"corrected on", no "previously said", no "retained for the record". If a reader needs the old
version they run `git log`.

---

## 2. The rule that was misapplied, because it will be misapplied again

`02-conventions.md` says an ADR is never edited to change its decision — write a superseding one.

**That rule governs `Accepted` ADRs.** An ADR marked `Proposed` is a recommendation awaiting
sign-off; it is not yet a decision, and there is nothing anyone is relying on to protect. When the
sign-off comes back different, **edit the `Proposed` ADR**. Writing a superseding ADR against an
unsigned recommendation produces two documents where one would do, and leaves the reader to work out
which is live.

Part of your deliverable is making that distinction explicit in `02-conventions.md` so the next
session does not repeat it (§6).

---

## 3. What to clean, specifically

This inventory was taken on 2026-08-20. Verify each item still holds before acting on it, and
**extend the list** — it is a starting point and not a boundary.

### 3.1 PRD §13 — open questions

Fourteen entries carry a resolution appended beneath their original options. A resolved question does
not belong in a section titled *"Open questions and decisions pending"*.

- **Fully resolved:** `OQ-002`, `OQ-010`, `OQ-016`, `OQ-024`, `OQ-026`, `OQ-033`, `OQ-035`,
  `OQ-036`, `OQ-039`, `OQ-041`, `OQ-048`.
- **Resolved with a genuinely open remainder:** `OQ-004` (*PSC* quotes), `OQ-006` (further sample
  documents), `OQ-012` (whether any client needs SSO), `OQ-025` (platform residency), `OQ-037` (the
  subcontracting notice obligation). Trim each to **the remainder only** — the resolved framing is
  what the requirements it produced now say.
- **`OQ-035a`** exists solely as the *"original framing"* of `OQ-035` and is referenced by nothing.
  Delete it.

**The constraint that makes this non-trivial.** `scripts/check_docs.py` requires every referenced
identifier to remain **defined**, and a resolved `OQ` is still referenced from the requirements it
settled — `OQ-026` from `FR-522`–`FR-524`, `OQ-048` from `FR-1481`, `OQ-039` from `FR-077` and
`FR-1362`, and so on. So a settled question cannot simply be deleted: it must keep a **one-line
definition**. The shape to use is a ledger table at the end of §13 — *identifier, the question in a
clause, what was decided, where the decision now lives* — with the option text, the trade-off and
the resolution narrative all gone.

Decide and apply one consistent form. Do not leave two.

### 3.2 Stale cross-references inside ADRs

- `ADR-0005` decision 3 argues messaging cost from *"roughly 22,000 events a month"*. `A-001` now
  states 44,000. `ADR-0002` and `ADR-0007` argue from the same superseded figure, and `A-001`
  carries a reconciliation note saying their conclusions are unaffected. Either fix the three ADRs
  and delete the note, or keep the note and leave them — **but not both**, and say which you chose.
- Sweep every ADR for a reference to an `OQ` that is now settled, and for any decision described as
  *pending* something that has landed.

### 3.3 The `JORNADA` rename

`FR-2030` renamed the capture event to `CHECADA` and gave `JORNADA` its real meaning — one
continuous work period. Rather than rewriting every requirement written before it, `FR-2030` supplies
a **mapping rule**: prose saying *"jornada record"* means the `CHECADA` and the `JORNADA` it
composes.

A mapping rule is a form of the exact debt this session exists to remove. Decide whether to do the
sweep now — while there is no schema and no code — or to keep the mapping rule deliberately. If you
keep it, say why in your summary; if you sweep, `INV-010`, `INV-011`, `INV-012` and the `FR-5xx`
block are where most of the affected prose lives.

### 3.4 Duplication between documents

`docs/README.md` rule 1: a requirement lives in exactly one place and design documents reference it,
never restate it. `FR-1301` and `FR-1362` were one instance of the failure and are now reconciled.

- Sweep the PRD for another requirement pair defining the same thing.
- Audit `docs/system/workflows/` and `docs/system/screens.md` against rule 1. They were written to
  it, and that claim is worth checking rather than trusting.

### 3.5 Section ordering and structure

§6.13.4–§6.13.6 were moved back into reading order on 2026-08-20. Check the rest of the PRD's
headings run in order, and that no subsection sits under a parent it has nothing to do with.

---

## 4. Out of scope

- **Making, changing or re-opening any decision.** Including one you believe is wrong — that goes in
  your summary.
- **Deleting a live requirement, invariant or assumption.** Consolidating two that say the same
  thing is in scope; removing an obligation is not.
- **Changing what an `Accepted` ADR decided.**
- Rewriting prose you merely find inelegant. The test is *does a reader have to work out which of
  two statements is live* — not *would I have phrased it differently*.
- Adding requirements. This session's `FR` count should be zero.

---

## 5. Constraints

1. **`scripts/check_docs.py` passes** — no dangling references, no duplicate definitions, no
   unbalanced fences.
2. **No dangling references in any document**, not only the PRD. The gate checks `prd.md` and the
   ADR index; `workflows/`, `screens.md` and `threat-model.md` are unchecked and must be verified by
   hand or by a script you write.
3. **No requirement identifier is renumbered, ever.** A reference in a document, a commit message or
   somebody's notes must keep resolving.
4. **Every removal is a removal of duplication, not of content.** If a line is the only place
   something is stated, it stays — however awkwardly it reads.
5. Language and identifier conventions are unchanged (`02-conventions.md`).

---

## 6. Deliverables

1. The edits themselves, across `docs/system/prd.md`, `docs/system/adr/*.md` and anything else the
   inventory reaches.
2. An addition to **`docs/prompts/common/02-conventions.md`** recording, so this does not recur:
   how a resolved `OQ` is retired (the ledger form you chose, and why the identifier must stay
   defined); that a `Proposed` ADR is edited in place while an `Accepted` one is superseded; and that
   living documents carry no changelog notes.
3. A **summary listing every deletion**, each with one line saying where the content now lives or
   that git holds it. This is the artifact that makes the session reviewable — a cleanup nobody can
   audit is indistinguishable from a cleanup that lost something.
4. Any decision you found yourself wanting to make, listed and **not made**.

**Definition of done:** PRD §13 contains only questions that are genuinely open; no document
contains an account of its own editing history; no reader has to choose between two statements of the
same fact; the gate passes; and the diff is almost entirely deletions.

---

## 7. A note on method

Work by deletion and re-read, not by rewriting. For each candidate, ask the two questions in order:
**is this stated anywhere else?** and **does a reader need it to know what is true today?** If the
answers are *yes* and *no*, it goes.

Run `scripts/check_docs.py` after every few edits rather than at the end. A dangling reference is
trivial to fix when you have just made it and tedious to locate an hour later.

Expect the diff to be large and almost entirely subtraction. If it is not, you have started
rewriting instead of editing, which is a different task and not this one.

---

## Start here

Open as `docs/prompts/common/01-method.md` specifies: your understanding in five sentences or fewer,
your blocking questions with options and recommendations, your non-blocking questions listed only,
and anything you find that looks wrong rather than merely redundant.

On that last item: a cleanup pass reads every document closely and in sequence, which is the only
time anybody does. **You will find live contradictions that nobody has noticed.** Those are findings
for your summary, not repairs — flag them, name the documents, and leave them for whoever owns the
decision.

Wait for answers before writing.
