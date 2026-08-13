# Writing and teaching technical work

## Purpose

Write so a reader can understand the idea, use it, and explain it to someone
else.

This guide applies the Feynman method to technical writing: explain the subject
in plain language, find the parts you cannot explain, return to the evidence,
and revise until the causal steps are clear. The result expands the audience.
It also reveals the writer's level of understanding. Compressed prose can hide
that the writer does not yet know what a label means or how one step causes the
next.

Use this guide for public-facing findings, project summaries, README prose,
release notes, and explanations meant to travel beyond the people who produced
the work. Internal identifiers may remain when they support audit or precision,
but the surrounding text must explain them.

This guide does not govern inter-agent messages, working notes, review packets,
test names, or other internal coordination. Those may use shared shorthand when
it improves speed and precision. If an internal result becomes a published
finding, rewrite it for a reader who does not share that context. Do not publish
the shorthand as the explanation.

## Core rule

Explain the subject in plain words for a reader who is new to it. Clear writing
is evidence of clear thought. Do not hide weak reasoning behind jargon, labels,
or broad claims.

A sentence such as `W-2 capture fail-open of sequence precommit` may be compact
for its authors, but it does not teach a finding. Write the causal account:

> In test W-2, the system recorded sequence state before the commit completed.
> If that recording step failed, the commit continued instead of stopping.

The identifier remains available for audit. The explanation tells a new reader
what happened, when it happened, and why the failure matters.

## Writing style

- Start with the main point.
- Use short words and short sentences when they are enough.
- Prefer concrete facts, actions, and examples.
- Define terms that a new reader may not know.
- Use technical terms only when they add precision.
- Explain what a thing does, how it works, and why it matters. Do not give only
  its name.
- Keep one main idea in each paragraph.
- Put ideas in an order that a reader can follow from start to finish.
- Remove filler, repetition, and claims that do not add meaning.
- Use lists only when the items are distinct.

## Reasoning process

Before writing:

1. State the idea in plain language.
2. Check each step in the explanation.
3. Find gaps, vague terms, and unsupported claims.
4. Read the source or inspect the evidence needed to fill those gaps.
5. Rewrite the explanation in a simpler order.

Do not pretend to know what you cannot explain. State what is unknown and what
would resolve it.

## Revision check

Before sending or saving text, ask:

- Can a new reader follow this without hidden context?
- Does each technical term have a clear meaning?
- Did I explain the cause or process, not just give it a label?
- Are all key claims supported by facts, code, or a source?
- Can any sentence be shorter without losing meaning?
- Does the text flow in a useful order?

If any answer is no, revise the text.

## Responses

- Answer the request first.
- Give enough context to make the answer usable.
- Show a small example when it makes the idea clearer.
- If the request is unclear, inspect available context before asking a question.
- If a choice matters, state the choice and the reason for it.
- Do not use praise, filler, or a sign-off.

## Avoid

- stock transitions;
- symmetrical phrasing used in place of an explanation;
- abstract claims without the event, mechanism, or evidence behind them;
- repeated contrast patterns;
- prose that sounds more polished than precise;
- unexplained internal labels or compressed finding names; and
- bragging or comparison with external work.
