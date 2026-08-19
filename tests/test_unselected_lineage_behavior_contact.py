import json
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from contact.unselected_lineage_behavior_contact import (
    ACTION_SETTINGS,
    ACTION_SYSTEM,
    AUTHORSHIP_SETTINGS,
    AUTHORSHIP_SYSTEM,
    MANIFEST_LENGTH,
    MANIFEST_PATH,
    MANIFEST_SHA256,
    PHYSICAL_CALL_CEILING,
    SMOKE_RECEIPT,
    WITNESS_LENGTH,
    WITNESS_PATH,
    WITNESS_SHA256,
    ActionParse,
    ProviderAttempt,
    ProviderContent,
    RenderAuditor,
    PinnedTokenCounter,
    ContactRefusal,
    CliConfig,
    EvidenceWriter,
    authorship_material,
    authorship_user,
    branch_materials,
    canonical_json_bytes,
    construct_witness,
    collect_provider_receipt,
    later_coordinates,
    load_published,
    main,
    parse_action,
    parse_cli,
    profile,
    proposal_from_content,
    provider_content,
    public_state,
    raw_foreground,
    replay_evidence,
    run_packet,
    sha256_bytes,
    static_lesson,
)
from micro_environment.unselected_lineage_behavior import ProposalReceipt, apply_committed_action
from unselected_lineage_specimen import (
    ABLATION,
    NO_PERSISTENCE,
    RAW_PERSISTENCE,
    RESULT_EXPOSED,
    RESULT_WITHHELD,
    STATIC_INSTRUCTION,
)


class FakeInvoker:
    def __init__(self, overrides=None):
        self.overrides = overrides or {}
        self.seen = []

    def __call__(self, call, attempt):
        self.seen.append((call, attempt))
        override = self.overrides.get((call.index, attempt), self.overrides.get(call.index))
        if override is not None:
            return override(call, attempt) if callable(override) else override
        if call.responsibility == "intermediate_authorship":
            content = f"guidance-{call.invocation}"
        else:
            request = json.loads(call.envelope["messages"][1]["content"].split("\n")[1])
            content = json.dumps({"action": request["device"]["allowed_actions"][0]}, separators=(",", ":"))
        envelope = {"choices": [{"finish_reason": "stop", "message": {"content": content}}], "usage": {"completion_tokens": 1}}
        return ProviderAttempt(call.request_body, canonical_json_bytes(envelope), envelope, 200)


_RENDER_AUDITOR = None


def render_auditor():
    global _RENDER_AUDITOR
    if _RENDER_AUDITOR is not None:
        return _RENDER_AUDITOR
    provider = json.loads(Path("evidence/executable-prediction-revision-contact-20260818/provider.json").read_text())
    template = provider["parsed_inspection"]["config"]["gguf"]["tokenizer.chat_template"]
    tokenizer_path = Path("/Users/macos-user/Library/Caches/formation/Qwen3-14B/7d3da9c56f02b22d31dc1ca97c7ee628d1e2e237/tokenizer.json")
    _RENDER_AUDITOR = PinnedTokenCounter(tokenizer_path, template).render_auditor
    return _RENDER_AUDITOR


class UnselectedLineageContactTests(unittest.TestCase):
    def test_cli_has_no_default_live_path(self):
        with self.assertRaises(SystemExit) as stopped:
            main([])
        self.assertEqual(stopped.exception.code, 2)

    def test_cli_configuration_is_pure_and_modes_are_closed(self):
        candidate = [
            "--live",
            "--evidence-dir",
            "evidence/UNLICENSED-LAUNCH-CANDIDATE",
            "--tokenizer-json",
            "/UNLICENSED/tokenizer.json",
        ]
        canaries = (
            "EvidenceWriter.write",
            "EvidenceWriter",
            "collect_provider_receipt",
            "shell_command",
            "endpoint_receipt",
            "PinnedTokenCounter",
            "render_chat",
            "DockerInvoker",
            "run_packet",
            "replay_evidence",
            "urlopen",
        )
        with ExitStack() as stack:
            for name in canaries:
                stack.enter_context(patch(
                    f"contact.unselected_lineage_behavior_contact.{name}",
                    side_effect=AssertionError(f"contact-adjacent surface entered: {name}"),
                ))
            config = parse_cli(candidate)
        self.assertEqual(
            config,
            CliConfig(
                True,
                False,
                Path("evidence/UNLICENSED-LAUNCH-CANDIDATE"),
                Path("/UNLICENSED/tokenizer.json"),
            ),
        )

        invalid = (
            ["--unknown"],
            ["--live", "--smoke-no-contact"],
            ["--live"],
            ["--smoke-no-contact", "--evidence-dir", "forbidden"],
        )
        for argv in invalid:
            with self.subTest(argv=argv), redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as stopped:
                    parse_cli(argv)
                self.assertEqual(stopped.exception.code, 2)

    def test_smoke_mode_is_exact_and_contact_adjacent_surfaces_fail_closed(self):
        canaries = (
            "EvidenceWriter.write",
            "EvidenceWriter",
            "collect_provider_receipt",
            "shell_command",
            "endpoint_receipt",
            "PinnedTokenCounter",
            "render_chat",
            "DockerInvoker",
            "run_packet",
            "replay_evidence",
            "urlopen",
        )
        stdout = StringIO()
        stderr = StringIO()
        with ExitStack() as stack:
            for name in canaries:
                stack.enter_context(patch(
                    f"contact.unselected_lineage_behavior_contact.{name}",
                    side_effect=AssertionError(f"contact-adjacent surface entered: {name}"),
                ))
            stack.enter_context(redirect_stdout(stdout))
            stack.enter_context(redirect_stderr(stderr))
            self.assertEqual(main(["--smoke-no-contact"]), 0)
        self.assertEqual(stdout.getvalue(), canonical_json_bytes(SMOKE_RECEIPT).decode() + "\n")
        self.assertEqual(stderr.getvalue(), "")

    def test_module_entrypoint_reaches_exact_no_contact_smoke_receipt(self):
        root = Path(__file__).resolve().parents[1]
        source = root / "contact" / "unselected_lineage_behavior_contact.py"
        argv = [
            "/opt/homebrew/opt/python@3.14/bin/python3.14",
            "-m",
            "contact.unselected_lineage_behavior_contact",
            "--smoke-no-contact",
        ]
        self.assertNotIn("--live", argv)
        self.assertNotIn("unselected-lineage-behavior-contact-20260818", " ".join(argv))
        self.assertEqual(Path(sys.executable).resolve(), Path(argv[0]).resolve())
        self.assertEqual(sys.version.split()[0], "3.14.6")
        self.assertEqual(len(source.read_bytes()), 56_940)
        self.assertEqual(
            sha256_bytes(source.read_bytes()),
            "353dbaf59355a67ca762958c7c760e2ae961af58ccb137bd719a71b33b116c91",
        )
        completed = subprocess.run(argv, cwd=root, capture_output=True, text=True, check=False)
        self.assertEqual(completed.args, argv)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, canonical_json_bytes(SMOKE_RECEIPT).decode() + "\n")
        self.assertEqual(completed.stderr, "")

    def test_existing_evidence_destination_stops_before_preflight_or_transport(self):
        with tempfile.TemporaryDirectory() as existing:
            with patch("contact.unselected_lineage_behavior_contact.collect_provider_receipt") as preflight:
                with patch("contact.unselected_lineage_behavior_contact.DockerInvoker") as transport:
                    with self.assertRaisesRegex(ContactRefusal, "evidence_directory_not_fresh"):
                        main([
                            "--live",
                            "--evidence-dir",
                            existing,
                            "--tokenizer-json",
                            str(Path(existing) / "unused-tokenizer.json"),
                        ])
            preflight.assert_not_called()
            transport.assert_not_called()

    def test_published_manifest_and_independent_witness(self):
        manifest = load_published(MANIFEST_PATH, MANIFEST_LENGTH, MANIFEST_SHA256)
        witness = load_published(WITNESS_PATH, WITNESS_LENGTH, WITNESS_SHA256)
        rebuilt = construct_witness(manifest)
        self.assertEqual(rebuilt, witness)
        self.assertEqual(len(canonical_json_bytes(rebuilt)), WITNESS_LENGTH)
        self.assertEqual(sha256_bytes(canonical_json_bytes(rebuilt)), WITNESS_SHA256)
        self.assertEqual(rebuilt["identifier_count"], 80)

    def test_provider_preflight_uses_only_injected_receipts(self):
        provider = json.loads(Path("evidence/executable-prediction-revision-contact-20260818/provider.json").read_text())
        inspection = provider["parsed_inspection"]
        by_command = {
            ("docker", "model", "version"): provider["version"],
            ("docker", "model", "status"): provider["status"],
            ("docker", "model", "list"): provider["inventory"],
            ("docker", "model", "inspect", "ai/qwen3:14B-Q6_K"): provider["inspection"],
            ("docker", "version", "--format", "{{json .}}"): provider["docker_version"],
        }

        def commands(command):
            return by_command[command]

        receipt = collect_provider_receipt(commands, lambda: {"status": 200, "url": "fixture"})
        self.assertTrue(receipt["valid"], receipt["refusals"])
        self.assertEqual(receipt["inspection"]["id"], inspection["id"])

        def drifted(command):
            value = dict(by_command[command])
            if command == ("docker", "model", "status"):
                value["stdout"] = "llama.cpp wrong-build (sha256:wrong)"
            return value
        self.assertFalse(collect_provider_receipt(drifted, lambda: {"status": 200})["valid"])

    def test_prompt_settings_and_schedule_bindings(self):
        self.assertEqual(len(ACTION_SYSTEM.encode()), 713)
        self.assertEqual(sha256_bytes(ACTION_SYSTEM.encode()), "f9f260f444f1807431e44b5688f925f899d0b6447bcefc8593ab10a7b8986095")
        self.assertEqual(len(AUTHORSHIP_SYSTEM.encode()), 259)
        self.assertEqual(sha256_bytes(AUTHORSHIP_SYSTEM.encode()), "8ded646c7f9230bebb75355123158be5f9b0be0df8b9ceed702320191aa70739")
        self.assertEqual(ACTION_SETTINGS["max_tokens"], 32)
        self.assertEqual(ACTION_SETTINGS["response_format"], {"type": "json_object"})
        self.assertNotIn("response_format", AUTHORSHIP_SETTINGS)
        self.assertEqual(AUTHORSHIP_SETTINGS["max_tokens"], 256)
        manifest = load_published(MANIFEST_PATH, MANIFEST_LENGTH, MANIFEST_SHA256)
        rows = later_coordinates(manifest)
        self.assertEqual((len(rows), rows[0][0], rows[-1][0]), (96, 14, 109))
        self.assertEqual(len({(b["block"], branch, case["coordinate"]) for _, b, branch, case in rows}), 96)
        packet = run_packet(FakeInvoker(), render_auditor=render_auditor())
        self.assertTrue(all(row["render_audit"]["prompt_tokens"] > 0 for row in packet.calls))
        self.assertTrue(all(row["render_audit"]["bindings"]["tools"] == "omitted" for row in packet.calls))

    def test_action_parser_is_strict_and_mapping_is_three_way(self):
        allowed = ("left", "right", "hold")
        valid = ProviderContent(True, '{"action":"left"}')
        parsed = parse_action(valid, allowed)
        self.assertEqual(parsed, ActionParse(True, "left", None))
        self.assertEqual(proposal_from_content(valid, parsed), ProposalReceipt(True, "left"))
        for raw in ('{}', '{"action":"left"} trailing', '{"action":NaN}', '{"action":"left","extra":1}', '{"action":1}', '{"action":"left","action":"right"}', '```json\n{"action":"left"}\n```', 'left'):
            receipt = ProviderContent(True, raw)
            parsed = parse_action(receipt, allowed)
            self.assertFalse(parsed.valid)
            self.assertEqual(proposal_from_content(receipt, parsed), ProposalReceipt(True, raw))
        unavailable = ProviderContent(False, "")
        self.assertEqual(proposal_from_content(unavailable, parse_action(unavailable, allowed)), ProposalReceipt(False, ""))
        unlisted = ProviderContent(True, '{"action":"foreign"}')
        self.assertEqual(proposal_from_content(unlisted, parse_action(unlisted, allowed)), ProposalReceipt(True, "foreign"))
        empty = ProviderContent(True, "")
        self.assertEqual(proposal_from_content(empty, parse_action(empty, allowed)), ProposalReceipt(True, ""))

    def test_provider_content_classes_are_total(self):
        self.assertEqual(provider_content({}, 200), ProviderContent(False, ""))
        self.assertEqual(provider_content({"choices": [{"message": {"reasoning_content": "only"}}]}, 200), ProviderContent(False, ""))
        self.assertEqual(provider_content({"choices": [{"message": {"content": ""}}]}, 200), ProviderContent(True, ""))
        self.assertEqual(provider_content({"choices": [{"message": {"content": "x"}}]}, 500), ProviderContent(False, ""))

    def test_parse_invalid_allowed_raw_is_still_applied(self):
        manifest = load_published(MANIFEST_PATH, MANIFEST_LENGTH, MANIFEST_SHA256)
        block = manifest["blocks"][0]
        state = public_state(block["acquisition"]["public_device"])
        raw = state.controls[0]
        receipt = ProviderContent(True, raw)
        parsed = parse_action(receipt, (*state.controls, "hold"))
        proposal = proposal_from_content(receipt, parsed)
        result = apply_committed_action(state, profile(block), proposal)
        self.assertFalse(parsed.valid)
        self.assertEqual(proposal.content, raw)
        self.assertEqual(result.status, "applied")

    def test_parse_invalid_allowed_raw_is_environment_valid_but_not_correct_score(self):
        def bare_allowed(call, attempt):
            request = json.loads(call.envelope["messages"][1]["content"].split("\n")[1])
            content = request["device"]["allowed_actions"][0]
            envelope = {"choices": [{"message": {"content": content}}]}
            return ProviderAttempt(call.request_body, canonical_json_bytes(envelope), envelope, 200)
        packet = run_packet(FakeInvoker({14: bare_allowed}))
        row = next(value for value in packet.later if value["call"].index == 14)
        self.assertFalse(row["interface_valid"])
        self.assertTrue(row["environment_valid"])
        self.assertFalse(row["correct_action"])

    def test_authorship_differs_only_at_external_result(self):
        manifest = load_published(MANIFEST_PATH, MANIFEST_LENGTH, MANIFEST_SHA256)
        block = manifest["blocks"][0]
        state = public_state(block["acquisition"]["public_device"])
        proposal = ProposalReceipt(True, state.controls[0])
        result = apply_committed_action(state, profile(block), proposal)
        exposed = authorship_material(state, proposal, result, True)
        withheld = authorship_material(state, proposal, result, False)
        self.assertEqual(set(exposed), set(withheld))
        for key in set(exposed) - {"external_result"}:
            self.assertEqual(exposed[key], withheld[key])
        self.assertNotEqual(authorship_user(exposed), authorship_user(withheld))

    def test_full_fake_packet_has_complete_denominators_and_identity(self):
        fake = FakeInvoker()
        packet = run_packet(fake)
        self.assertEqual(len(packet.calls), 109)
        self.assertEqual(len(packet.later), 96)
        self.assertEqual(packet.report["physical_attempts"], 109)
        self.assertEqual(packet.report["reserved_completion_tokens"], 5280)
        self.assertIsNone(packet.report["formation_verdict"])
        self.assertIsNone(packet.report["validation_verdict"])
        for branch in packet.report["branches"].values():
            for role in branch.values():
                self.assertEqual(role["assigned"], 4)
        by_key = {(row["block"], row["case"], row["branch"]): row for row in packet.later}
        for block, case, _ in {(row["block"], row["case"], row["branch"]) for row in packet.later}:
            no = by_key[(block, case, NO_PERSISTENCE)]
            ablation = by_key[(block, case, ABLATION)]
            self.assertEqual(no["call"].request_body, ablation["call"].request_body)
            self.assertIs(ablation["hidden_intermediate"], packet.intermediates[(block, RESULT_EXPOSED)])
        self.assertEqual(len(packet.action_receipts), 101)
        self.assertEqual(len(packet.report["paired_facts"]), 96)
        self.assertEqual(len(packet.report["request_audit"]["later"]), 16)
        self.assertTrue(all(row["no_persistence_ablation_request_equal"] for row in packet.report["request_audit"]["later"]))
        self.assertEqual(len(packet.report["request_audit"]["authorship"]), 4)

    def test_all_six_foregrounds_and_intermediate_diagnostics_are_retained(self):
        manifest = load_published(MANIFEST_PATH, MANIFEST_LENGTH, MANIFEST_SHA256)
        control = manifest["blocks"][0]["acquisition"]["public_device"]["allowed_actions"][0]
        def copied(call, attempt):
            envelope = {"choices": [{"message": {"content": f"{control} applied"}}], "usage": {"completion_tokens": 2}}
            return ProviderAttempt(call.request_body, canonical_json_bytes(envelope), envelope, 200)
        packet = run_packet(FakeInvoker({6: copied, 7: copied}), render_auditor=render_auditor())
        intermediate = packet.intermediates[("live-block-0", RESULT_EXPOSED)]
        self.assertIn(control, intermediate.copied_acquisition_strings)
        self.assertIn("applied", intermediate.copied_result_strings)
        self.assertEqual(intermediate.byte_length, len(intermediate.content.encode()))
        audit = next(row for row in packet.report["request_audit"]["later"] if row["block"] == "live-block-0")
        self.assertEqual(set(audit["branches"]), {"no_persistence", "raw_persistence", "result_withheld_authorship", "result_exposed_authorship", "ablation", "static_instruction"})
        for branch, values in audit["branches"].items():
            row = next(item for item in packet.later if item["block"] == audit["block"] and item["case"] == audit["case"] and item["branch"] == branch)
            self.assertEqual(values["foreground_sha256"], sha256_bytes(row["delivered"].encode()))

    def test_all_six_paths_bind_exact_delivered_and_hidden_material(self):
        packet = run_packet(FakeInvoker())
        blocks = {block["block"]: block for block in packet.manifest["blocks"]}
        for row in packet.later:
            block = blocks[row["block"]]
            withheld = packet.intermediates[(row["block"], RESULT_WITHHELD)]
            exposed = packet.intermediates[(row["block"], RESULT_EXPOSED)]
            if row["branch"] == NO_PERSISTENCE:
                self.assertEqual(row["delivered"], "")
                self.assertIsNone(row["hidden_intermediate"])
            elif row["branch"] == RAW_PERSISTENCE:
                state = public_state(block["acquisition"]["public_device"])
                proposal = ProposalReceipt(True, state.controls[0])
                self.assertEqual(
                    row["delivered"],
                    raw_foreground(state, proposal, packet.acquisition_results[row["block"]]),
                )
                self.assertIsNone(row["hidden_intermediate"])
            elif row["branch"] == RESULT_WITHHELD:
                self.assertEqual(row["delivered"], withheld.content if withheld.available else "")
                self.assertIs(row["hidden_intermediate"], withheld)
            elif row["branch"] == RESULT_EXPOSED:
                self.assertEqual(row["delivered"], exposed.content if exposed.available else "")
                self.assertIs(row["hidden_intermediate"], exposed)
            elif row["branch"] == ABLATION:
                self.assertEqual(row["delivered"], "")
                self.assertIs(row["hidden_intermediate"], exposed)
            elif row["branch"] == STATIC_INSTRUCTION:
                self.assertEqual(row["delivered"], static_lesson(block))
                self.assertIsNone(row["hidden_intermediate"])
            else:
                self.fail(f"unexpected branch: {row['branch']}")

    def test_render_refusal_occurs_before_any_provider_transport(self):
        fake = FakeInvoker()
        auditor = render_auditor()
        with patch(
            "contact.unselected_lineage_behavior_contact.render_chat",
            side_effect=ContactRefusal("template_renderer_implementation_mismatch"),
        ):
            with self.assertRaisesRegex(ContactRefusal, "template_renderer_implementation_mismatch"):
                run_packet(fake, render_auditor=auditor)
        self.assertEqual(fake.seen, [])

    def test_disposable_invalid_stops_before_acquisition(self):
        def invalid(call, attempt):
            envelope = {"choices": [{"message": {"content": "not-json"}}]}
            return ProviderAttempt(call.request_body, canonical_json_bytes(envelope), envelope, 200)
        fake = FakeInvoker({1: invalid})
        packet = run_packet(fake)
        self.assertEqual(len(packet.calls), 1)
        self.assertEqual([call.index for call, _ in fake.seen], [1])
        self.assertTrue(packet.report["interface_stop"])

        def unavailable_response(call, attempt):
            return ProviderAttempt(call.request_body, b"{}", {}, 200)
        unavailable = run_packet(FakeInvoker({1: unavailable_response}))
        self.assertTrue(unavailable.report["interface_stop"])

        def unlisted(call, attempt):
            envelope = {"choices": [{"message": {"content": '{"action":"foreign"}'}}]}
            return ProviderAttempt(call.request_body, canonical_json_bytes(envelope), envelope, 200)
        self.assertTrue(run_packet(FakeInvoker({1: unlisted})).report["interface_stop"])

    def test_pre_response_retry_is_bounded_and_retained(self):
        def failure(call, attempt):
            return ProviderAttempt(call.request_body, b"", {}, None, "timeout", True)
        fake = FakeInvoker({(2, 1): failure})
        packet = run_packet(fake)
        self.assertEqual(packet.report["physical_attempts"], 110)
        self.assertEqual(packet.report["retries"], 1)
        attempts = [row for row in packet.attempts if row["invocation"] == "iv002"]
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[1]["retry_of"], 1)

    def test_global_retry_limit_and_http_failures_do_not_change_schedule(self):
        def transport(call, attempt):
            return ProviderAttempt(call.request_body, b"", {}, None, "timeout", True)
        def rate_limit(call, attempt):
            return ProviderAttempt(call.request_body, b'{"error":"rate"}', {"error": "rate"}, 429, "http_429")
        fake = FakeInvoker({(2, 1): transport, (3, 1): transport, (4, 1): transport, (5, 1): transport, 14: rate_limit})
        packet = run_packet(fake)
        self.assertEqual(packet.report["retries"], 3)
        self.assertEqual(packet.report["physical_attempts"], 112)
        self.assertEqual(len(packet.calls), 109)
        self.assertEqual(len([row for row in packet.attempts if row["invocation"] == "iv005"]), 1)
        self.assertEqual(len([row for row in packet.attempts if row["invocation"] == "iv014"]), 1)

    def test_physical_exhaustion_preserves_all_assignments(self):
        packet = run_packet(FakeInvoker(), physical_ceiling=5)
        self.assertEqual(packet.report["physical_attempts"], 5)
        self.assertEqual(len(packet.calls), 109)
        self.assertEqual(len(packet.later), 96)
        self.assertEqual(packet.report["assigned"], 96)
        self.assertEqual(sum(
            role["provider_content_available"]
            for branch in packet.report["branches"].values()
            for role in branch.values()
        ), 0)

    def test_retry_at_last_physical_slot_finalizes_and_replays(self):
        def timeout(call, attempt):
            return ProviderAttempt(call.request_body, b"", {}, None, "timeout", True)
        auditor = render_auditor()
        packet = run_packet(FakeInvoker({5: timeout}), physical_ceiling=5, render_auditor=auditor)
        self.assertEqual(packet.report["physical_attempts"], 5)
        self.assertEqual(len([row for row in packet.attempts if row["invocation"] == "iv005"]), 1)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "evidence"
            EvidenceWriter(directory).write(packet, physical_ceiling=5)
            self.assertEqual(replay_evidence(directory, auditor).report, packet.report)

    def test_fake_packet_never_uses_live_http(self):
        with patch("contact.unselected_lineage_behavior_contact.urlopen", side_effect=AssertionError("live_http_forbidden")):
            packet = run_packet(FakeInvoker())
        self.assertEqual(len(packet.calls), 109)

    def test_unavailable_acquisition_and_authorship_continue(self):
        def unavailable(call, attempt):
            return ProviderAttempt(call.request_body, b"{}", {}, 200)
        fake = FakeInvoker({2: unavailable, 6: unavailable, 7: unavailable})
        packet = run_packet(fake)
        self.assertEqual(len(packet.calls), 109)
        self.assertEqual(packet.acquisition_results["live-block-0"].status, "not_applied")
        self.assertFalse(packet.intermediates[("live-block-0", RESULT_WITHHELD)].available)
        self.assertFalse(packet.intermediates[("live-block-0", RESULT_EXPOSED)].available)
        self.assertEqual(len([row for row in packet.later if row["block"] == "live-block-0"]), 24)

    def test_evidence_replay_rebuilds_full_packet_from_raw_attempts(self):
        auditor = render_auditor()
        packet = run_packet(FakeInvoker(), render_auditor=auditor)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "evidence"
            EvidenceWriter(directory).write(packet)
            replayed = replay_evidence(directory, auditor)
            self.assertEqual(replayed.report, packet.report)
            self.assertEqual(len(replayed.later), 96)

    def test_evidence_replay_rejects_derived_and_raw_tampering(self):
        auditor = render_auditor()
        packet = run_packet(FakeInvoker(), render_auditor=auditor)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "evidence"
            EvidenceWriter(directory).write(packet)
            packet_path = directory / "packet.json"
            stored = json.loads(packet_path.read_text())
            stored["projection"]["report"]["assigned"] = 95
            packet_path.write_text(json.dumps(stored, indent=2, sort_keys=True) + "\n")
            with self.assertRaisesRegex(ContactRefusal, "integrity_projection_mismatch"):
                replay_evidence(directory, auditor)

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "evidence"
            EvidenceWriter(directory).write(packet)
            response = next((directory / "attempts").glob("*.response.bin"))
            response.write_bytes(b"{}")
            with self.assertRaises(ContactRefusal):
                replay_evidence(directory, auditor)


if __name__ == "__main__":
    unittest.main()
