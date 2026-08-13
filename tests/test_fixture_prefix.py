from __future__ import annotations

import copy
from dataclasses import replace
import hashlib
from pathlib import Path
import unittest

from formation.fixture_prefix import (
    FrozenPrefixHandoff,
    HandoffRefusal,
    MATERIALIZER,
    PrefixSourceRefusal,
    RuntimePrefixMaterializer,
    adapt_fixture_prefix_source,
    expected_fixture_artifact,
)
from trajectory.fixture_fork import (
    ALGORITHM,
    IDENTITY_CONTRACT,
    ForkController,
    ForkRefusal,
    PrefixBinding,
    PrefixWitness,
    PrefixValidationRefusal,
    compute_binding,
    validate_fixture_prefix,
)


EXPECTED_DIGEST = "1a219122dec8b02544ef5502194da8e9920ebc2aaa7168a8dabb38eae71e4a0d"


class ExtraFieldBinding(PrefixBinding):
    def __init__(self, binding: PrefixBinding) -> None:
        super().__init__(
            binding.materializer,
            binding.identity_contract,
            binding.algorithm,
            binding.digest,
            binding.byte_length,
        )
        object.__setattr__(self, "extra", "forbidden")

    def __eq__(self, other) -> bool:
        return isinstance(other, PrefixBinding) and all(
            getattr(self, field) == getattr(other, field)
            for field in (
                "materializer",
                "identity_contract",
                "algorithm",
                "digest",
                "byte_length",
            )
        )


def clean_receipts() -> list[dict]:
    return [
        {
            "contract": "fixture-v0",
            "coordinate": "D-C-001",
            "record": "developmental",
            "order": 1,
            "event": "practitioner_initialized",
            "authority": "formation_runtime",
            "parents": [],
            "retention": "inline",
            "payload": {
                "model_identity": "cold-model-stub-v0",
                "model_configuration": "deterministic-v0",
                "runtime_interface": "formation-runtime-v0",
                "initial_lineage_head": None,
                "supported_interfaces": [
                    "practice-v0",
                    "formation-procedure-v0",
                    "governance-v0",
                    "influence-v0",
                    "replay-v0",
                ],
            },
        },
        {
            "contract": "fixture-v0",
            "coordinate": "D-C-002",
            "record": "developmental",
            "order": 2,
            "event": "encounter_opened",
            "authority": "formation_runtime",
            "parents": ["D-C-001"],
            "retention": "inline",
            "payload": {
                "encounter": "E-C-001",
                "candidate_object": "render-17",
                "derived_from": "atlas",
                "artifact_revision": 41,
                "authority_revision": 42,
                "depends_on_current_authority": True,
                "commit_action": "publish",
                "refresh_action": "refresh_then_publish",
            },
        },
        {
            "contract": "fixture-v0",
            "coordinate": "D-C-003",
            "record": "developmental",
            "order": 3,
            "event": "model_invoked",
            "authority": "formation_runtime",
            "parents": ["D-C-002"],
            "retention": "inline",
            "payload": {
                "encounter": "E-C-001",
                "invocation": "I-C-001",
                "stub": "blind-commit-v0",
                "cold_invocation": True,
                "request_binding": "D-C-002",
                "output_authority": "cold_model",
                "output": "publish",
            },
        },
        {
            "contract": "fixture-v0",
            "coordinate": "D-C-004",
            "record": "developmental",
            "order": 4,
            "event": "action_committed",
            "authority": "formation_runtime",
            "parents": ["D-C-003"],
            "retention": "inline",
            "payload": {
                "encounter": "E-C-001",
                "invocation": "I-C-001",
                "action": "A-C-001",
                "action_name": "publish",
                "target": "render-17",
            },
        },
        {
            "contract": "fixture-v0",
            "coordinate": "D-C-005",
            "record": "developmental",
            "order": 5,
            "event": "consequence_observed",
            "authority": "environment",
            "parents": ["D-C-004"],
            "retention": "inline",
            "payload": {
                "encounter": "E-C-001",
                "action": "A-C-001",
                "consequence": "K-C-001",
                "source": "fixture-environment-v0",
                "outcome": "rejected",
                "reason": "stale_dependency",
                "observed_rule": "artifact_revision_must_equal_authority_revision",
            },
        },
        {
            "contract": "fixture-v0",
            "coordinate": "D-C-006",
            "record": "developmental",
            "order": 6,
            "event": "experience_closed",
            "authority": "formation_runtime",
            "parents": ["D-C-002", "D-C-005"],
            "retention": "inline",
            "payload": {
                "encounter": "E-C-001",
                "included_events": [
                    "D-C-002",
                    "D-C-003",
                    "D-C-004",
                    "D-C-005",
                ],
                "consequence": "K-C-001",
                "applicability_claim": None,
            },
        },
    ]


def clean_runtime(run_id: str = "run-clean"):
    runtime = RuntimePrefixMaterializer(run_id)
    source = adapt_fixture_prefix_source(run_id, clean_receipts())
    handoff = runtime.materialize(source)
    return runtime, handoff


def mutate_scalar(value):
    if value is None:
        return "not-null"
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return value + "-mutated"
    raise TypeError(value)


def scalar_paths(value, path=()):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from scalar_paths(item, path + (key,))
    elif isinstance(value, list):
        if not value:
            yield path
        else:
            for index, item in enumerate(value):
                yield from scalar_paths(item, path + (index,))
    else:
        yield path


def mutate_at(value, path):
    target = value
    for part in path[:-1]:
        target = target[part]
    if not path:
        raise ValueError("root mutation unsupported")
    leaf = path[-1]
    if isinstance(target[leaf], list) and not target[leaf]:
        target[leaf].append("mutated")
    else:
        target[leaf] = mutate_scalar(target[leaf])


def omission_paths(value, path=()):
    if isinstance(value, dict):
        for key, item in value.items():
            yield path + (key,)
            yield from omission_paths(item, path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield path + (index,)
            yield from omission_paths(item, path + (index,))


def omit_at(value, path):
    target = value
    for part in path[:-1]:
        target = target[part]
    del target[path[-1]]


class FixturePrefixTests(unittest.TestCase):
    def test_clean_artifact_and_binding_match_contract(self):
        runtime, handoff = clean_runtime()
        self.assertEqual(handoff.artifact, expected_fixture_artifact())
        self.assertEqual(len(handoff.artifact), 2303)
        self.assertEqual(hashlib.sha256(handoff.artifact).hexdigest(), EXPECTED_DIGEST)
        self.assertEqual(handoff.artifact.count(b"\n"), 6)
        self.assertTrue(handoff.artifact.endswith(b"\n"))

        controller = ForkController(runtime)
        self.assertEqual(
            validate_fixture_prefix(handoff.artifact),
            "valid_fixture_prefix_bytes",
        )
        witness = controller.witness(handoff)
        self.assertEqual(
            witness.binding,
            PrefixBinding(MATERIALIZER, IDENTITY_CONTRACT, ALGORITHM, EXPECTED_DIGEST, 2303),
        )
        roots = [controller.fork(handoff, witness, witness.binding) for _ in range(3)]
        self.assertTrue(all(root.artifact is handoff.artifact for root in roots))

    def test_document_literal_matches_implementation(self):
        document = Path("docs/MATERIALIZATION.md").read_text()
        literal = document.split("```jsonl\n", 1)[1].split("```", 1)[0].encode()
        self.assertEqual(literal, expected_fixture_artifact())

    def test_every_source_leaf_affects_output_or_refuses(self):
        original = clean_receipts()
        paths = list(scalar_paths(original))
        self.assertGreater(len(paths), 70)
        for index, path in enumerate(paths):
            with self.subTest(path=path):
                changed = copy.deepcopy(original)
                mutate_at(changed, path)
                runtime = RuntimePrefixMaterializer(f"run-mutation-{index}")
                try:
                    source = adapt_fixture_prefix_source(runtime.run_id, changed)
                    artifact = runtime.materialize(source).artifact
                except PrefixSourceRefusal:
                    continue
                self.assertNotEqual(artifact, expected_fixture_artifact())
                with self.assertRaisesRegex(
                    PrefixValidationRefusal, "invalid_fixture_prefix_bytes"
                ):
                    validate_fixture_prefix(artifact)

    def test_source_omissions_refuse(self):
        original = clean_receipts()
        paths = list(omission_paths(original))
        self.assertGreater(len(paths), 100)
        for index, path in enumerate(paths):
            with self.subTest(path=path):
                receipts = copy.deepcopy(original)
                omit_at(receipts, path)
                runtime = RuntimePrefixMaterializer(f"run-omission-{index}")
                try:
                    source = adapt_fixture_prefix_source(runtime.run_id, receipts)
                    artifact = runtime.materialize(source).artifact
                except PrefixSourceRefusal:
                    continue
                self.assertNotEqual(artifact, expected_fixture_artifact())
                with self.assertRaises(PrefixValidationRefusal):
                    validate_fixture_prefix(artifact)

    def test_validator_refuses_independent_artifact_mutations(self):
        clean = expected_fixture_artifact()
        lines = clean.splitlines(keepends=True)
        mutations = {
            "changed_value": clean.replace(b"render-17", b"render-18", 1),
            "omitted_line": b"".join(lines[:2] + lines[3:]),
            "reordered_line": b"".join([lines[1], lines[0], *lines[2:]]),
            "duplicated_line": b"".join([lines[0], *lines]),
            "extra_line": clean + lines[0],
            "trajectory_field": clean.replace(
                b'"record":"developmental"',
                b'"record":"developmental","branch_label":"governed"',
                1,
            ),
            "trajectory_receipt": clean + b'{"coordinate":"T-C-001"}\n',
            "expected_result": clean.replace(
                b'"record":"developmental"',
                b'"record":"developmental","expected_result":"wire_pass"',
                1,
            ),
            "scorer_field": clean.replace(
                b'"record":"developmental"',
                b'"record":"developmental","scorer_verdict":"pass"',
                1,
            ),
            "key_order": clean.replace(
                b'{"contract":"fixture-v0","coordinate":"D-C-001"',
                b'{"coordinate":"D-C-001","contract":"fixture-v0"',
                1,
            ),
            "whitespace": clean.replace(b'"contract"', b' "contract"', 1),
            "crlf": clean.replace(b"\n", b"\r\n"),
            "missing_final_lf": clean[:-1],
            "equivalent_reencoding": b"\n".join(line.rstrip() + b" " for line in lines),
        }
        for name, artifact in mutations.items():
            with self.subTest(name=name), self.assertRaisesRegex(
                PrefixValidationRefusal, "invalid_fixture_prefix_bytes"
            ):
                validate_fixture_prefix(artifact)

    def test_raw_forged_other_run_wrong_head_and_stale_handoffs_refuse(self):
        runtime, handoff = clean_runtime("run-a")
        controller = ForkController(runtime)
        with self.assertRaisesRegex(HandoffRefusal, "typed_handoff_required"):
            controller.witness(handoff.artifact)

        forged = replace(handoff, _issuer=object())
        with self.assertRaises(HandoffRefusal):
            controller.witness(forged)

        other_runtime, other_handoff = clean_runtime("run-b")
        with self.assertRaises(HandoffRefusal):
            controller.witness(other_handoff)

        wrong_head = replace(handoff, source_head="D-C-005")
        with self.assertRaises(HandoffRefusal):
            controller.witness(wrong_head)

        runtime.close()
        with self.assertRaisesRegex(HandoffRefusal, "stale_or_forged_handoff"):
            controller.witness(handoff)
        other_runtime.close()

    def test_fork_refuses_wrong_witness_and_binding(self):
        runtime, handoff = clean_runtime()
        controller = ForkController(runtime)
        witness = controller.witness(handoff)

        mutations = [
            replace(witness.binding, materializer="unknown"),
            replace(witness.binding, identity_contract="unknown"),
            replace(witness.binding, algorithm="sha-512"),
            replace(witness.binding, digest=witness.binding.digest.upper()),
            replace(witness.binding, digest="0" * 64),
            replace(witness.binding, byte_length=2302),
            replace(witness.binding, byte_length=True),
        ]
        for binding in mutations:
            with self.subTest(binding=binding), self.assertRaises(ForkRefusal):
                controller.fork(handoff, witness, binding)

        wrong_witnesses = [
            replace(witness, coordinate="T-C-003"),
            replace(witness, handoff_id="other"),
            replace(witness, run_id="other"),
            replace(witness, source_head="D-C-005"),
        ]
        for changed_witness in wrong_witnesses:
            with self.subTest(witness=changed_witness), self.assertRaises(ForkRefusal):
                controller.fork(handoff, changed_witness, witness.binding)

        with self.assertRaisesRegex(ForkRefusal, "complete_prefix_binding_required"):
            controller.fork(handoff, witness, witness.binding.__dict__)
        with self.assertRaisesRegex(ForkRefusal, "complete_prefix_binding_required"):
            controller.fork(handoff, witness, ExtraFieldBinding(witness.binding))

        forged_equal_witness = replace(witness)
        with self.assertRaisesRegex(ForkRefusal, "exact_prefix_witness_required"):
            controller.fork(handoff, forged_equal_witness, witness.binding)

        with self.assertRaisesRegex(ForkRefusal, "prefix_witness_already_issued"):
            controller.witness(handoff)

        for replacement in (
            handoff.artifact,
            Path("prefix.jsonl"),
            {"artifact": handoff.artifact},
        ):
            with self.subTest(replacement=replacement), self.assertRaisesRegex(
                HandoffRefusal, "typed_handoff_required"
            ):
                controller.fork(replacement, witness, witness.binding)

    def test_post_binding_changed_bytes_refuse_in_identity_checker(self):
        runtime, handoff = clean_runtime("run-tamper")
        controller = ForkController(runtime)
        witness = controller.witness(handoff)

        object.__setattr__(
            handoff,
            "artifact",
            handoff.artifact.replace(b"render-17", b"render-18", 1),
        )
        with self.assertRaisesRegex(ForkRefusal, "branch_binding_mismatch"):
            controller.fork(handoff, witness, witness.binding)

    def test_forged_witness_cannot_bypass_validation(self):
        receipts = clean_receipts()
        receipts[1]["payload"]["candidate_object"] = "invalid-artifact"
        runtime = RuntimePrefixMaterializer("run-invalid")
        source = adapt_fixture_prefix_source(runtime.run_id, receipts)
        handoff = runtime.materialize(source)
        controller = ForkController(runtime)

        with self.assertRaises(PrefixValidationRefusal):
            controller.witness(handoff)

        forged_binding = compute_binding(handoff.artifact)
        forged_witness = PrefixWitness(
            coordinate="T-C-002",
            handoff_id=handoff.handoff_id,
            run_id=handoff.run_id,
            source_head=handoff.source_head,
            binding=forged_binding,
            _issuer=object(),
        )
        with self.assertRaisesRegex(ForkRefusal, "exact_prefix_witness_required"):
            controller.fork(handoff, forged_witness, forged_binding)

    def test_source_and_handoff_are_one_shot_and_immutable(self):
        receipts = clean_receipts()
        source = adapt_fixture_prefix_source("run", receipts)
        receipts[1]["payload"]["candidate_object"] = "changed-after-adaptation"
        runtime = RuntimePrefixMaterializer("run")
        handoff = runtime.materialize(source)
        self.assertEqual(handoff.artifact, expected_fixture_artifact())
        with self.assertRaises(HandoffRefusal):
            runtime.materialize(source)
        with self.assertRaises(TypeError):
            source.receipts[1]["payload"]["candidate_object"] = "mutation"

        controller = ForkController(runtime)
        witness = controller.witness(handoff)
        root = controller.fork(handoff, witness, witness.binding)
        self.assertIs(root.artifact, handoff.artifact)
        self.assertFalse(hasattr(root, "path"))
        with self.assertRaises(TypeError):
            root.artifact[0] = 0

    def test_forged_source_refuses(self):
        source = adapt_fixture_prefix_source("run", clean_receipts())
        forged = replace(source, _issuer=object())
        runtime = RuntimePrefixMaterializer("run")
        with self.assertRaisesRegex(PrefixSourceRefusal, "forged_fixture_prefix_source"):
            runtime.materialize(forged)


if __name__ == "__main__":
    unittest.main()
