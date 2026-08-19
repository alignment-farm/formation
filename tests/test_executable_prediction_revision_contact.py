import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from contact.executable_prediction_revision_contact import (
    ACQUISITION_SETTINGS,
    CASE_MANIFEST_SHA256,
    CASE_MANIFEST_UTF8_LENGTH,
    MODEL,
    ORDINARY_SETTINGS,
    PHYSICAL_CALL_CEILING,
    PLANNED_COMPLETION_ALLOWANCE,
    PLANNED_LOGICAL_CALLS,
    REPORT_CONDITIONS,
    SAME_RESPONSE_SETTINGS,
    STATIC_RULE_SHA256,
    WITNESS_SHA256,
    WITNESS_UTF8_LENGTH,
    WORLD_J,
    WORLD_K,
    _lookup_rule,
    _validate_frozen_artifacts,
    acquisition_prompt,
    base_material,
    canonical_json_bytes,
    case_manifest,
    evaluate_rule,
    integrity_audit,
    later_same_prompt,
    main,
    ordinary_prompt,
    parent_withheld_material,
    parse_acquisition,
    parse_same_response,
    recognize_rule,
    rule_system,
    run_contact,
    selected_material,
    sha256_bytes,
    static_prompt,
    witness_artifact,
)
from contact.exploratory_developmental_contact import InvocationFailure, ProviderAttempt


def attempt_for(call, attempt_index, content):
    envelope = {
        "choices": [{"message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 1},
    }
    body = json.dumps(envelope, ensure_ascii=True, separators=(",", ":")).encode()
    return ProviderAttempt(
        call.logical_index, attempt_index, call.call_id, call.request_body, body,
        envelope, envelope["choices"][0]["message"], content, 200,
        "start", "end", 0.01,
    )


class FakeInvoker:
    def __init__(self, *, unavailable=(), malformed_same=(), retry_first=False, fatal_first=None, content_overrides=None):
        self.unavailable = set(unavailable)
        self.malformed_same = set(malformed_same)
        self.retry_first = retry_first
        self.fatal_first = fatal_first
        self.content_overrides = content_overrides or {}
        self.calls = []

    def __call__(self, call, attempt_index):
        self.calls.append((call, attempt_index))
        if self.retry_first and len(self.calls) == 1:
            failed = ProviderAttempt(
                call.logical_index, attempt_index, call.call_id, call.request_body,
                b"", {"transport_error": "fake"}, None, None, None,
                "start", "end", 0.01, "transport_failure",
            )
            raise InvocationFailure("transport_failure", failed, True)
        if self.fatal_first and len(self.calls) == 1:
            failed = ProviderAttempt(
                call.logical_index, attempt_index, call.call_id, call.request_body,
                b"bad", {"error": self.fatal_first}, None, None, 500,
                "start", "end", 0.01, self.fatal_first,
            )
            raise InvocationFailure(self.fatal_first, failed, False)
        if call.logical_index in self.content_overrides:
            content = self.content_overrides[call.logical_index]
        elif call.logical_index in self.unavailable:
            content = None
        elif call.logical_index == 1:
            content = '{"prediction":"bren"}'
        elif call.logical_index == 2:
            content = '{"prediction":"zafren"}'
        elif call.logical_index == 3:
            content = '{"prediction":"qoril"}'
        elif call.logical_index in self.malformed_same:
            content = '{"successor":"x","parent":"y"}'
        elif call.condition in {"same_response", "later_same_response"}:
            content = json.dumps(
                {
                    "parent": "zafren" if call.world_id == "J" else "qoril",
                    "successor": "ulmec" if call.world_id == "J" else "vesan",
                },
                separators=(",", ":"),
            )
        else:
            content = "zafren" if call.world_id == "J" else "qoril"
        return attempt_for(call, attempt_index, content)


class ExecutablePredictionRevisionContactTests(unittest.TestCase):
    def run_fake(self, fake=None, **kwargs):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name) / "evidence"
        fake = fake or FakeInvoker()
        summary = run_contact(fake, directory, {"valid": True}, **kwargs)
        return summary, fake, directory

    def test_frozen_manifest_witness_and_static_rules_reproduce(self):
        manifest, witness = _validate_frozen_artifacts()
        manifest_bytes = canonical_json_bytes(manifest)
        witness_bytes = canonical_json_bytes(witness)
        self.assertEqual((len(manifest_bytes), sha256_bytes(manifest_bytes)), (CASE_MANIFEST_UTF8_LENGTH, CASE_MANIFEST_SHA256))
        self.assertEqual((len(witness_bytes), sha256_bytes(witness_bytes)), (WITNESS_UTF8_LENGTH, WITNESS_SHA256))
        for item in witness["worlds"]:
            self.assertEqual(sha256_bytes(item["static_rule_raw"].encode()), STATIC_RULE_SHA256[item["world"]])
            self.assertEqual(len(item["pairs"]), 18)

    def test_all_awkward_scalar_strings_remain_literal_rules(self):
        values = ["", "prose", "x" * 20_000, "```json\n{}\n```", '{"when":', "zafren", "RULE_AST_V1\n{}"]
        for value in values:
            with self.subTest(value=value):
                rule = recognize_rule(value)
                self.assertEqual(rule.kind, "literal_rule")
                self.assertEqual(evaluate_rule(rule, WORLD_J.case(2).input), {"status": "prediction", "value": value})
        self.assertIsNone(recognize_rule(None))
        self.assertIsNone(recognize_rule("\ud800"))

    def test_valid_ast_and_failed_ast_marker_are_distinct(self):
        raw = _lookup_rule(WORLD_J, {"J0", "J3"})
        rule = recognize_rule(raw + "  \n")
        self.assertEqual(rule.kind, "ast_rule")
        self.assertEqual(evaluate_rule(rule, WORLD_J.case(0).input)["value"], "ulmec")
        duplicate = 'RULE_AST_V1\n{"when":{"bool":true},"when":{"bool":false},"predict":{"lit":"zafren"}}'
        self.assertEqual(recognize_rule(duplicate).kind, "literal_rule")

    def test_missing_fields_use_three_valued_logic(self):
        raw = 'RULE_AST_V1\n{"predict":{"lit":"zafren"},"when":{"not":{"eq":[{"field":"missing"},{"lit":"x"}]}}}'
        self.assertEqual(evaluate_rule(recognize_rule(raw), WORLD_J.case(0).input), {"status": "evaluation_unavailable", "value": None})
        false_and_missing = 'RULE_AST_V1\n{"predict":{"lit":"zafren"},"when":{"and":[{"bool":false},{"eq":[{"field":"missing"},{"lit":"x"}]}]}}'
        self.assertEqual(evaluate_rule(recognize_rule(false_and_missing), WORLD_J.case(0).input), {"status": "out_of_scope", "value": None})

    def test_request_surfaces_and_settings_are_frozen(self):
        system = rule_system(WORLD_J)
        self.assertIn('["zafren","ulmec"]', system)
        self.assertNotIn("<PREDICTION_VOCABULARY_JSON>", system)
        self.assertNotIn("response_format", ORDINARY_SETTINGS)
        self.assertEqual(ACQUISITION_SETTINGS["response_format"], {"type": "json_object"})
        self.assertEqual(SAME_RESPONSE_SETTINGS["max_tokens"], 1024)
        self.assertEqual(PLANNED_COMPLETION_ALLOWANCE, 18_816)
        self.assertEqual(MODEL, "ai/qwen3:14B-Q6_K")
        self.assertNotIn("FIRST EXPERIENCE", static_prompt(WORLD_J))

    def test_material_statuses_and_withheld_single_mutation(self):
        case = WORLD_J.case(1)
        trial = {"status": "prediction", "value": "zafren"}
        selected = selected_material("iv04.content", "raw", trial, case)
        withheld = selected_material("iv04.content", "raw", trial, case, withhold=True)
        changed = {key for key in selected if selected[key] != withheld[key]}
        self.assertEqual(changed, {"external_result"})
        self.assertEqual(withheld["external_result"]["status"], "result_not_revealed")
        self.assertEqual(parent_withheld_material(case)["trial"]["status"], "not_available")
        prompt = ordinary_prompt({"x": 1}, base_material())
        self.assertTrue(prompt.endswith("/no_think"))

    def test_strict_acquisition_and_same_response_parsing(self):
        self.assertEqual(parse_acquisition('{"prediction":"zafren"}', WORLD_J.prediction_vocabulary), "zafren")
        self.assertIsNone(parse_acquisition('{"prediction":"zafren","prediction":"ulmec"}', WORLD_J.prediction_vocabulary))
        self.assertIsNone(parse_acquisition('{"prediction":"other"}', WORLD_J.prediction_vocabulary))
        self.assertEqual(parse_same_response('{"parent":"x","successor":null}'), ("x", None))
        self.assertIsNone(parse_same_response('{"successor":"y","parent":"x"}'))
        self.assertIsNone(parse_same_response('{"parent":"x","successor":"y","extra":1}'))

    def test_later_same_prompt_distinguishes_empty_and_unavailable(self):
        occurrence = {"input": {}, "prediction": {}, "result": {}}
        unavailable = later_same_prompt(WORLD_J, occurrence, None)
        empty = later_same_prompt(WORLD_J, occurrence, "")
        self.assertIn("CURRENT PARENT\nnull", unavailable)
        self.assertIn('CURRENT PARENT\n""', empty)
        self.assertIn(canonical_json_bytes(WORLD_J.case(8).input).decode(), unavailable)
        self.assertNotIn(canonical_json_bytes(WORLD_J.case(1).input).decode(), unavailable)

    def test_full_fake_packet_has_exact_schedule_denominators_and_repeats(self):
        summary, fake, directory = self.run_fake()
        self.assertEqual((summary["contact_state"], summary["completed_logical_calls"], summary["physical_attempts"]), ("completed", PLANNED_LOGICAL_CALLS, PLANNED_LOGICAL_CALLS))
        self.assertTrue(summary["integrity"]["valid"])
        self.assertEqual([call.call_id for call, _ in fake.calls], [f"iv{index:02d}" for index in range(1, 36)])
        calls = {call.logical_index: call for call, _ in fake.calls}
        for left, right in ((4, 6), (5, 7), (8, 9), (17, 18), (26, 27), (31, 32)):
            self.assertEqual(calls[left].request_body, calls[right].request_body)
        self.assertEqual(len(summary["condition_report"]), len(REPORT_CONDITIONS))
        self.assertTrue(all(item["assigned_world_units"] == 2 and item["completed_count"] == 2 for item in summary["condition_report"]))
        self.assertTrue(all(item["assigned_world_units"] == 2 for item in summary["atomic_fact_report"]))
        selected_facts = next(item for item in summary["atomic_fact_report"] if item["condition"] == "selected_successor")["facts"]
        self.assertIn("parent_test_in_scope", selected_facts)
        self.assertIn("parent_test_prediction_differed_from_result", selected_facts)
        self.assertEqual(summary["completion_usage"]["logical_completion_tokens"], 35)
        self.assertEqual(summary["completion_usage"]["physical_completion_tokens"], 35)
        self.assertEqual(len((directory / "case-manifest.json").read_bytes()), CASE_MANIFEST_UTF8_LENGTH)
        self.assertEqual(len((directory / "witness.json").read_bytes()), WITNESS_UTF8_LENGTH)
        proposals = json.loads((directory / "protocol-proposals.json").read_text())
        self.assertEqual([item["proposal_coordinate"] for item in proposals["visible_material"]], ["pvj01", "pvk01"])
        self.assertTrue(all(item["author"] == "deterministic_protocol_constructor" for item in proposals["visible_material"]))
        for selected_index, withheld_index in ((8, 10), (17, 19), (26, 28), (31, 33)):
            selected_user = json.loads(calls[selected_index].request_body)["messages"][1]["content"]
            withheld_user = json.loads(calls[withheld_index].request_body)["messages"][1]["content"]
            selected_material_json = json.loads(selected_user.split("RUNTIME MATERIAL\n", 1)[1].split("\n\nAUTHORSHIP", 1)[0])
            withheld_material_json = json.loads(withheld_user.split("RUNTIME MATERIAL\n", 1)[1].split("\n\nAUTHORSHIP", 1)[0])
            differences = {key for key in selected_material_json if selected_material_json[key] != withheld_material_json[key]}
            self.assertEqual(differences, {"external_result"})
        self.assertEqual(json.loads((directory / "summary.json").read_text())["formation_verdict"], None)

    def test_unavailable_acquisition_and_parent_continue(self):
        summary, fake, directory = self.run_fake(FakeInvoker(unavailable={2, 8}, content_overrides={4: {"unexpected": "object"}}))
        self.assertEqual(summary["contact_state"], "completed")
        self.assertEqual(summary["completed_logical_calls"], 35)
        call8 = json.loads((directory / "calls" / "08-iv08.logical.json").read_text())
        self.assertEqual(call8["runtime_material"]["parent_raw"], None)
        self.assertEqual(call8["runtime_material"]["trial"]["status"], "rule_unavailable")
        call26 = json.loads((directory / "calls" / "26-iv26.logical.json").read_text())
        self.assertEqual(call26["runtime_material"]["parent_raw"], None)
        self.assertEqual(call26["runtime_material"]["trial"]["status"], "rule_unavailable")

    def test_malformed_same_response_remains_assigned(self):
        summary, _, directory = self.run_fake(FakeInvoker(malformed_same={12, 35}))
        self.assertEqual(summary["completed_logical_calls"], 35)
        first = json.loads((directory / "calls" / "12-iv12.logical.json").read_text())
        later = json.loads((directory / "calls" / "35-iv35.logical.json").read_text())
        self.assertFalse(first["envelope_available"])
        self.assertFalse(later["envelope_available"])
        self.assertEqual(next(item for item in summary["condition_report"] if item["condition"] == "same_response")["assigned_world_units"], 2)
        for condition in ("same_response", "later_same_response"):
            facts = next(item for item in summary["atomic_fact_report"] if item["condition"] == condition)["facts"]
            for slot in ("parent", "successor"):
                self.assertEqual(sum(facts[f"{slot}_{kind}"]["count"] for kind in ("literal_rule", "ast_rule", "rule_unavailable")), 2)

    def test_transport_retry_spends_physical_not_logical_slot(self):
        summary, fake, _ = self.run_fake(FakeInvoker(retry_first=True))
        self.assertEqual(summary["completed_logical_calls"], 35)
        self.assertEqual(summary["physical_attempts"], 36)
        self.assertEqual([item[1] for item in fake.calls[:2]], [1, 2])
        for reason in ("http_500", "provider_envelope_invalid"):
            stopped, fatal, _ = self.run_fake(FakeInvoker(fatal_first=reason))
            self.assertEqual((stopped["stop_reason"], len(fatal.calls), stopped["physical_attempts"]), (reason, 1, 1))

    def test_physical_stop_preserves_all_fixed_denominators(self):
        summary, _, _ = self.run_fake(physical_ceiling=5)
        self.assertEqual(summary["contact_state"], "stopped")
        self.assertEqual(summary["stop_reason"], "physical_call_ceiling_reached")
        self.assertEqual(len(summary["condition_report"]), len(REPORT_CONDITIONS))
        self.assertEqual(next(item for item in summary["condition_report"] if item["condition"] == "selected_successor")["completed_count"], 0)

    def test_invalid_provider_and_interface_stop_without_replacement(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name) / "invalid-provider"
        fake = FakeInvoker()
        summary = run_contact(fake, directory, {"valid": False})
        self.assertEqual((summary["stop_reason"], len(fake.calls)), ("provider_receipt_invalid", 0))
        summary2, fake2, _ = self.run_fake(FakeInvoker(unavailable={1}))
        self.assertEqual((summary2["stop_reason"], len(fake2.calls)), ("disposable_interface_unavailable", 1))

    def test_integrity_detects_logical_and_summary_changes(self):
        summary, _, directory = self.run_fake()
        self.assertTrue(summary["integrity"]["valid"])
        logical = directory / "calls" / "08-iv08.logical.json"
        logical.write_text(logical.read_text().replace("selected_successor", "changed"))
        bindings_path = directory / "integrity-bindings.json"
        bindings = json.loads(bindings_path.read_text())
        relative = str(logical.relative_to(directory))
        bindings["sha256"][relative] = sha256_bytes(logical.read_bytes())
        bindings_path.write_text(json.dumps(bindings, indent=2, sort_keys=True) + "\n")
        self.assertFalse(integrity_audit(directory)["valid"])

        summary2, _, directory2 = self.run_fake()
        request = directory2 / "calls" / "08-iv08-a1.request.json"
        meta = directory2 / "calls" / "08-iv08-a1.meta.json"
        request.write_bytes(request.read_bytes() + b" ")
        meta_value = json.loads(meta.read_text())
        meta_value["request_sha256"] = sha256_bytes(request.read_bytes())
        meta.write_text(json.dumps(meta_value, indent=2, sort_keys=True) + "\n")
        self.assertFalse(integrity_audit(directory2)["valid"])

        summary3, _, directory3 = self.run_fake()
        manifest = directory3 / "case-manifest.json"
        manifest.write_bytes(manifest.read_bytes() + b" ")
        self.assertFalse(integrity_audit(directory3)["valid"])

        summary4, _, directory4 = self.run_fake()
        logical4 = directory4 / "calls" / "08-iv08.logical.json"
        value4 = json.loads(logical4.read_text())
        value4["trial_receipt"]["observation"]["value"] = "tampered"
        value4["consequence_receipt"]["value"] = "tampered"
        logical4.write_text(json.dumps(value4, indent=2, sort_keys=True) + "\n")
        bindings4_path = directory4 / "integrity-bindings.json"
        bindings4 = json.loads(bindings4_path.read_text())
        bindings4["sha256"][str(logical4.relative_to(directory4))] = sha256_bytes(logical4.read_bytes())
        bindings4_path.write_text(json.dumps(bindings4, indent=2, sort_keys=True) + "\n")
        self.assertFalse(integrity_audit(directory4)["valid"])

        summary5, _, directory5 = self.run_fake()
        proposals5 = directory5 / "protocol-proposals.json"
        value5 = json.loads(proposals5.read_text())
        value5["visible_material"][0]["author"] = "tampered"
        proposals5.write_text(json.dumps(value5, indent=2, sort_keys=True) + "\n")
        bindings5_path = directory5 / "integrity-bindings.json"
        bindings5 = json.loads(bindings5_path.read_text())
        bindings5["sha256"]["protocol-proposals.json"] = sha256_bytes(proposals5.read_bytes())
        bindings5_path.write_text(json.dumps(bindings5, indent=2, sort_keys=True) + "\n")
        self.assertFalse(integrity_audit(directory5)["valid"])

    def test_cli_requires_explicit_live_flag(self):
        with patch("sys.argv", ["runner", "--evidence-dir", "/tmp/not-used"]):
            with self.assertRaisesRegex(SystemExit, "requires --live"):
                main()


if __name__ == "__main__":
    unittest.main()
