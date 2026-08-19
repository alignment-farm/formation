# Unselected-lineage behavior contact attempt

This directory is the public account of the one execution attempt licensed by
the [contact decision](../../docs/UNSELECTED_LINEAGE_CONTACT_DECISION.md). It is
not a runner-produced evidence packet. The runner module did not finish its
top-level imports or reach `main()`, so it created no evidence files and made no
provider or participant request.

## Outcome

The exact reviewed command was invoked once on 2026-08-18:

```text
python3 contact/unselected_lineage_behavior_contact.py --live --evidence-dir evidence/unselected-lineage-behavior-contact-20260818 --tokenizer-json /Users/macos-user/Library/Caches/formation/Qwen3-14B/7d3da9c56f02b22d31dc1ca97c7ee628d1e2e237/tokenizer.json
```

It exited with status 1 during top-level import, before `main()` began:

```text
ModuleNotFoundError: No module named 'micro_environment'
```

The reviewed runner was 55,951 bytes with SHA-256
`8c8b9f69a5913810a4850fee65d750968287c2d4057d95edb2085efc5f5ca679`.
Running that file by path made `contact/` the script import directory. The
root-level `micro_environment` package was therefore unavailable even though
the same runner imported correctly from repository-root tests.

## What did not happen

- The evidence destination was not reserved by the runner.
- Provider preflight did not run.
- Live transport was not constructed.
- The disposable interface call was not sent.
- Qwen received no request.
- No logical call, physical attempt, model output, environment result, score,
  or terminal verdict was produced.

This README was written after the failed command to preserve the operational
fact. Its presence is not evidence that the runner reached its evidence writer.

## Process finding

The focused tests called `main()` through an imported module. The peer reviews
checked the exact command and the runner's internal gates, but did not exercise
the command's import-only launch path. The project therefore proved the
runner's behavior after import without proving that its authorized entrypoint
could reach that behavior.

This is an interface failure in the research machinery, not an observation
about Qwen and not a Formation result. A future contact boundary would need a
no-transport smoke check of the exact launch command before it could authorize
model traffic.

## Closure

The contact decision is consumed by this pre-contact refusal. This account
licenses no path correction, environment-variable change, module-form command,
rerun, successor contact, validation packet, or Formation claim.

## Account review

The first independent Composer 2.5 and Grok 4.6 reviews both returned
`REVISE_ATTEMPT_ACCOUNT`. They found stale routing text that still described a
completed contact and null runner verdicts, plus imprecise language that placed
the failure before rather than during top-level import.

After those statements were repaired, both final read-only reviews returned
`ATTEMPT_ACCOUNT_STABLE`. Neither reviewer executed a runner command, edited
repository files, or contacted the participant model.
