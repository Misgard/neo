# Common — working method

## The hard rule on uncertainty

If a decision is required and the information is not in the documents you were told to read, **do
not invent it. Stop and ask.**

Every question carries three things:

1. At least two concrete options.
2. The trade-off of each — what it costs, not just what it gives.
3. Your recommendation, with the reasoning that produced it.

Group questions into **blocking** — you cannot produce the deliverable without an answer — and
**non-blocking** — you can proceed and record it as an open item. Ask the blocking ones before
writing anything. Record the non-blocking ones as `OQ-###` in PRD §13, with options and a
recommendation, in the same form.

A question is blocking only if proceeding under any assumption would produce work that is wrong or
useless if the assumption fails. If a sensible default exists, take it, state it as an assumption,
and keep going.

## Decisions already made

**Do not re-open a decided ADR.** An ADR marked `Accepted` follows from an answer already given;
one marked `Proposed` is a recommendation awaiting sign-off and is your working assumption until
told otherwise.

If you believe a decision is wrong, **say so explicitly and separately** — name the ADR, state the
problem, propose superseding it. Never quietly design around a decision; a silent workaround leaves
two contradictory sources of truth and nobody knows which is live.

## Never resolve an open question in passing

`OQ-###` entries exist because someone has to choose. Picking one in a design document, or
implicitly in a diagram, is not a decision — it is a decision made invisibly. Ask.

## Open every session this way

Before writing anything, reply with:

1. Your understanding of the task, in five sentences or fewer.
2. Your **blocking** questions, in priority order, in the form above.
3. Your **non-blocking** questions, listed only.
4. Anything in the PRD or the ADRs that looks wrong, risky, or internally inconsistent in light of
   what you now have to decide. Name it explicitly. This is often the most valuable thing a session
   produces, and it is the part that gets skipped under time pressure.

Then wait.

## Definition of done

- Every decision traces to the PRD, to an existing ADR, or to an answer given in the session.
- No requirement is invented. If you need behaviour the PRD does not specify, **add the requirement
  first**, then design against it.
- Every gap is an open question with options and a recommendation — never papered over, never left
  as a `TODO`.
- Where your work closes or narrows an `OQ-###`, update that entry to point at what closed it.
