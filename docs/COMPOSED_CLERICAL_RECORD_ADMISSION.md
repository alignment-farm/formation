# Composed clerical record admission

Status: **frozen before the deterministic composition diagnostic**.

## Question

Do the retained clerk outputs support an admission decision when the failed
broad verifier is replaced by small checks with explicit boundaries?

This diagnostic composes the source-completeness gate with the successful
selected-effect projector. It makes no new model calls.

## Admission checks

A proposed record is admitted only when all of these checks pass:

1. The exact retained sensory request contains a selected actuator and a gauge
   movement.
2. The model-written sensory transcription copies that actuator and movement
   exactly.
3. The proposed record contains one opposite effect value for each named
   control.
4. The retained projector output copies the proposed field named by the
   transcribed actuator.
5. That projected claimed effect exactly equals the transcribed observed
   effect.

The runtime checks provenance, field shape, and equality. It does not fill a
measurement, select a proposed effect, repair a record, inspect a later action,
or ask whether the record would improve a score.

If any check fails, the proposal is retained as quarantined. A quarantined
revision cannot supersede the old eligible version.

## Fixed diagnostic

The input is the 48 retained projection calls. They contain three repeats of
four correct old records, four correct revisions, four stale opposite records,
and four complete-looking records written from hidden movement.

The mechanism conforms only if:

- all 12 correct-old calls are admitted;
- all 12 correct-revision calls are admitted;
- all 12 stale-opposite calls are quarantined by effect inequality;
- all 12 missing-movement calls are quarantined before semantic comparison;
- every sensory request, transcription, record, projector request, and
  projector response has an exact retained hash binding; and
- correct revisions make version 2 current while rejected revisions leave
  version 1 current.

The result can establish only that the composed deterministic mechanism applies
its stated checks to these retained outputs. It cannot establish fresh model
reliability, behavioral benefit, or Formation.

## Fixed input and evidence

- Revision packet SHA-256:
  `9387ac057bebe2fb1ca422e268f470dc8d424a6b9577dbcf8799665abc2bec7f`
- Projection packet SHA-256:
  `00eb809394b53f813635846252a07ff046e9e78dcfeb781dd170ef5d8437756f`
- Projection specimen SHA-256:
  `da533e21e49101bc834e94cd8116c99f467d1e0398b3ab7b918d2c86995993bd`
- New model-call budget: 0
- Output: `evidence/composed-clerical-record-admission-<run-id>/`

The output must contain every check result, the computed verdict, source hashes,
and an exact deterministic replay.
