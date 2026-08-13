from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import unittest

from formation.condition_append import (
    ConditionHandoffRefusal,
    ConditionSourceRefusal,
    PublicConditionDelivery,
    CoordinateRefusal,
    RuntimeConditionRun,
    _adapt_condition_source,
    baseline_condition,
    treatment_condition,
)
from trajectory.fixture_condition import (
    AssignmentRefusal,
    BranchAssignment,
    ConditionAppendController,
    ConditionAppendRefusal,
    ConditionBinding,
    ConditionValidationRefusal,
    ConditionWitness,
    compute_condition_binding,
    validate_fixture_condition,
)
from trajectory.fixture_fork import ForkController, ForkRefusal
from test_fixture_prefix import clean_runtime


def clean_forks(run_id: str = "run-condition"):
    runtime, prefix_handoff = clean_runtime(run_id)
    forks = ForkController(runtime)
    prefix_witness = forks.witness(prefix_handoff)
    roots = [
        forks.fork(prefix_handoff, prefix_witness, prefix_witness.binding)
        for _ in range(3)
    ]
    forks.seal_roots()
    return runtime, prefix_handoff, forks, roots


def materialize_all(labels=("baseline", "governed", "ablation")):
    prefix_runtime, prefix_handoff, forks, roots = clean_forks()
    runtime_run = RuntimeConditionRun(roots[0].run_id, forks)
    runtimes = [runtime_run.materializer(root) for root in roots]
    controller = ConditionAppendController(forks)
    assignments = [controller.assign(root, label) for root, label in zip(roots, labels)]
    results = []
    for root, runtime, (assignment, delivery) in zip(roots, runtimes, assignments):
        source = controller.deliver(root, assignment, delivery)
        handoff = runtime.materialize(source)
        witness = controller.witness(runtime, handoff, assignment, delivery)
        local_root = controller.append(runtime, handoff, witness, root)
        results.append((assignment, delivery, runtime, handoff, witness, local_root))
    return prefix_runtime, prefix_handoff, forks, roots, controller, results


class FixtureConditionTests(unittest.TestCase):
    def test_clean_three_branch_append(self):
        prefix_runtime, prefix_handoff, _, roots, _, results = materialize_all()

        self.assertEqual([result[3].head_after for result in results], [
            "D-X-000001",
            "D-X-000002",
            "D-X-000003",
        ])
        self.assertTrue(all(root.artifact is prefix_handoff.artifact for root in roots))
        self.assertTrue(all(result[5].prefix_root is root for result, root in zip(results, roots)))
        self.assertTrue(all(result[5].condition_segment is result[3].artifact for result in results))

        decoded = [json.loads(result[3].artifact) for result in results]
        self.assertEqual(decoded[0]["payload"], {
            "condition": "audit_lineage_only-v0",
            "interpreter": None,
            "governor": None,
            "influence_policy": "declared-role-match-v0",
        })
        self.assertEqual(decoded[1]["payload"], decoded[2]["payload"])
        self.assertNotEqual(results[1][3].artifact, results[2][3].artifact)
        self.assertEqual(decoded[1]["parents"], ["D-C-006"])
        self.assertEqual(decoded[1]["order"], 7)
        self.assertFalse(any(label.encode() in result[3].artifact for label in ("baseline", "governed", "ablation") for result in results))
        self.assertEqual(prefix_handoff.artifact.count(b"\n"), 6)
        prefix_runtime.close()

    def test_document_templates_match_runtime_bytes(self):
        _, _, _, _, _, results = materialize_all()
        document = Path("docs/CONDITION_APPEND.md").read_text()
        blocks = document.split("```jsonl\n")[1:3]
        templates = [block.split("```", 1)[0].encode() for block in blocks]
        self.assertEqual(
            templates[0].replace(b"<opaque>", b"D-X-000001"),
            results[0][3].artifact,
        )
        self.assertEqual(
            templates[1].replace(b"<opaque>", b"D-X-000002"),
            results[1][3].artifact,
        )

    def test_roots_are_exact_sealed_once_only_capabilities(self):
        _, prefix_handoff, forks, roots = clean_forks()
        self.assertEqual(roots[0], roots[1])
        self.assertIsNot(roots[0], roots[1])
        with self.assertRaisesRegex(ForkRefusal, "exact_issued_root_required"):
            forks.require_issued_root(replace(roots[0]))
        with self.assertRaisesRegex(ForkRefusal, "fork_set_already_sealed"):
            forks.fork(prefix_handoff, object(), object())
        _, _, changed_forks, changed_roots = clean_forks("run-changed-root")
        object.__setattr__(
            changed_roots[2],
            "artifact",
            bytes(bytearray(changed_roots[2].artifact)),
        )
        with self.assertRaisesRegex(ForkRefusal, "issued_root_changed"):
            changed_forks.require_issued_root(changed_roots[2])

        RuntimeConditionRun(roots[0].run_id, forks)
        controller = ConditionAppendController(forks)
        assignment, delivery = controller.assign(roots[0], "baseline")
        controller.deliver(roots[0], assignment, delivery)
        with self.assertRaisesRegex(
            ForkRefusal, "assignment_controller_already_registered"
        ):
            ConditionAppendController(forks)

    def test_fork_set_must_be_complete_before_assignment(self):
        runtime, handoff = clean_runtime("run-incomplete")
        forks = ForkController(runtime)
        witness = forks.witness(handoff)
        root = forks.fork(handoff, witness, witness.binding)
        with self.assertRaisesRegex(ForkRefusal, "fixture_requires_three_roots"):
            forks.seal_roots()
        with self.assertRaisesRegex(ForkRefusal, "fork_set_not_sealed"):
            RuntimeConditionRun("run-incomplete", forks)

    def test_assignment_and_delivery_refuse_forgery_and_mismatch(self):
        _, _, forks, roots = clean_forks()
        RuntimeConditionRun(roots[0].run_id, forks)
        controller = ConditionAppendController(forks)
        assignment, delivery = controller.assign(roots[0], "baseline")

        with self.assertRaisesRegex(AssignmentRefusal, "exact_assignment_required"):
            controller.deliver(roots[0], replace(assignment), delivery)
        with self.assertRaisesRegex(AssignmentRefusal, "exact_public_delivery_required"):
            controller.deliver(roots[0], assignment, replace(delivery))
        with self.assertRaisesRegex(AssignmentRefusal, "exact_public_delivery_required"):
            controller.deliver(
                roots[0],
                assignment,
                PublicConditionDelivery(roots[0], treatment_condition(), object()),
            )
        with self.assertRaisesRegex(AssignmentRefusal, "unknown_fixture_branch_label"):
            controller.assign(roots[1], "unknown")
        with self.assertRaisesRegex(AssignmentRefusal, "root_already_assigned"):
            controller.assign(roots[0], "governed")

    def test_label_bearing_run_id_refuses_before_delivery(self):
        for run_id in (
            "run-baseline-hidden",
            "runbaselinehidden",
            "run-governed",
            "runablationhidden",
            "run-B",
            "G-run",
            "run-A-1",
        ):
            with self.subTest(run_id=run_id):
                _, _, forks, _ = clean_forks(run_id)
                with self.assertRaisesRegex(
                    ConditionSourceRefusal, "label_bearing_run_id"
                ):
                    RuntimeConditionRun(run_id, forks)

    def test_coordinates_are_reserved_before_assignment_without_harness_issuer(self):
        _, _, forks, roots = clean_forks("run-reserved")
        runtime_run = RuntimeConditionRun("run-reserved", forks)
        runtimes = [runtime_run.materializer(root) for root in roots]
        controller = ConditionAppendController(forks)
        self.assertFalse(hasattr(controller, "allocator"))
        self.assertFalse(hasattr(controller, "_allocator"))
        self.assertFalse(hasattr(runtime_run, "issue"))
        with self.assertRaisesRegex(
            CoordinateRefusal, "runtime_root_materializer_already_opened"
        ):
            runtime_run.materializer(roots[0])
        self.assertEqual([runtime._coordinate for runtime in runtimes], [
            "D-X-000001",
            "D-X-000002",
            "D-X-000003",
        ])

    def test_fake_or_permuting_fork_boundary_cannot_reserve_coordinates(self):
        _, _, forks, roots = clean_forks("run-fake-boundary")

        class FakeForkBoundary:
            def claim_runtime_roots(self):
                return tuple(reversed(roots))

        with self.assertRaisesRegex(CoordinateRefusal, "exact_fork_boundary_required"):
            RuntimeConditionRun("run-fake-boundary", FakeForkBoundary())

        runtime_run = RuntimeConditionRun("run-fake-boundary", forks)
        self.assertEqual(
            [runtime_run.materializer(root)._coordinate for root in roots],
            ["D-X-000001", "D-X-000002", "D-X-000003"],
        )

    def test_reserved_coordinate_and_root_cannot_change(self):
        _, _, forks, roots = clean_forks("run-reservation-mutation")
        runtime_run = RuntimeConditionRun("run-reservation-mutation", forks)
        runtimes = [runtime_run.materializer(root) for root in roots]
        controller = ConditionAppendController(forks)
        assignments = [
            controller.assign(root, label)
            for root, label in zip(roots, ("baseline", "governed", "ablation"))
        ]

        source = controller.deliver(roots[0], *assignments[0])
        runtimes[0]._coordinate = "D-X-999999"
        with self.assertRaisesRegex(
            CoordinateRefusal, "runtime_coordinate_reservation_changed"
        ):
            runtimes[0].materialize(source)

        source_2 = controller.deliver(roots[1], *assignments[1])
        runtimes[1]._root = roots[2]
        with self.assertRaisesRegex(
            CoordinateRefusal, "runtime_coordinate_reservation_changed"
        ):
            runtimes[1].materialize(source_2)

        first = materialize_all(("baseline", "governed", "ablation"))[5]
        second = materialize_all(("ablation", "baseline", "governed"))[5]
        self.assertEqual(
            [result[3].head_after for result in first],
            [result[3].head_after for result in second],
        )

    def test_validator_refuses_independent_byte_mutations(self):
        _, _, _, _, _, results = materialize_all()
        handoff = results[0][3]
        condition = results[0][1].condition
        clean = handoff.artifact
        mutations = {
            "branch_coordinate": clean.replace(b"D-X-000001", b"D-B-000001"),
            "wrong_parent": clean.replace(b"D-C-006", b"D-C-005"),
            "wrong_order": clean.replace(b'"order":7', b'"order":8'),
            "branch_label": clean.replace(b'"record"', b'"branch":"baseline","record"'),
            "expected": clean.replace(b'"record"', b'"expected":"pass","record"'),
            "scorer": clean.replace(b'"record"', b'"scorer":"pass","record"'),
            "ablation": clean.replace(b'"record"', b'"ablation":"causal_probe","record"'),
            "key_order": clean.replace(b'{"contract":"fixture-v0","coordinate"', b'{"coordinate":"D-X-000001","contract"').replace(b'"D-X-000001","record"', b'"fixture-v0","record"', 1),
            "whitespace": clean.replace(b'"record"', b' "record"'),
            "crlf": clean.replace(b"\n", b"\r\n"),
            "missing_lf": clean[:-1],
            "extra_line": clean + clean,
        }
        for name, artifact in mutations.items():
            with self.subTest(name=name), self.assertRaisesRegex(
                ConditionValidationRefusal, "invalid_fixture_condition_bytes"
            ):
                validate_fixture_condition(artifact, handoff.head_after, condition)

    def test_raw_forged_handoff_witness_and_post_binding_tamper_refuse(self):
        _, _, forks, roots = clean_forks()
        runtime_run = RuntimeConditionRun(roots[0].run_id, forks)
        controller = ConditionAppendController(forks)
        assignment, delivery = controller.assign(roots[0], "baseline")
        source = controller.deliver(roots[0], assignment, delivery)
        runtime = runtime_run.materializer(roots[0])
        with self.assertRaisesRegex(ConditionSourceRefusal, "exact_condition_source_required"):
            runtime.materialize({"condition": baseline_condition()})
        handoff = runtime.materialize(source)
        witness = controller.witness(runtime, handoff, assignment, delivery)

        with self.assertRaisesRegex(ConditionAppendRefusal, "exact_condition_witness_required"):
            forged_witness = ConditionWitness(
                witness.assignment_coordinate,
                witness.prefix_witness_coordinate,
                witness.handoff_id,
                witness.run_id,
                witness.head_after,
                witness.binding,
                object(),
            )
            controller.append(runtime, handoff, forged_witness, roots[0])

        with self.assertRaisesRegex(ConditionHandoffRefusal, "stale_or_forged"):
            controller.append(runtime, replace(handoff), witness, roots[0])
        with self.assertRaisesRegex(ConditionAppendRefusal, "exact_condition_witness_required"):
            controller.append(runtime, handoff, replace(witness), roots[0])

        object.__setattr__(handoff, "artifact", handoff.artifact.replace(b"audit", b"alter", 1))
        with self.assertRaisesRegex(ConditionAppendRefusal, "condition_binding_mismatch"):
            controller.append(runtime, handoff, witness, roots[0])

    def test_witness_requires_delivery_and_append_returns_once(self):
        _, _, forks, roots = clean_forks()
        runtime_run = RuntimeConditionRun(roots[0].run_id, forks)
        controller = ConditionAppendController(forks)
        assignment, delivery = controller.assign(roots[0], "baseline")
        runtime = runtime_run.materializer(roots[0])
        bypass_source = _adapt_condition_source(
            roots[0].run_id, roots[0], delivery
        )
        with self.assertRaisesRegex(
            ConditionSourceRefusal, "exact_condition_source_required"
        ):
            runtime.materialize(replace(bypass_source))
        handoff = runtime.materialize(bypass_source)
        with self.assertRaisesRegex(
            CoordinateRefusal, "runtime_root_materializer_already_opened"
        ):
            runtime_run.materializer(roots[0])
        with self.assertRaisesRegex(
            ConditionSourceRefusal, "public_delivery_already_consumed"
        ):
            _adapt_condition_source(
                roots[0].run_id, roots[0], delivery
            )
        with self.assertRaisesRegex(AssignmentRefusal, "public_condition_not_delivered"):
            controller.witness(runtime, handoff, assignment, delivery)

        _, _, forks_2, roots_2 = clean_forks("run-return-once")
        runtime_run_2 = RuntimeConditionRun(roots_2[0].run_id, forks_2)
        controller_2 = ConditionAppendController(forks_2)
        assignment_2, delivery_2 = controller_2.assign(roots_2[0], "baseline")
        source_2 = controller_2.deliver(roots_2[0], assignment_2, delivery_2)
        runtime_2 = runtime_run_2.materializer(roots_2[0])
        handoff_2 = runtime_2.materialize(source_2)
        witness_2 = controller_2.witness(
            runtime_2, handoff_2, assignment_2, delivery_2
        )
        controller_2.append(runtime_2, handoff_2, witness_2, roots_2[0])
        with self.assertRaisesRegex(
            ConditionAppendRefusal, "condition_root_already_returned"
        ):
            controller_2.append(runtime_2, handoff_2, witness_2, roots_2[0])

    def test_returned_root_is_exact_and_unchanged(self):
        _, _, _, _, controller, results = materialize_all()
        local_root = results[0][5]
        self.assertIs(controller.require_returned_root(local_root), local_root)
        with self.assertRaisesRegex(
            ConditionAppendRefusal, "exact_branch_local_root_required"
        ):
            controller.require_returned_root(replace(local_root))
        object.__setattr__(
            local_root,
            "condition_segment",
            bytes(bytearray(local_root.condition_segment)),
        )
        with self.assertRaisesRegex(
            ConditionAppendRefusal, "branch_local_root_changed"
        ):
            controller.require_returned_root(local_root)

    def test_binding_forms_and_wrong_root_refuse(self):
        _, _, forks, roots = clean_forks()
        runtime_run = RuntimeConditionRun(roots[0].run_id, forks)
        controller = ConditionAppendController(forks)
        assignments = [controller.assign(root, label) for root, label in zip(roots, ("baseline", "governed", "ablation"))]
        assignment, delivery = assignments[0]
        source = controller.deliver(roots[0], assignment, delivery)
        runtime = runtime_run.materializer(roots[0])
        handoff = runtime.materialize(source)
        witness = controller.witness(runtime, handoff, assignment, delivery)

        with self.assertRaisesRegex(ConditionAppendRefusal, "condition_witness_handoff_mismatch"):
            controller.append(runtime, handoff, witness, roots[1])

        for changed in (
            replace(witness.binding, materializer="unknown"),
            replace(witness.binding, identity_contract="unknown"),
            replace(witness.binding, algorithm="sha-512"),
            replace(witness.binding, digest=witness.binding.digest.upper()),
            replace(witness.binding, byte_length=True),
        ):
            with self.subTest(binding=changed), self.assertRaises(
                ConditionAppendRefusal
            ):
                changed.require_valid()

        original_binding = witness.binding
        object.__setattr__(witness, "binding", replace(original_binding, digest="0" * 64))
        with self.assertRaisesRegex(ConditionAppendRefusal, "condition_witness_changed"):
            controller.append(runtime, handoff, witness, roots[0])
        object.__setattr__(witness, "binding", original_binding)

    def test_condition_fields_are_source_derived_or_refuse(self):
        clean = baseline_condition()
        changes = (
            replace(clean, condition="unknown"),
            replace(clean, interpreter="revision-check-candidate-v0"),
            replace(clean, governor="consequence-warrant-v0"),
            replace(clean, influence_policy="unknown"),
        )
        for condition in changes:
            with self.subTest(condition=condition), self.assertRaises(ConditionSourceRefusal):
                condition.require_valid()


if __name__ == "__main__":
    unittest.main()
