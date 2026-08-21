# Model-authored representation class exploration

Status: **frozen before contact under the session-wide human authorization**.

## Question

Can a cold model turn one experienced consequence into a representation that
guides later action in both target directions across fresh devices?

This experiment compares three kinds of representation. The harness supplies
their empty form, but it does not fill in the controller family, effects, or
policy choices:

1. a sentence that states what the first and second displayed controls do;
2. a JSON effect table that assigns movement to each displayed slot; and
3. a JSON target policy that assigns a displayed slot to targets above and
   below the current position.

The later cold-model interface receives the exact model-authored bytes as
retained material. No parser or mechanical applicator turns that material into
an action.

## Comparison

Two fresh opaque controller families share the counter-prior profile in which
the second displayed control increases position. One acquisition targets above
and the other targets below. Each resulting occurrence is paired with its
environment-issued consequence.

For every world and representation class, one author sees the consequence and
one sees the same occurrence with the consequence withheld. Every authored
result continues, including malformed or unavailable output.

Fresh matching-family devices test targets above and below. Four identical
requests are made for empty retention and for every exposed and withheld
representation. Fresh opposite-profile families test empty retention and each
exposed representation without a scope gate. These diagnostic calls reveal
whether a representation carries harm outside its source family. The already
implemented exact-family gate remains available as a later substrate mechanism;
it is not credited with making a representation usable.

## Budget and evidence

The exact model is `ai/qwen3:14B-Q6_K`, artifact digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`,
through the unchanged Docker Model Runner chat interface.

The schedule contains 190 logical calls:

- two acquisition actions;
- twelve authorship calls; and
- 176 later action calls.

The physical ceiling is 198 attempts. Only transport failures may be retried,
with at most eight retries. The run stops after the fixed schedule or either
ceiling. Raw requests and responses, the frozen specimen, provider identity,
computed packet, and replay result are retained under
`evidence/representation-class-exploration-<run-id>/`.

## Prospective interpretation

A representation class is a bidirectional candidate only when, in both worlds:

- consequence-exposed authorship exactly fills the frozen form;
- exposed delivery scores at least three of four on targets above and below;
- exposed delivery beats empty retention by at least two actions in each
  direction;
- exposed delivery beats its consequence-withheld counterpart by at least two
  actions in each direction; and
- no matching cell contains more than one malformed or unavailable result.

A class that meets the action requirements in only one direction is recorded as
one-directional. A class whose exposed author does not fill the form exactly is
not authored. Any loss of at least two actions against empty retention on a
nonmatching case is recorded as ungated harm.

Finding a bidirectional class would select a candidate substrate for a later
frozen comparison. It would not establish Formation. A null result would leave
representation robustness as the active problem and would argue against more
minor wording changes inside these three forms.
