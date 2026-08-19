import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from contact.exploratory_developmental_contact import (
    InvocationFailure,
    ProviderAttempt,
)
from contact.phase_coupled_exploratory_contact import (
    ACTOR_SETTINGS,
    COMMITMENT_CASES,
    COMMITMENT_OFFERS,
    INTERFACE_STATE,
    MODEL,
    MODEL_DIGEST,
    PHYSICAL_CALL_CEILING,
    PLANNED_LOGICAL_CALLS,
    PROBE_CASES,
    PROBE_OFFERS,
    TOKEN_DELTA_CEILING,
    WORLD_A,
    WORLD_B,
    CandidateParse,
    LogicalCall,
    actor_envelope,
    content_ablation,
    govern_candidate,
    later_schedule,
    lexical_diagnostic,
    main,
    offer_material,
    parse_actions,
    parse_candidate,
    run_contact,
)
from micro_environment.phase_coupled_specimen import acquisition_occurrence


def provider_attempt(call, attempt_index, content, prompt_tokens=100):
    envelope = {
        "choices": [{"message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": 8},
    }
    body = json.dumps(envelope, sort_keys=True).encode("utf-8")
    return ProviderAttempt(
        call.logical_index,
        attempt_index,
        call.call_id,
        call.request_body,
        body,
        envelope,
        envelope["choices"][0]["message"],
        content,
        200,
        "start",
        "end",
        0.01,
    )


class FakeInvoker:
    def __init__(
        self,
        malformed_interpreter=False,
        invalid_acquisition=False,
        large_content_delta=False,
        retry_first=False,
    ):
        self.calls = []
        self.malformed_interpreter = malformed_interpreter
        self.invalid_acquisition = invalid_acquisition
        self.large_content_delta = large_content_delta
        self.retry_first = retry_first

    def __call__(self, call, attempt_index):
        self.calls.append((call, attempt_index))
        if self.retry_first and len(self.calls) == 1:
            attempt = ProviderAttempt(
                call.logical_index,
                attempt_index,
                call.call_id,
                call.request_body,
                b"",
                {"transport_error": "fake"},
                None,
                None,
                None,
                "start",
                "end",
                0.01,
                "transport_failure",
            )
            raise InvocationFailure("transport_failure", attempt, True)
        if call.responsibility == "interpreter":
            content = (
                "not-json"
                if self.malformed_interpreter
                else json.dumps(
                    {
                        "change": "Use the observed family phase profile.",
                        "counterevidence": "A later same-family movement contradicts it.",
                    }
                )
            )
        elif self.invalid_acquisition and call.call_id == "world-a-acquisition":
            content = '{"actions":["not-listed"]}'
        else:
            if call.commitment and call.probe_id is None:
                actions = call.state.controls
            elif call.commitment:
                actions = (call.state.controls[0], call.state.controls[0])
            else:
                actions = ("hold",)
            content = json.dumps({"actions": list(actions)})
        prompt_tokens = (
            140
            if self.large_content_delta and call.offer_key == "content_ablation"
            else 100
        )
        return provider_attempt(call, attempt_index, content, prompt_tokens)


def admitted_materials():
    result = {}
    for world in (WORLD_A, WORLD_B):
        occurrence = acquisition_occurrence(
            world.acquisition, world.acquisition_profile, world.acquisition.controls
        )
        candidate = {
            "change": "Use the observed family phase profile.",
            "counterevidence": "A contradiction should count against it.",
        }
        governance = {
            "admitted": True,
            "refusals": [],
            "candidate": candidate,
        }
        result[world.world_id] = {
            "occurrence": occurrence,
            "governance": governance,
            "source_family": world.acquisition.controller_family,
        }
    return result


class PhaseCoupledExploratoryContactTests(unittest.TestCase):
    def test_model_budget_settings_and_case_counts_are_frozen(self):
        self.assertEqual(MODEL, "ai/qwen3:14B-Q6_K")
        self.assertEqual(
            MODEL_DIGEST,
            "sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219",
        )
        self.assertEqual((PLANNED_LOGICAL_CALLS, PHYSICAL_CALL_CEILING), (69, 72))
        self.assertEqual(TOKEN_DELTA_CEILING, 24)
        self.assertEqual(ACTOR_SETTINGS["response_format"], {"type": "json_object"})
        self.assertEqual((len(COMMITMENT_CASES), len(PROBE_CASES)), (8, 4))

    def test_commitment_cases_exhaust_profiles_phases_directions_and_unique_pairs(self):
        seen = set()
        for case in COMMITMENT_CASES:
            world = WORLD_A if case.world_id == "world-a" else WORLD_B
            phase_index = world.acquisition_profile.phases.index(case.state.phase)
            direction = 1 if case.state.target > case.state.position else -1
            seen.add((case.world_id, phase_index, direction))
            self.assertEqual(abs(case.state.target - case.state.position), 2)
            self.assertNotEqual(case.expected_actions[0], case.expected_actions[1])
        self.assertEqual(len(seen), 8)

    def test_all_twelve_later_cases_match_frozen_charter_literals(self):
        expected = {
            "a-p0-up": ("418e2788910b4d0d", "5daafeba44700e4a", "48ec89c0bb579d0a", 10, 12, ("f2436f5682e9fa1a", "1630d33cf00b85a0"), ("f2436f5682e9fa1a", "1630d33cf00b85a0")),
            "a-p0-down": ("418e2788910b4d0d", "0283d37fb2f261f8", "48ec89c0bb579d0a", 10, 8, ("6f3cd77e3eda3722", "78025e8f696c5986"), ("78025e8f696c5986", "6f3cd77e3eda3722")),
            "a-p1-up": ("418e2788910b4d0d", "bf25d7ad05fa3966", "713562aa1a463b44", 20, 22, ("13eed001c1ff06a6", "2341a53aaa5fcf49"), ("2341a53aaa5fcf49", "13eed001c1ff06a6")),
            "a-p1-down": ("418e2788910b4d0d", "6a29c326c8338238", "713562aa1a463b44", 20, 18, ("2fc0146f35188936", "a3e2fdaef0816f8c"), ("2fc0146f35188936", "a3e2fdaef0816f8c")),
            "b-p0-up": ("cabd05ee74f6137f", "18f73d6d1e3d7ff9", "a7fdcdee8ffb8e83", 30, 32, ("36fe253f69414cdb", "933157db26a0398a"), ("933157db26a0398a", "36fe253f69414cdb")),
            "b-p0-down": ("cabd05ee74f6137f", "379d52df2a8c40a5", "a7fdcdee8ffb8e83", 30, 28, ("e4ee5c8c37e6b8cc", "fc216678eb3e1ce0"), ("e4ee5c8c37e6b8cc", "fc216678eb3e1ce0")),
            "b-p1-up": ("cabd05ee74f6137f", "1c4dc1793123bb3a", "e4827a8649c41e3f", 40, 42, ("77d0684a164f6e33", "4b732ad67a9d8698"), ("77d0684a164f6e33", "4b732ad67a9d8698")),
            "b-p1-down": ("cabd05ee74f6137f", "125569c2598f087c", "e4827a8649c41e3f", 40, 38, ("c91e1a0e760ddb08", "45f7fc5cc2047071"), ("45f7fc5cc2047071", "c91e1a0e760ddb08")),
            "a-other": ("38e53c39643e5d39", "7c459798a90ec52d", "c59dba393c6b9ab5", 4, 5, ("94fd8e79c52d9b28", "9bae416d06fdc594"), ("hold",)),
            "b-other": ("d61fdcf3cb2327db", "0926df441abbc04b", "fe07ba41b4f75840", 9, 8, ("50ecfb1b91c64226", "6ee06644c42e68e0"), ("hold",)),
            "a-current": ("418e2788910b4d0d", "abf06a862f8580e1", "48ec89c0bb579d0a", 7, 7, ("ab3de3c86d1a3762", "b0ab827c7b6094e2"), ("hold",)),
            "b-current": ("cabd05ee74f6137f", "8da6ced685a9c8c4", "e4827a8649c41e3f", 9, 9, ("2ae7131dd2485a9f", "45c5f8d4d8fbd8d8"), ("hold",)),
        }
        actual = {}
        for case in (*COMMITMENT_CASES, *PROBE_CASES):
            actual[case.case_id] = (
                case.state.controller_family, case.state.device, case.state.phase,
                case.state.position, case.state.target, case.state.controls,
                case.expected_actions,
            )
        self.assertEqual(actual, expected)

    def test_actor_request_uses_only_public_state_controls_array_and_null_preload(self):
        envelope = actor_envelope(INTERFACE_STATE, None, 1)
        user = envelope["messages"][1]["content"]
        self.assertIn('"material":null', user)
        self.assertIn('"controls":[', user)
        for forbidden in (
            "first_control",
            "second_control",
            "expected_action",
            "world-a",
            "branch",
            "relation",
        ):
            self.assertNotIn(forbidden, user)
        self.assertTrue(user.endswith("/no_think"))
        for world in (WORLD_A, WORLD_B):
            acquisition = actor_envelope(world.acquisition, None, 2)
            self.assertIn('"material":null', acquisition["messages"][1]["content"])

    def test_action_parser_is_exact_and_does_not_repair(self):
        state = COMMITMENT_CASES[0].state
        good = json.dumps({"actions": list(state.controls)})
        self.assertEqual(parse_actions(good, state, True).actions, state.controls)
        for bad in (
            '{"actions":["hold","hold"]}',
            '{"actions":["x"]}',
            '{"actions":[],"actions":[]}',
            '{"actions":["%s","%s"],"phase":"x"}' % state.controls,
        ):
            self.assertIsNone(parse_actions(bad, state, True).actions)

    def test_candidate_parser_retains_null_but_governor_refuses_without_semantic_oracle(self):
        parsed = parse_candidate('{"change":null,"counterevidence":""}')
        self.assertEqual(parsed.candidate, {"change": None, "counterevidence": ""})
        occurrence = acquisition_occurrence(
            WORLD_A.acquisition,
            WORLD_A.acquisition_profile,
            WORLD_A.acquisition.controls,
        )
        governance = govern_candidate(parsed, occurrence, WORLD_A.acquisition.controls)
        self.assertFalse(governance["admitted"])
        semantic_wrong = CandidateParse(
            {"change": "The opposite profile applies.", "counterevidence": "Anything."},
            None,
        )
        self.assertTrue(
            govern_candidate(semantic_wrong, occurrence, WORLD_A.acquisition.controls)[
                "admitted"
            ]
        )

    def test_control_copy_refuses_and_nulls_governed_presence_and_content(self):
        occurrence = acquisition_occurrence(
            WORLD_A.acquisition,
            WORLD_A.acquisition_profile,
            WORLD_A.acquisition.controls,
        )
        copied = CandidateParse(
            {
                "change": f"Use {WORLD_A.acquisition.controls[0]}",
                "counterevidence": "contradiction",
            },
            None,
        )
        governance = govern_candidate(copied, occurrence, WORLD_A.acquisition.controls)
        materials = {
            "occurrence": occurrence,
            "governance": governance,
            "source_family": WORLD_A.acquisition.controller_family,
        }
        state = COMMITMENT_CASES[0].state
        self.assertIsNotNone(offer_material("authored_direct", materials, state))
        for key in ("governed_candidate", "presence_ablation", "content_ablation"):
            self.assertIsNone(offer_material(key, materials, state))

    def test_content_ablation_matches_each_utf8_byte_length(self):
        candidate = {"change": "éx", "counterevidence": "雪"}
        ablated = content_ablation(candidate)
        self.assertEqual(ablated, {"change": "xxx", "counterevidence": "xxx"})
        for key in candidate:
            self.assertEqual(
                len(ablated[key].encode("utf-8")),
                len(candidate[key].encode("utf-8")),
            )

    def test_lexical_diagnostic_is_offer_blind_and_deterministic(self):
        governance = {
            "candidate": {
                "change": "phase controls family behavior",
                "counterevidence": "contradictory movement",
            }
        }
        first = lexical_diagnostic(WORLD_A, governance)
        second = lexical_diagnostic(WORLD_A, governance)
        self.assertEqual(first, second)
        self.assertEqual(set(first["scores"]), {
            "a-p0-up", "a-p0-down", "a-p1-up", "a-p1-down", "a-other", "a-current"
        })

    def test_schedule_is_exact_rotated_and_request_parity_is_structural(self):
        schedule = later_schedule(admitted_materials())
        self.assertEqual((len(schedule), schedule[0].logical_index, schedule[-1].logical_index), (64, 6, 69))
        first = [call.offer_key for call in schedule[:6]]
        second = [call.offer_key for call in schedule[6:12]]
        self.assertEqual(first, list(COMMITMENT_OFFERS))
        self.assertEqual(second, list(COMMITMENT_OFFERS[1:] + COMMITMENT_OFFERS[:1]))
        first_case = {call.offer_key: call for call in schedule[:6]}
        self.assertEqual(
            first_case["no_persistence"].request_body,
            first_case["presence_ablation"].request_body,
        )
        self.assertEqual(
            first_case["authored_direct"].request_body,
            first_case["governed_candidate"].request_body,
        )
        self.assertNotEqual(
            first_case["governed_candidate"].request_body,
            first_case["content_ablation"].request_body,
        )
        probe_start = schedule[48:52]
        self.assertEqual([call.offer_key for call in probe_start], list(PROBE_OFFERS))

    def test_full_fake_contact_completes_69_calls_with_null_verdicts(self):
        fake = FakeInvoker()
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "evidence"
            summary = run_contact(fake, evidence, {"valid": True})
            self.assertEqual(summary["contact_state"], "completed")
            self.assertEqual(summary["completed_logical_calls"], 69)
            self.assertEqual(summary["physical_attempts"], 69)
            self.assertEqual(len(summary["cells"]), 64)
            self.assertIsNone(summary["formation_verdict"])
            self.assertIsNone(summary["validation_verdict"])
            self.assertEqual(len(summary["content_diagnostics"]), 8)
            self.assertTrue(
                all(item["interpretable"] for item in summary["content_diagnostics"])
            )
            self.assertTrue(summary["request_parity_equivalence_classes"])
            self.assertTrue(summary["interface_observability"]["observable"])
            self.assertEqual(len(summary["acquisitions"]), 2)
            self.assertTrue(all("offer_utf8_length" in cell for cell in summary["cells"]))
            self.assertTrue((evidence / "summary.json").exists())

    def test_malformed_interpreter_continues_with_predeclared_null_equivalence(self):
        fake = FakeInvoker(malformed_interpreter=True)
        with tempfile.TemporaryDirectory() as directory:
            summary = run_contact(fake, Path(directory) / "evidence", {"valid": True})
        self.assertEqual(summary["contact_state"], "completed")
        self.assertTrue(all(not value["admitted"] for value in summary["governance"].values()))
        first_case_groups = [
            group
            for group in summary["request_parity_equivalence_classes"]
            if group["case_id"] == "a-p0-up"
        ]
        self.assertTrue(any(len(group["offers"]) == 5 for group in first_case_groups))
        self.assertTrue(all(not item["available"] for item in summary["content_diagnostics"]))
        self.assertTrue(all("action_difference" not in item for item in summary["content_diagnostics"]))
        self.assertTrue(all("language" not in item for item in summary["presence_diagnostics"]))

    def test_large_prompt_token_delta_is_unavailable_without_action_language(self):
        fake = FakeInvoker(large_content_delta=True)
        with tempfile.TemporaryDirectory() as directory:
            summary = run_contact(fake, Path(directory) / "evidence", {"valid": True})
        self.assertTrue(all(not item["available"] for item in summary["content_diagnostics"]))
        self.assertTrue(all("action_difference" not in item for item in summary["content_diagnostics"]))

    def test_provider_receipt_and_transport_retry_are_frozen(self):
        with tempfile.TemporaryDirectory() as directory:
            stopped = run_contact(
                FakeInvoker(), Path(directory) / "invalid", {"valid": False}
            )
        self.assertEqual(stopped["stop_reason"], "provider_receipt_invalid")
        self.assertEqual(stopped["physical_attempts"], 0)
        retrying = FakeInvoker(retry_first=True)
        with tempfile.TemporaryDirectory() as directory:
            completed = run_contact(
                retrying, Path(directory) / "retry", {"valid": True}
            )
        self.assertEqual(completed["contact_state"], "completed")
        self.assertEqual(completed["physical_attempts"], 70)
        self.assertEqual(retrying.calls[:2][0][0].call_id, retrying.calls[:2][1][0].call_id)

    def test_cli_requires_explicit_live_flag(self):
        with patch("sys.argv", ["runner", "--evidence-dir", "unused"]):
            with self.assertRaisesRegex(SystemExit, "live contact requires --live"):
                main()

    def test_invalid_acquisition_stops_without_search_or_later_calls(self):
        fake = FakeInvoker(invalid_acquisition=True)
        with tempfile.TemporaryDirectory() as directory:
            summary = run_contact(fake, Path(directory) / "evidence", {"valid": True})
        self.assertEqual(summary["contact_state"], "stopped")
        self.assertEqual(summary["stop_reason"], "world-a_acquisition_pair_unobservable")
        self.assertEqual(summary["physical_attempts"], 2)
        self.assertEqual(summary["completed_logical_calls"], 2)


if __name__ == "__main__":
    unittest.main()
