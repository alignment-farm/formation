# Evidence

This directory records model contacts and deterministic diagnostics derived
from retained contacts. Each committed run keeps a short explanation beside
its computed result, frozen specimen, provider receipt, and the hashes that bind
those records to the raw model traffic.

Start with a run's `README.md`. Raw per-attempt requests and responses remain
in ignored local `attempts/` directories and are backed up outside Git. The
committed packet preserves their request and response hashes, status, retry,
outcome, and scoring record so an external copy can be verified.

For the project’s current state and active empirical question, read the root
[README](../README.md#present-state). This index does not maintain a second
current-state narrative.

## How to read one run

| Item | What it contains |
| --- | --- |
| `README.md` | The question, result, meaning, limits, and the next step proposed when that run closed. |
| `packet.json` | The computed calls, distributions, and verdict used by the runner. |
| `specimen.json` | The cases and identities fixed before the run. |
| `provider.json` | The exact model and interface receipt, when a model was called. |
| Local `attempts/` | Every raw request, response, and transport record. Ignored by Git and retained in the external evidence backup. |

The README explains the result. The packet lets code recompute it and binds its
claims to the externally retained raw attempts by hash.

## Recent experimental chain

| Experiment | Main result |
| --- | --- |
| [Same-request repeats](same-request-variation-20260819T231848Z/README.md) | One exact request returned different actions, so later comparisons began using repeated distributions. |
| [Repeated developmental comparison](distributional-developmental-20260819T233903Z/README.md) | Raw experience, a model-written lesson, its removal, and a static instruction produced the same behavior. |
| [Canonical lesson authorship](canonical-mapping-authorship-20260819T235351Z/README.md) | The model wrote a correct lesson and its later actions changed, but unrelated actions were harmed. |
| [Fresh continuation](scoped-candidate-continuation-20260819T235912Z/README.md) | The narrow matching effect repeated; the first unrelated case did not expose the known harm. |
| [Frozen candidate validation](canonical-mapping-candidate-validation-20260820T000646Z/README.md) | The model-written lesson changed all matching actions, but a supplied answer-like lesson did too. The verdict was null. |
| [Wider unrelated-case test](candidate-nontransfer-sweep-20260820T001430Z/README.md) | The lesson preserved upward cases but reversed almost every downward case. |
| [Family-gate test](canonical-mapping-scope-gate-validation-20260820T001909Z/README.md) | The gate blocked the known harm, but the lesson itself did not guide matching upward cases reliably. |
| [Representation forms](representation-class-exploration-20260820T010342Z/README.md) | Sentence, table, and policy forms exposed separate failures in lesson writing and lesson use. |
| [Correct lesson consumption](representation-consumption-calibration-20260820T112303Z/README.md) | Sentence and table lessons worked across every matching device; the policy did not, and both successful forms still need a family gate. |
| [Staged lesson authorship](staged-observation-authorship-20260820T115153Z/README.md) | A model-written direct observation repaired table authorship across all eight fresh experiences. |
| [Staged action chain](staged-observation-action-chain-20260820T115845Z/README.md) | The full chain changed every matching action and the gate prevented 21 unrelated errors; one raw-history cell kept the frozen verdict null. |
| [Four-world validation](staged-chain-validation-20260820T121232Z/README.md) | Exact staged lessons made 29/32 matching actions and preserved unrelated action, but two frozen thresholds missed. |
| [Balanced validation](balanced-relation-staged-validation-20260820T122857Z/README.md) | Exact staged lessons made 33/36 matching actions across both true relations; one difficult upward cell kept the verdict null. |
| [Staged sentence and table](staged-representation-consumption-20260820T124630Z/README.md) | Both exact model-written forms made 36/36 matching actions; the formal table preference reflects a scorer limitation. |
| [Aggregate staged validation](staged-chain-aggregate-validation-20260820T130635Z/README.md) | The staged mechanism made 48/48 matching actions, preserved unrelated action, and passed its frozen bounded validation. |
| [Revision exploration](staged-table-revision-20260820T133010Z/README.md) | Exact revisions made 21/24 post-change actions; the supplied table failed the same one cell and the frozen verdict was null. |
| [Revision validation](staged-table-revision-validation-20260820T134318Z/README.md) | Revised tables made 48/48 post-change actions and passed the frozen bounded revision validation. |
| [Two-table accumulation](staged-table-accumulation-20260820T140646Z/README.md) | External gating retained both lessons, while joint delivery favored the first family; the verdict was null. |
| [Container diagnostic](accumulated-table-container-20260820T142422Z/README.md) | List order shifted the favored family, a keyed prompt object did not repair selection, and the verdict was null. |
| [First learned clerk](learned-clerical-instrument-20260820T161702Z/README.md) | Restricted classification reached 10/12, but effect encoding and participant delivery failed. |
| [Structural delivery calibration](structural-record-delivery-20260820T162946Z/README.md) | A short effect sentence and current-family table each made 32/32 actions; other JSON forms failed. |
| [Staged clerk successor](staged-clerical-instrument-20260820T164000Z/README.md) | Transcription and structural normalization worked, but reversed sentence order blocked later use. |
| [Canonical record diagnostic](canonical-clerical-record-20260820T165350Z/README.md) | Named fields still failed when the clerk had to infer an unstated opposite effect. |
| [Clerical prose parser](clerical-prose-parser-20260820T170434Z/README.md) | Parsing two explicit facts produced 4/4 exact records and a pipeline candidate. |
| [Learned-instrument validation](learned-clerical-instrument-validation-20260820T171748Z/README.md) | The complete fresh chain made 48/48 matching actions, preserved unrelated action, and passed its frozen validation. |
| [Learned revision exploration](learned-clerical-revision-20260820T174848Z/README.md) | Newest exposed records made 24/24 post-change actions, but hidden-consequence clerks invented unsupported records. |
| [Source-grounded admission](source-grounded-revision-admission-20260820T180358Z/README.md) | Exact provenance blocked all four missing-movement proposals but deliberately did not judge record truth. |
| [Learned source verifier](clerical-source-support-verifier-20260820T180818Z/README.md) | It returned valid labels but accepted 9/12 stale opposite records, so the verdict was null. |
| [Selected-effect projection](clerical-selected-effect-projection-20260820T181202Z/README.md) | The clerk copied the requested proposed-record field exactly on 48/48 calls. |
| [Composed record admission](composed-clerical-record-admission-20260820T181541Z/README.md) | Exact composition admitted all 24 supported retained records and quarantined all 24 unsupported ones. |
| [Fresh composed validation](composed-clerical-revision-validation-20260820T183033Z/README.md) | All mechanism comparisons passed, but one invalid raw-control cell triggered the frozen `not_engaged` verdict. |
| [Engagement successor](composed-clerical-revision-engagement-successor-20260820T185545Z/README.md) | Admitted revisions made 45/48 matching actions, tied supplied revisions, lost their benefit under removal, and passed the corrected frozen validation. |
| [Selective longer lineage](selective-longer-lineage-revision-20260820T192314Z/README.md) | Version 3 acted only in scope A and preserved scope B, but one source action lacked frozen attribution to version 2, so the verdict was null. |
| [Counterevidence authority](counterevidence-authority-diagnostic-20260820T194134Z/README.md) | A zero-call reconstruction separates 4/4 observation-grounded admissions from 3/4 action-attributed admissions without changing the null. |
| [Observational counterevidence](observational-counterevidence-comparison-20260820T195003Z/README.md) | Deliberate exploration earned 48/48 action under the observation governor; attribution quarantine and removal retained only unchanged scope B. |
| [Contested accumulation](contested-counterevidence-accumulation-20260820T200609Z/README.md) | Four append-only histories reach distinct governance states without collapsing source occurrences into a vote. |
| [Learned uncertain-evidence continuation](learned-contested-counterevidence-continuation-20260820T214847Z/README.md) | Clerk and governor mechanics passed, but recovered delivery tied removal, leaving the frozen behavioral verdict null. |
| [Mirrored recovery influence](mirrored-recovery-influence-successor-20260820T221149Z/README.md) | Public-identical opposite worlds made recovery causal: learned and supplied records scored 48/48; cold and removal scored 24/48. |
| [Uncertain-consequence policy](uncertain-consequence-policy-specimen-20260820T222304Z/README.md) | Two confirmations removed wrong active records in five authored histories but increased withholding and adaptation delay. |
| [Suspension consequences](suspension-consequence-specimen-20260820T222814Z/README.md) | Reversible task actions made current, newest, cold, and explore policies observationally equivalent. |
| [Asymmetric suspension domain](asymmetric-suspension-domain-20260820T223216Z/README.md) | A wrong task action can now fail irreversibly while a lower-cost diagnostic preserves the device and reveals a useful signal. |
| [Asymmetric probe clerical contact](asymmetric-probe-clerical-contact-20260820T224335Z/README.md) | Learned signal records matched supplied guidance at 24/24, lost their benefit under removal, and reversed all outcomes when inverted. |
| [Self-directed probe contact](self-directed-probe-contact-20260820T225832Z/README.md) | The catalog guided 17/18 known signals but did not cause probing and guessed beyond its evidence, producing a harmful verdict. |
| [Explicit applicability receipt](explicit-applicability-receipt-contact-20260820T231222Z/README.md) | Every unsafe control held under changed wording, so the receipt comparison did not engage. |
| [Matched applicability receipt](matched-applicability-receipt-successor-20260820T232130Z/README.md) | Exact unsafe controls recurred; an explicit empty match receipt replaced six unsupported guesses with six holds. |

For the older sequence, use the [research history](../docs/RESEARCH_HISTORY.md)
instead of opening directories by date.

## What these records can support

Evidence can support only the comparison that produced it. A working prompt,
a correct answer, or a changed action is not automatically evidence that the
model developed. A beneficial developmental claim still needs a same-model
baseline, new cases where the effect should transfer, cases where it should
not transfer, and an external result that does not come from the model's own
explanation.

Evidence does not govern the runtime and does not enter later model prompts
unless a frozen experiment explicitly permits it.
