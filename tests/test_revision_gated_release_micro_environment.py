from dataclasses import FrozenInstanceError, replace
from itertools import product
import ast
from pathlib import Path
import unittest

from micro_environment import (
    ACCEPTED,
    REBUILD_THEN_RELEASE,
    REJECTED,
    RELEASE,
    RELEASED,
    STALE_DEPENDENCY,
    RevisionResult,
    RevisionState,
    TransitionRefusal,
    apply_revision_gated_release,
)
from revision_micro_environment_oracle import (
    ConformanceRefusal,
    require_conforming,
)


DOMAIN = (0, 1, 2, 7, 8, 41, 42)
ACTIONS = (RELEASE, REBUILD_THEN_RELEASE)


def canonical_cases():
    return tuple(
        (RevisionState(artifact, authority), action)
        for artifact, authority, action in product(DOMAIN, DOMAIN, ACTIONS)
    )


def affine_order(cases, multiplier, offset):
    return tuple(cases[(multiplier * position + offset) % 98] for position in range(98))


def result_map(cases, engine=apply_revision_gated_release):
    results = {}
    for state, action in cases:
        result = engine(state, action)
        require_conforming(state, action, result)
        results[(state.artifact_revision, state.authority_revision, action)] = result
    return results


def action_only(state, action):
    accepted = action == REBUILD_THEN_RELEASE
    return RevisionResult(
        action,
        state.artifact_revision,
        state.authority_revision if accepted else state.artifact_revision,
        state.authority_revision,
        ACCEPTED if accepted else REJECTED,
        RELEASED if accepted else STALE_DEPENDENCY,
    )


def fixed_after_state(state, action):
    artifact_after = 8 if action == REBUILD_THEN_RELEASE else state.artifact_revision
    accepted = artifact_after == state.authority_revision
    return RevisionResult(
        action,
        state.artifact_revision,
        artifact_after,
        state.authority_revision,
        ACCEPTED if accepted else REJECTED,
        RELEASED if accepted else STALE_DEPENDENCY,
    )


class RevisionGatedReleaseTests(unittest.TestCase):
    def test_all_98_prospective_cases_in_three_frozen_orders(self):
        cases = canonical_cases()
        self.assertEqual(len(cases), 98)
        expected = result_map(cases)
        self.assertEqual(result_map(affine_order(cases, 37, 11)), expected)
        self.assertEqual(result_map(affine_order(cases, 55, 23)), expected)

    def test_release_depends_on_state(self):
        accepted = apply_revision_gated_release(RevisionState(8, 8), RELEASE)
        rejected = apply_revision_gated_release(RevisionState(7, 8), RELEASE)
        self.assertEqual((accepted.disposition, accepted.observation), (ACCEPTED, RELEASED))
        self.assertEqual(
            (rejected.disposition, rejected.observation),
            (REJECTED, STALE_DEPENDENCY),
        )

    def test_rebuild_after_state_tracks_authority(self):
        for authority in DOMAIN:
            result = apply_revision_gated_release(
                RevisionState(7, authority), REBUILD_THEN_RELEASE
            )
            self.assertEqual(result.artifact_revision_after, authority)
            self.assertEqual(result.disposition, ACCEPTED)

    def test_action_only_comparator_fails(self):
        failures = 0
        for state, action in canonical_cases():
            try:
                require_conforming(state, action, action_only(state, action))
            except ConformanceRefusal:
                failures += 1
        self.assertEqual(failures, 7)

    def test_fixed_after_state_comparator_fails(self):
        failures = 0
        for state, action in canonical_cases():
            try:
                require_conforming(state, action, fixed_after_state(state, action))
            except ConformanceRefusal:
                failures += 1
        self.assertEqual(failures, 42)

    def test_bad_actions_refuse(self):
        state = RevisionState(7, 8)
        for action in ("Release", None, 1, ""):
            with self.assertRaises(TransitionRefusal):
                apply_revision_gated_release(state, action)
        with self.assertRaises(TypeError):
            apply_revision_gated_release(state)

    def test_bad_state_shape_refuses(self):
        for state in (None, (7, 8), {"artifact_revision": 7, "authority_revision": 8}):
            with self.assertRaises(TransitionRefusal):
                apply_revision_gated_release(state, RELEASE)
        with self.assertRaises(TypeError):
            RevisionState(artifact_revision=7)
        with self.assertRaises(TypeError):
            RevisionState(7, 8, expected_disposition=ACCEPTED)

    def test_caller_result_fields_refuse(self):
        for field, value in (
            ("disposition", ACCEPTED),
            ("observation", RELEASED),
            ("artifact_revision_after", 8),
        ):
            with self.subTest(field=field):
                with self.assertRaises(TypeError):
                    RevisionState(7, 8, **{field: value})

    def test_non_integer_revisions_refuse_in_each_position(self):
        for bad in (True, "7", 7.0, None, [7]):
            with self.assertRaises(TransitionRefusal):
                RevisionState(bad, 8)
            with self.assertRaises(TransitionRefusal):
                RevisionState(7, bad)

    def test_input_is_immutable_and_unchanged(self):
        state = RevisionState(7, 8)
        before = (state.artifact_revision, state.authority_revision)
        apply_revision_gated_release(state, REBUILD_THEN_RELEASE)
        self.assertEqual((state.artifact_revision, state.authority_revision), before)
        with self.assertRaises(FrozenInstanceError):
            state.artifact_revision = 8

    def test_repeated_results_are_equal_but_distinct(self):
        state = RevisionState(7, 8)
        first = apply_revision_gated_release(state, RELEASE)
        second = apply_revision_gated_release(state, RELEASE)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)

    def test_different_actions_return_distinct_result_objects(self):
        state = RevisionState(7, 8)
        released = apply_revision_gated_release(state, RELEASE)
        rebuilt = apply_revision_gated_release(state, REBUILD_THEN_RELEASE)
        self.assertIsNot(released, rebuilt)

    def test_counterfeit_results_refuse(self):
        stale = RevisionState(7, 8)
        current = RevisionState(8, 8)
        valid_stale = apply_revision_gated_release(stale, RELEASE)
        counterfeits = (
            (stale, RELEASE, replace(valid_stale, artifact_revision_before=8)),
            (current, RELEASE, RevisionResult(RELEASE, 8, 8, 8, REJECTED, STALE_DEPENDENCY)),
            (stale, RELEASE, RevisionResult(RELEASE, 7, 7, 8, ACCEPTED, RELEASED)),
            (stale, RELEASE, replace(valid_stale, artifact_revision_after=8)),
            (
                stale,
                REBUILD_THEN_RELEASE,
                RevisionResult(
                    REBUILD_THEN_RELEASE,
                    7,
                    7,
                    8,
                    REJECTED,
                    STALE_DEPENDENCY,
                ),
            ),
            (stale, RELEASE, replace(valid_stale, observation=RELEASED)),
            (stale, RELEASE, replace(valid_stale, disposition=ACCEPTED)),
        )
        for state, action, result in counterfeits:
            with self.assertRaises(ConformanceRefusal):
                require_conforming(state, action, result)

    def test_order_dependent_diagnostic_fails(self):
        for order in (
            canonical_cases(),
            affine_order(canonical_cases(), 37, 11),
            affine_order(canonical_cases(), 55, 23),
        ):
            calls = 0
            failures = 0

            def alternating(state, action):
                nonlocal calls
                calls += 1
                chosen = RELEASE if calls % 2 else REBUILD_THEN_RELEASE
                return action_only(state, chosen)

            for state, action in order:
                try:
                    require_conforming(state, action, alternating(state, action))
                except ConformanceRefusal:
                    failures += 1
            self.assertGreater(failures, 0)

    def test_engine_has_no_formation_or_trajectory_dependency(self):
        package = Path(__file__).parents[1] / "micro_environment"
        imports = set()
        for path in package.glob("*.py"):
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
        self.assertLessEqual(imports, {"dataclasses", "micro_environment"})


if __name__ == "__main__":
    unittest.main()
