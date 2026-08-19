from dataclasses import FrozenInstanceError, fields
import ast
import inspect
import itertools
import json
import unittest

import micro_environment.unselected_lineage_behavior as environment_module
from micro_environment.unselected_lineage_behavior import (
    APPLIED,
    DECREASED,
    FIRST_INCREASES,
    HELD,
    HOLD,
    INCREASED,
    NOT_APPLIED,
    REFUSED,
    SECOND_INCREASES,
    LineageActionResult,
    LineageBehaviorRefusal,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import (
    ABLATION,
    ACQUISITION_USE,
    ACTION_RESPONSIBILITY,
    ALREADY_CURRENT,
    BRANCHES,
    COPY_CONTROL,
    NO_PERSISTENCE,
    RAW_PERSISTENCE,
    RESULT_EXPOSED,
    RESULT_WITHHELD,
    ROLES,
    STATIC_INSTRUCTION,
    TRANSFER,
    WITHHELD_SENTINEL,
    BehaviorCase,
    IntermediateReceipt,
    LaterObservation,
    UnselectedSpecimenRefusal,
    authorship_material,
    branch_foregrounds,
    canonical_json_bytes,
    complete_observations,
    expected_coordinates,
    exposed_result,
    later_request,
    make_block,
    oracle_action,
    public_state,
    raw_foreground,
    score_observations,
    shared_occurrence,
    specimen_blocks,
    static_lesson,
    validate_fixture,
)


class UnselectedLineageBehaviorTests(unittest.TestCase):
    def test_environment_total_proposal_states_and_immutability(self):
        profile = LineageProfile("family", FIRST_INCREASES)
        state = LineageState("family", "device", 0, 1, ("left", "right"))

        unavailable = apply_committed_action(state, profile, ProposalReceipt(False, ""))
        empty = apply_committed_action(state, profile, ProposalReceipt(True, ""))
        foreign = apply_committed_action(state, profile, ProposalReceipt(True, "foreign"))
        held = apply_committed_action(state, profile, ProposalReceipt(True, HOLD))
        moved = apply_committed_action(state, profile, ProposalReceipt(True, "left"))

        self.assertEqual(unavailable.status, NOT_APPLIED)
        self.assertEqual(unavailable.reason, "proposal_unavailable")
        self.assertEqual(empty.status, REFUSED)
        self.assertEqual(foreign.status, REFUSED)
        self.assertEqual(held.status, HELD)
        self.assertEqual(moved.status, APPLIED)
        self.assertEqual(moved.movement_direction, INCREASED)
        self.assertEqual(state.position, 0)
        with self.assertRaises(FrozenInstanceError):
            state.position = 5

        with self.assertRaisesRegex(
            LineageBehaviorRefusal, "unavailable_proposal_must_be_empty"
        ):
            ProposalReceipt(False, "foreign")

    def test_environment_exhausts_profiles_directions_and_permitted_actions(self):
        for increasing_slot, direction in itertools.product(
            (FIRST_INCREASES, SECOND_INCREASES), (-1, 1)
        ):
            block = make_block(0, increasing_slot, direction)
            state = block.acquisition
            expected = oracle_action(state, block.profile)
            self.assertIn(expected, state.controls)
            for action in (*state.controls, HOLD):
                result = apply_committed_action(
                    state, block.profile, ProposalReceipt(True, action)
                )
                self.assertIn(result.status, (APPLIED, HELD))
                if action == expected:
                    self.assertTrue(result.target_reached)
                elif action in state.controls:
                    self.assertFalse(result.target_reached)
                    wanted_direction = INCREASED if direction > 0 else DECREASED
                    self.assertNotEqual(result.movement_direction, wanted_direction)

    def test_environment_types_and_fields_exclude_experimental_authority(self):
        self.assertEqual(
            {field.name for field in fields(LineageActionResult)},
            {
                "status",
                "proposal",
                "before",
                "selected_slot",
                "position_after",
                "movement_direction",
                "target_reached",
                "reason",
            },
        )
        source = inspect.getsource(environment_module)
        tree = ast.parse(source)
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        self.assertEqual(imports, {"dataclasses"})
        forbidden = (
            "branch",
            "intermediate",
            "lesson",
            "scorer",
            "expected_action",
            "oracle_action",
        )
        self.assertTrue(all(word not in source for word in forbidden))

    def test_fixture_is_fresh_unique_and_fully_counterbalanced(self):
        blocks = specimen_blocks()
        validate_fixture(blocks)
        self.assertEqual(len(blocks), 4)
        self.assertEqual(
            {
                (
                    block.profile.increasing_slot,
                    1 if block.acquisition.target > block.acquisition.position else -1,
                )
                for block in blocks
            },
            {
                (FIRST_INCREASES, 1),
                (SECOND_INCREASES, 1),
                (FIRST_INCREASES, -1),
                (SECOND_INCREASES, -1),
            },
        )
        identifiers = []
        for block in blocks:
            for state in (block.acquisition, *(case.state for case in block.cases)):
                identifiers.extend((state.device, *state.controls))
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_roles_are_frozen_from_oracle_geometry(self):
        for block in specimen_blocks():
            by_role = {case.role: case for case in block.cases}
            acquisition_action = oracle_action(block.acquisition, block.profile)
            acquisition_slot = block.acquisition.controls.index(acquisition_action)
            use = by_role[ACQUISITION_USE]
            transfer = by_role[TRANSFER]
            self.assertEqual(
                1 if use.state.target > use.state.position else -1,
                1 if block.acquisition.target > block.acquisition.position else -1,
            )
            self.assertNotEqual(
                transfer.state.controls.index(oracle_action(transfer.state, block.profile)),
                acquisition_slot,
            )
            self.assertEqual(
                oracle_action(by_role[ALREADY_CURRENT].state, block.profile), HOLD
            )

            frozen_roles = tuple(case.role for case in block.cases)
            for proposal in (
                ProposalReceipt(False, ""),
                ProposalReceipt(True, ""),
                ProposalReceipt(True, "foreign"),
                ProposalReceipt(True, HOLD),
                ProposalReceipt(True, block.acquisition.controls[0]),
                ProposalReceipt(True, block.acquisition.controls[1]),
            ):
                apply_committed_action(block.acquisition, block.profile, proposal)
                self.assertEqual(tuple(case.role for case in block.cases), frozen_roles)

    def test_occurrence_is_pre_result_and_result_projection_is_separate(self):
        block = specimen_blocks()[0]
        proposal = ProposalReceipt(True, block.acquisition.controls[0])
        result = apply_committed_action(block.acquisition, block.profile, proposal)
        occurrence = shared_occurrence(block.acquisition, proposal)
        serialized = canonical_json_bytes(occurrence).decode("utf-8")
        for forbidden in (
            "application_status",
            "selected_slot",
            "position_after",
            "movement_direction",
            "target_reached",
            "reason",
            "correct",
            "profile",
        ):
            self.assertNotIn(forbidden, serialized)
        exposed = authorship_material(
            block.acquisition, proposal, result, expose_result=True
        )
        withheld = authorship_material(
            block.acquisition, proposal, result, expose_result=False
        )
        self.assertEqual(exposed["occurrence"], withheld["occurrence"])
        self.assertEqual(withheld["external_result"], WITHHELD_SENTINEL)
        self.assertEqual(exposed["external_result"], exposed_result(result))

    def test_unavailable_acquisition_has_total_occurrence_and_result(self):
        block = specimen_blocks()[0]
        proposal = ProposalReceipt(False, "")
        result = apply_committed_action(block.acquisition, block.profile, proposal)
        occurrence = shared_occurrence(block.acquisition, proposal)
        self.assertEqual(
            occurrence["committed_proposal"], {"available": False, "content": ""}
        )
        self.assertEqual(
            exposed_result(result),
            {"application_status": NOT_APPLIED, "reason": "proposal_unavailable"},
        )
        exposed = authorship_material(
            block.acquisition, proposal, result, expose_result=True
        )
        withheld = authorship_material(
            block.acquisition, proposal, result, expose_result=False
        )
        self.assertEqual(exposed["occurrence"], withheld["occurrence"])

    def test_raw_and_static_foregrounds_preserve_authorship_boundaries(self):
        block = specimen_blocks()[0]
        proposal = ProposalReceipt(True, oracle_action(block.acquisition, block.profile))
        result = apply_committed_action(block.acquisition, block.profile, proposal)
        raw = json.loads(raw_foreground(block.acquisition, proposal, result))
        self.assertEqual(set(raw), {"external_result", "occurrence"})
        raw_text = canonical_json_bytes(raw).decode("utf-8")
        self.assertNotIn("increasing_slot", raw_text)
        lesson = static_lesson(block)
        self.assertIn(block.profile.controller_family, lesson)
        self.assertNotIn(block.acquisition.device, lesson)
        self.assertTrue(all(control not in lesson for control in block.acquisition.controls))
        for case in block.cases:
            for token in (case.state.device, *case.state.controls):
                self.assertNotIn(token, raw_text)
                self.assertNotIn(token, lesson)

    def test_six_paths_and_exact_exposed_ablation_identity(self):
        block = specimen_blocks()[0]
        proposal = ProposalReceipt(True, oracle_action(block.acquisition, block.profile))
        result = apply_committed_action(block.acquisition, block.profile, proposal)
        withheld = IntermediateReceipt(True, "withheld guidance")
        exposed = IntermediateReceipt(True, "exposed guidance")
        foregrounds = {
            row.branch: row
            for row in branch_foregrounds(block, proposal, result, withheld, exposed)
        }
        self.assertEqual(tuple(foregrounds), BRANCHES)
        self.assertEqual(foregrounds[NO_PERSISTENCE].delivered, "")
        self.assertEqual(
            foregrounds[RAW_PERSISTENCE].delivered,
            raw_foreground(block.acquisition, proposal, result),
        )
        self.assertEqual(foregrounds[RESULT_WITHHELD].delivered, withheld.content)
        self.assertEqual(foregrounds[RESULT_EXPOSED].delivered, exposed.content)
        self.assertEqual(foregrounds[ABLATION].delivered, "")
        self.assertEqual(
            foregrounds[STATIC_INSTRUCTION].delivered, static_lesson(block)
        )
        self.assertIsNone(foregrounds[NO_PERSISTENCE].retained_intermediate)
        self.assertIsNone(foregrounds[RAW_PERSISTENCE].retained_intermediate)
        self.assertIsNone(foregrounds[STATIC_INSTRUCTION].retained_intermediate)
        self.assertIs(foregrounds[RESULT_WITHHELD].retained_intermediate, withheld)
        self.assertIs(foregrounds[RESULT_EXPOSED].retained_intermediate, exposed)
        self.assertIs(foregrounds[ABLATION].retained_intermediate, exposed)
        self.assertEqual(
            later_request(block.cases[0], foregrounds[NO_PERSISTENCE].delivered),
            later_request(block.cases[0], foregrounds[ABLATION].delivered),
        )

        unavailable = IntermediateReceipt(False, "")
        unavailable_rows = {
            row.branch: row
            for row in branch_foregrounds(
                block, proposal, result, unavailable, unavailable
            )
        }
        self.assertEqual(unavailable_rows[RESULT_WITHHELD].delivered, "")
        self.assertEqual(unavailable_rows[RESULT_EXPOSED].delivered, "")
        self.assertIs(
            unavailable_rows[RESULT_WITHHELD].retained_intermediate, unavailable
        )
        self.assertIs(
            unavailable_rows[RESULT_EXPOSED].retained_intermediate, unavailable
        )
        self.assertIs(unavailable_rows[ABLATION].retained_intermediate, unavailable)

    def test_later_request_is_common_and_excludes_hidden_labels(self):
        block = specimen_blocks()[0]
        for case in block.cases:
            request = json.loads(later_request(case, "arbitrary material"))
            self.assertEqual(
                set(request), {"device", "responsibility", "retained_material"}
            )
            self.assertEqual(request["responsibility"], ACTION_RESPONSIBILITY)
            serialized = canonical_json_bytes(request).decode("utf-8")
            self.assertNotIn(case.role, serialized)
            self.assertTrue(all(branch not in serialized for branch in BRANCHES))
            self.assertNotIn("increasing_slot", serialized)

    def test_copy_control_is_precontact_and_live_collision_is_report_only(self):
        block = specimen_blocks()[0]
        copy_case = next(case for case in block.cases if case.role == COPY_CONTROL)
        copy_action = oracle_action(copy_case.state, block.profile)
        proposal = ProposalReceipt(True, oracle_action(block.acquisition, block.profile))
        result = apply_committed_action(block.acquisition, block.profile, proposal)
        exposed = IntermediateReceipt(True, copy_action)
        rows = branch_foregrounds(
            block,
            proposal,
            result,
            IntermediateReceipt(True, "other"),
            exposed,
        )
        self.assertEqual(copy_case.role, COPY_CONTROL)
        self.assertEqual(
            next(row for row in rows if row.branch == RESULT_EXPOSED).delivered,
            copy_action,
        )
        validate_fixture(specimen_blocks())

    def test_complete_scorer_has_all_branch_role_denominators_and_strata(self):
        blocks = specimen_blocks()
        acquisition_results, observations = complete_observations(blocks, "oracle")
        report = score_observations(blocks, acquisition_results, observations)
        self.assertEqual(report["assigned"], 4 * len(BRANCHES) * len(ROLES))
        self.assertNotIn("formation_verdict", report)
        self.assertNotIn("validation_verdict", report)
        for branch in BRANCHES:
            self.assertEqual(set(report["branches"][branch]), set(ROLES))
            for role in ROLES:
                cell = report["branches"][branch][role]
                self.assertEqual(cell["assigned"], 4)
                self.assertEqual(cell["correct_action"], 4)
                self.assertEqual(cell["invalid_or_unavailable"], 0)
                self.assertEqual(sum(cell["acquisition_status"].values()), 4)

        unavailable_acquisition = {
            block.coordinate: apply_committed_action(
                block.acquisition, block.profile, ProposalReceipt(False, "")
            )
            for block in blocks
        }
        unavailable_report = score_observations(
            blocks, unavailable_acquisition, observations
        )
        for branch in BRANCHES:
            for role in ROLES:
                self.assertEqual(
                    unavailable_report["branches"][branch][role]["acquisition_status"],
                    {NOT_APPLIED: 4},
                )

    def test_scorer_retains_invalid_and_unavailable_later_actions(self):
        blocks = specimen_blocks()
        for mode in ("invalid", "unavailable"):
            acquisition_results, observations = complete_observations(blocks, mode)
            report = score_observations(blocks, acquisition_results, observations)
            for branch in BRANCHES:
                for role in ROLES:
                    cell = report["branches"][branch][role]
                    self.assertEqual(cell["assigned"], 4)
                    self.assertEqual(cell["correct_action"], 0)
                    self.assertEqual(cell["invalid_or_unavailable"], 4)

    def test_scorer_refuses_missing_duplicate_extra_and_lineage_mismatch(self):
        blocks = specimen_blocks()
        acquisition_results, observations = complete_observations(blocks)
        with self.assertRaisesRegex(UnselectedSpecimenRefusal, "missing_later_observation"):
            score_observations(blocks, acquisition_results, observations[:-1])
        with self.assertRaisesRegex(UnselectedSpecimenRefusal, "duplicate_later_observation"):
            score_observations(blocks, acquisition_results, (*observations, observations[0]))

        first = observations[0]
        with self.assertRaisesRegex(UnselectedSpecimenRefusal, "unknown_observation_branch"):
            LaterObservation(
                first.block,
                "unknown_branch",
                first.case,
                first.role,
                first.proposal,
                first.result,
            )

        extra = LaterObservation(
            first.block,
            first.branch,
            "unknown-case",
            first.role,
            first.proposal,
            first.result,
        )
        with self.assertRaisesRegex(UnselectedSpecimenRefusal, "unexpected_later_observation"):
            score_observations(blocks, acquisition_results, (extra, *observations[1:]))

        wrong_case = blocks[0].cases[1]
        mismatch = LaterObservation(
            first.block,
            first.branch,
            first.case,
            first.role,
            first.proposal,
            apply_committed_action(wrong_case.state, blocks[0].profile, first.proposal),
        )
        with self.assertRaisesRegex(UnselectedSpecimenRefusal, "later_result_lineage_mismatch"):
            score_observations(blocks, acquisition_results, (mismatch, *observations[1:]))

        impossible = LineageActionResult(
            status=first.result.status,
            proposal=first.proposal,
            before=first.result.before,
            selected_slot=first.result.selected_slot,
            position_after=999,
            movement_direction=first.result.movement_direction,
            target_reached=first.result.target_reached,
            reason=first.result.reason,
        )
        impossible_observation = LaterObservation(
            first.block,
            first.branch,
            first.case,
            first.role,
            first.proposal,
            impossible,
        )
        with self.assertRaisesRegex(UnselectedSpecimenRefusal, "later_result_physics_mismatch"):
            score_observations(
                blocks, acquisition_results, (impossible_observation, *observations[1:])
            )

        with self.assertRaisesRegex(
            UnselectedSpecimenRefusal, "exact_observation_proposal_required"
        ):
            LaterObservation(
                first.block,
                first.branch,
                first.case,
                first.role,
                object(),
                first.result,
            )


if __name__ == "__main__":
    unittest.main()
