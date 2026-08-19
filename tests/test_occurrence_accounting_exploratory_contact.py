import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from contact.exploratory_developmental_contact import InvocationFailure, ProviderAttempt
from contact.occurrence_accounting_exploratory_contact import (
    ACTOR_SETTINGS,
    AUTHOR_SETTINGS,
    CONDITIONS,
    CONTENT_CONTROL_ALPHABET,
    INTERFACE_STATE,
    MODEL,
    MODEL_DIGEST,
    PHYSICAL_CALL_CEILING,
    PLANNED_LOGICAL_CALLS,
    PUBLIC_FORMATION_CONDITIONS,
    ROUND_ORDERS,
    TOKEN_DELTA_CEILING,
    WORLD_E,
    WORLD_F,
    WORLDS,
    AccountParse,
    CandidateParse,
    LogicalCall,
    account_diagnostic,
    account_envelope,
    actor_envelope,
    candidate_envelope,
    candidate_schedule,
    content_control,
    deterministic_restatement,
    govern_candidate,
    main,
    parse_account,
    parse_actions,
    parse_candidate,
    run_contact,
)
from micro_environment.phase_coupled_specimen import (
    acquisition_occurrence,
    canonical_json_bytes,
    offer_envelope,
)


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
        *,
        null_account=False,
        invalid_world=None,
        invalid_interface=False,
        malformed_condition=None,
        unstable_condition=None,
        carryover=False,
        collapsed_condition=None,
        large_token_delta=False,
        retry_first=False,
    ):
        self.null_account = null_account
        self.invalid_world = invalid_world
        self.invalid_interface = invalid_interface
        self.malformed_condition = malformed_condition
        self.unstable_condition = unstable_condition
        self.carryover = carryover
        self.collapsed_condition = collapsed_condition
        self.large_token_delta = large_token_delta
        self.retry_first = retry_first
        self.calls = []

    def __call__(self, call, attempt_index):
        self.calls.append((call, attempt_index))
        if self.retry_first and len(self.calls) == 1:
            failed = ProviderAttempt(
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
            raise InvocationFailure("transport_failure", failed, True)
        if call.responsibility == "actor":
            if self.invalid_interface and call.call_id == "interface-disposable":
                content = '{"actions":["not-listed"]}'
            elif self.invalid_world and call.call_id == f"{self.invalid_world}-acquisition":
                content = '{"actions":["not-listed","not-listed"]}'
            elif call.commitment:
                content = json.dumps({"actions": list(call.state.controls)})
            else:
                content = '{"actions":["hold"]}'
            return provider_attempt(call, attempt_index, content)
        if call.responsibility == "account":
            account = None if self.null_account else (
                "The recorded controls changed phase and position in the two recorded steps."
            )
            return provider_attempt(call, attempt_index, json.dumps({"account": account}))

        condition = call.offer_key
        if self.malformed_condition == condition and call.repetition == 1:
            return provider_attempt(call, attempt_index, "not-json")
        effective = condition
        if self.carryover and condition == "withheld":
            effective = "delivered"
        if self.collapsed_condition == condition:
            effective = "delivered"
        if condition in ("direct", "withheld") and not (
            self.unstable_condition == condition and call.repetition == 2
        ) and not (self.carryover and condition == "withheld"):
            effective = "direct"
        if self.unstable_condition == condition and call.repetition == 2:
            effective = f"{condition}-unstable"
        candidate = {
            "change": f"candidate change for {effective}",
            "counterevidence": f"counterevidence for {effective}",
        }
        if call.same_response:
            content = json.dumps(
                {
                    "account": "same-response account",
                    "change": candidate["change"],
                    "counterevidence": candidate["counterevidence"],
                }
            )
        else:
            content = json.dumps(candidate)
        prompt_tokens = 110 if condition == "delivered" else 112 if condition == "content_control" else 100
        if self.large_token_delta and condition == "content_control":
            prompt_tokens = 150
        return provider_attempt(call, attempt_index, content, prompt_tokens)


def world_data():
    result = {}
    for world in WORLDS:
        occurrence = acquisition_occurrence(world.state, world.profile, world.state.controls)
        account = {"account": "A fixed model-authored account."}
        result[world.world_id] = {
            "occurrence": occurrence,
            "controls": world.state.controls,
            "account_object": account,
            "content_control": content_control(account),
        }
    return result


class OccurrenceAccountingExploratoryContactTests(unittest.TestCase):
    def test_model_worlds_settings_and_budgets_are_frozen(self):
        self.assertEqual(MODEL, "ai/qwen3:14B-Q6_K")
        self.assertEqual(
            MODEL_DIGEST,
            "sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219",
        )
        self.assertEqual((PLANNED_LOGICAL_CALLS, PHYSICAL_CALL_CEILING), (37, 40))
        self.assertEqual(TOKEN_DELTA_CEILING, 24)
        self.assertEqual(AUTHOR_SETTINGS["max_tokens"], 256)
        self.assertEqual(ACTOR_SETTINGS["max_tokens"], 128)
        self.assertEqual(AUTHOR_SETTINGS["response_format"], {"type": "json_object"})
        expected = {
            "world-e": ("c378816a8c4ed06f", "adfc8f4a1b01d510", "72b4369223095ae5", ("91dd8389d9c3730a", "c07e743cb43592c8"), 0),
            "world-f": ("95d703a257e5a8fb", "a4c67fdac36e0ef5", "41dd49a87033606b", ("20de6d24dbe28705", "9c3e211ff8cc41c2"), 1),
        }
        actual = {
            world.world_id: (
                world.state.controller_family,
                world.state.device,
                world.state.phase,
                world.state.controls,
                world.profile.phase_zero_increasing_slot,
            )
            for world in WORLDS
        }
        self.assertEqual(actual, expected)
        self.assertEqual(INTERFACE_STATE.device, "0ac23ba43c882959")

    def test_actor_and_author_prompts_freeze_null_material_and_hide_harness_labels(self):
        for state, count in ((INTERFACE_STATE, 1), (WORLD_E.state, 2), (WORLD_F.state, 2)):
            envelope = actor_envelope(state, count)
            user = envelope["messages"][1]["content"]
            self.assertIn(offer_envelope(None).decode("utf-8"), user)
            self.assertTrue(user.endswith("/no_think"))
        occurrence = acquisition_occurrence(WORLD_E.state, WORLD_E.profile, WORLD_E.state.controls)
        direct = candidate_envelope(occurrence, None)
        self.assertTrue(direct["messages"][1]["content"].endswith("/no_think"))
        for forbidden in ("world-e", "withheld_null", "exact_account_output", "round-1"):
            self.assertNotIn(forbidden, canonical_json_bytes(direct).decode("utf-8"))
        self.assertTrue(account_envelope(occurrence)["messages"][1]["content"].endswith("/no_think"))
        static_user = candidate_envelope(
            occurrence, None, static_expanded=True
        )["messages"][1]["content"]
        self.assertIn("what remains\nuncertain.", static_user)

    def test_parsers_are_strict_and_same_response_requires_key_order(self):
        self.assertEqual(
            parse_actions('{"actions":["hold"]}', INTERFACE_STATE, False).actions,
            ("hold",),
        )
        self.assertIsNone(parse_actions('{"actions":[],"actions":[]}', INTERFACE_STATE, False).actions)
        self.assertEqual(parse_account('{"account":null}'), AccountParse({"account": None}, None))
        self.assertIsNone(parse_account('{"account":"x","extra":1}').account_object)
        good = '{"account":"a","change":"c","counterevidence":"e"}'
        self.assertEqual(parse_candidate(good, same_response=True).candidate, {"change": "c", "counterevidence": "e"})
        bad_order = '{"change":"c","account":"a","counterevidence":"e"}'
        self.assertEqual(parse_candidate(bad_order, same_response=True).refusal, "invalid_same_response_key_order")
        self.assertEqual(parse_candidate('{"change":null,"counterevidence":"e"}').candidate["change"], None)

    def test_restatement_is_deterministic_public_and_complete(self):
        occurrence = acquisition_occurrence(WORLD_E.state, WORLD_E.profile, WORLD_E.state.controls)
        first = deterministic_restatement(occurrence)
        self.assertEqual(first, deterministic_restatement(occurrence))
        self.assertTrue(first.startswith("Recorded family c378816a8c4ed06f; device adfc8f4a1b01d510;"))
        self.assertIn("Step 1: action 91dd8389d9c3730a", first)
        self.assertIn("Step 2: action c07e743cb43592c8", first)
        self.assertNotIn("slot", first.casefold())
        self.assertNotIn("world-e", first)

    def test_content_control_uses_only_length_seed_and_non_hex_alphabet(self):
        left = {"account": "é relation one"}
        right = {"account": "xx relation two"}
        self.assertEqual(len(canonical_json_bytes(left)), len(canonical_json_bytes(right)))
        left_control = content_control(left)
        right_control = content_control(right)
        self.assertEqual(left_control, right_control)
        self.assertEqual(len(canonical_json_bytes(left)), len(canonical_json_bytes(left_control)))
        self.assertTrue(set(left_control["account"]) <= set(CONTENT_CONTROL_ALPHABET))
        self.assertFalse(set(left_control["account"]) & set("0123456789abcdef"))

    def test_account_diagnostic_never_mints_a_semantic_class(self):
        occurrence = acquisition_occurrence(WORLD_E.state, WORLD_E.profile, WORLD_E.state.controls)
        relation = AccountParse({"account": "Use slot zero across devices."}, None)
        diagnostic = account_diagnostic(relation, occurrence, WORLD_E.state.controls)
        self.assertEqual(diagnostic["class"], "indeterminate")
        self.assertTrue(diagnostic["relation_already_present_remains_live"])
        self.assertEqual(account_diagnostic(AccountParse({"account": None}, None), occurrence, WORLD_E.state.controls)["class"], "not_classified")

    def test_governor_is_nonsemantic_and_refuses_exact_control_copy(self):
        occurrence = acquisition_occurrence(WORLD_E.state, WORLD_E.profile, WORLD_E.state.controls)
        copied = CandidateParse(
            {"change": f"Use {WORLD_E.state.controls[0]}", "counterevidence": "later contradiction"}
        )
        self.assertFalse(govern_candidate(copied, occurrence, WORLD_E.state.controls)["admitted"])
        wrong_but_noncopying = CandidateParse(
            {"change": "Use the opposite relation.", "counterevidence": "later contradiction"}
        )
        self.assertTrue(govern_candidate(wrong_but_noncopying, occurrence, WORLD_E.state.controls)["admitted"])

    def test_schedule_has_frozen_slots_rounds_lineage_and_request_identity(self):
        schedule = candidate_schedule(world_data())
        self.assertEqual((len(schedule), schedule[0].logical_index, schedule[-1].logical_index), (32, 6, 37))
        for round_number in (1, 2):
            for world in WORLDS:
                actual = [
                    call.offer_key
                    for call in schedule
                    if call.repetition == round_number and call.world_id == world.world_id
                ]
                self.assertEqual(actual, list(ROUND_ORDERS[(round_number, world.world_id)]))
        e_calls = [call for call in schedule if call.world_id == "world-e"]
        direct = [call for call in e_calls if call.offer_key == "direct"]
        withheld = [call for call in e_calls if call.offer_key == "withheld"]
        self.assertEqual({call.request_body for call in direct + withheld}, {direct[0].request_body})
        self.assertTrue(all(call.account_receipt == "world-e-account" for call in withheld))
        self.assertTrue(all(not call.account_is_request_parent for call in withheld))
        self.assertTrue(all(call.account_is_request_parent for call in e_calls if call.offer_key == "delivered"))
        self.assertEqual(
            {call.offer_key: call.formation_condition for call in e_calls[:8]},
            PUBLIC_FORMATION_CONDITIONS,
        )

    def test_full_fake_contact_completes_and_emits_only_weak_exact_label(self):
        fake = FakeInvoker()
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "evidence"
            summary = run_contact(fake, evidence, {"valid": True})
            self.assertTrue((evidence / "summary.json").exists())
        self.assertEqual(summary["contact_state"], "completed")
        self.assertEqual(summary["completed_logical_calls"], 37)
        self.assertEqual(summary["physical_attempts"], 37)
        self.assertEqual(summary["usage"], {"prompt_tokens": 3788, "completion_tokens": 296})
        self.assertTrue(all(item["account_delivery_conditioned_exact_candidate_difference"] for item in summary["world_comparisons"]))
        self.assertTrue(all(item["withheld_matches_direct"] for item in summary["world_comparisons"]))
        self.assertTrue(all(item["relation_already_present_remains_live"] for item in summary["world_comparisons"]))
        self.assertIsNone(summary["formation_verdict"])
        self.assertIsNone(summary["validation_verdict"])

    def test_null_accounts_omit_only_account_dependent_candidate_calls(self):
        fake = FakeInvoker(null_account=True)
        with tempfile.TemporaryDirectory() as directory:
            summary = run_contact(fake, Path(directory) / "evidence", {"valid": True})
        self.assertEqual(summary["contact_state"], "completed")
        self.assertEqual(summary["completed_logical_calls"], 29)
        self.assertTrue(all(not item["account_delivery_conditioned_exact_candidate_difference"] for item in summary["world_comparisons"]))
        self.assertTrue(all(set(item["unavailable_conditions"]) == {"delivered", "content_control"} for item in summary["world_comparisons"]))
        called_conditions = {call.offer_key for call, _ in fake.calls if call.responsibility == "candidate"}
        self.assertFalse({"delivered", "content_control"} & called_conditions)

    def test_invalid_acquisition_skips_one_world_without_screening_other(self):
        fake = FakeInvoker(invalid_world="world-e")
        with tempfile.TemporaryDirectory() as directory:
            summary = run_contact(fake, Path(directory) / "evidence", {"valid": True})
        self.assertEqual(summary["contact_state"], "completed")
        self.assertEqual(summary["completed_logical_calls"], 20)
        comparisons = {item["world_id"]: item for item in summary["world_comparisons"]}
        self.assertEqual(comparisons["world-e"]["reason"], "acquisition_occurrence_unavailable")
        self.assertTrue(comparisons["world-f"]["account_delivery_conditioned_exact_candidate_difference"])

    def test_instability_malformed_cells_and_token_disparity_forbid_label(self):
        cases = (
            (FakeInvoker(unstable_condition="delivered"), "delivered"),
            (FakeInvoker(malformed_condition="restatement"), "restatement"),
            (FakeInvoker(large_token_delta=True), None),
        )
        for fake, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                summary = run_contact(fake, Path(directory) / "evidence", {"valid": True})
                self.assertTrue(all(not item["account_delivery_conditioned_exact_candidate_difference"] for item in summary["world_comparisons"]))
                if expected == "delivered":
                    self.assertTrue(all(expected in item["unstable_conditions"] for item in summary["world_comparisons"]))
                elif expected == "restatement":
                    self.assertTrue(all(expected in item["unavailable_conditions"] for item in summary["world_comparisons"]))
                else:
                    self.assertTrue(all(not item["prompt_mass_comparison_available"] for item in summary["world_comparisons"]))

    def test_withheld_carryover_pattern_is_invalid_not_positive(self):
        fake = FakeInvoker(carryover=True)
        with tempfile.TemporaryDirectory() as directory:
            summary = run_contact(fake, Path(directory) / "evidence", {"valid": True})
        self.assertTrue(all(item["carryover_pattern_delivery_contrast_invalid"] for item in summary["world_comparisons"]))
        self.assertTrue(all(not item["account_delivery_conditioned_exact_candidate_difference"] for item in summary["world_comparisons"]))

    def test_exact_control_collapse_suppresses_weak_delivery_label(self):
        fake = FakeInvoker(collapsed_condition="restatement")
        with tempfile.TemporaryDirectory() as directory:
            summary = run_contact(fake, Path(directory) / "evidence", {"valid": True})
        for comparison in summary["world_comparisons"]:
            self.assertIn("restatement-equivalent", comparison["collapse_labels"])
            self.assertFalse(
                comparison["account_delivery_conditioned_exact_candidate_difference"]
            )
            self.assertFalse(comparison["weak_label_available"])

    def test_provider_receipt_retry_interface_stop_and_cli_gate_are_frozen(self):
        with tempfile.TemporaryDirectory() as directory:
            stopped = run_contact(FakeInvoker(), Path(directory) / "invalid", {"valid": False})
        self.assertEqual((stopped["stop_reason"], stopped["physical_attempts"]), ("provider_receipt_invalid", 0))
        retry = FakeInvoker(retry_first=True)
        with tempfile.TemporaryDirectory() as directory:
            completed = run_contact(retry, Path(directory) / "retry", {"valid": True})
        self.assertEqual((completed["contact_state"], completed["physical_attempts"]), ("completed", 38))
        invalid = FakeInvoker(invalid_interface=True)
        with tempfile.TemporaryDirectory() as directory:
            interface_stop = run_contact(invalid, Path(directory) / "stop", {"valid": True})
        self.assertEqual((interface_stop["stop_reason"], interface_stop["physical_attempts"]), ("interface_action_unobservable", 1))
        with patch("sys.argv", ["runner", "--evidence-dir", "unused"]):
            with self.assertRaisesRegex(SystemExit, "live contact requires --live"):
                main()


if __name__ == "__main__":
    unittest.main()
