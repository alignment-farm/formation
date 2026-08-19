import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from contact.draft_challenge_exploratory_contact import (
    ACTOR_SETTINGS,
    AUTHOR_SETTINGS,
    AUTHORSHIP_RESPONSIBILITY,
    CANDIDATE_SYSTEM,
    CHALLENGE_RESPONSIBILITY,
    CONDITIONS,
    DIRECT_IDENTIFIERS,
    DOCKER_DESKTOP_PLATFORM,
    DraftLiveInvoker,
    INTERFACE_STATE,
    LLAMA_BACKEND_BUILD,
    LLAMA_BACKEND_DIGEST,
    MASS_CONTROL_ALPHABET,
    MAX_COMPLETION_ALLOWANCE,
    MODEL,
    MODEL_DIGEST,
    PHYSICAL_CALL_CEILING,
    PLANNED_LOGICAL_CALLS,
    ROUND_ORDERS,
    SAME_RESPONSE_BUDGET,
    STATIC_RESPONSIBILITY,
    TEMPLATE_RENDERER_IMPLEMENTATION,
    TOKENIZER_SHA256,
    TOKENIZER_IMPLEMENTATION,
    WORLD_G,
    WORLD_H,
    WORLDS,
    LogicalCall,
    MassControl,
    candidate_envelope,
    candidate_user_prompt,
    collect_provider_receipt,
    construct_mass_control,
    direct_calls,
    downstream_calls,
    draft_material,
    main,
    parse_candidate,
    render_chat,
    run_contact,
    same_response_envelope,
    unicode_scalar_string,
)
from contact.exploratory_developmental_contact import (
    INSPECT_TAG,
    InvocationFailure,
    ProviderAttempt,
)
from contact.occurrence_accounting_exploratory_contact import (
    actor_envelope,
    deterministic_restatement,
    govern_candidate as real_govern_candidate,
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


def candidate(name):
    return {
        "change": f"change for {name}",
        "counterevidence": f"counterevidence for {name}",
    }


class ByteTokenCounter:
    implementation = "fake-byte-counter"
    renderer_implementation = "fake-byte-renderer"

    def __call__(self, system, user):
        rendered = (
            f"<|im_start|>system\n{system}<|im_end|>\n"
            f"<|im_start|>user\n{user}<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        return len(rendered.encode("utf-8"))


class FakeInvoker:
    def __init__(
        self,
        *,
        invalid_world=None,
        invalid_interface=False,
        source_content="normal",
        challenge_mode="revision",
        collapsed_conditions=(),
        malformed_condition=None,
        unstable_condition=None,
        carryover=False,
        mass_token_mismatch=False,
        retry_first=False,
        event_log=None,
    ):
        self.invalid_world = invalid_world
        self.invalid_interface = invalid_interface
        self.source_content = source_content
        self.challenge_mode = challenge_mode
        self.collapsed_conditions = set(collapsed_conditions)
        self.malformed_condition = malformed_condition
        self.unstable_condition = unstable_condition
        self.carryover = carryover
        self.mass_token_mismatch = mass_token_mismatch
        self.retry_first = retry_first
        self.event_log = event_log
        self.calls = []

    def __call__(self, call, attempt_index):
        self.calls.append((call, attempt_index))
        if self.event_log is not None:
            self.event_log.append(("invoke", call.call_id))
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

        condition = call.offer_key
        if (
            self.malformed_condition == condition
            and call.repetition == 1
        ):
            return provider_attempt(call, attempt_index, "not-json")

        direct_name = f"{call.world_id}-direct"
        if condition == "direct_candidate":
            if call.repetition == 1:
                if self.source_content == "normal":
                    value = candidate(direct_name)
                    content = json.dumps(value)
                elif self.source_content == "malformed":
                    content = "not-json"
                elif self.source_content == "missing":
                    content = None
                elif self.source_content == "object":
                    content = {"unexpected": "object"}
                elif self.source_content == "surrogate":
                    content = "\ud800"
                else:
                    raise AssertionError(self.source_content)
            else:
                content = json.dumps(candidate(direct_name))
            return provider_attempt(call, attempt_index, content)

        if condition == "draft_withheld":
            name = "challenge" if self.carryover else direct_name
        elif condition == "exact_draft_challenge":
            if self.challenge_mode == "source_match":
                name = direct_name
            elif self.challenge_mode == "withdrawal":
                value = {"change": None, "counterevidence": None}
                return provider_attempt(call, attempt_index, json.dumps(value), 500)
            else:
                name = "challenge"
        elif condition in self.collapsed_conditions:
            name = "challenge"
        else:
            name = condition

        if self.unstable_condition == condition and call.repetition == 2:
            name += "-unstable"
        value = candidate(name)
        if call.same_response:
            content = json.dumps({"draft": candidate("nested-draft"), "final": value})
        else:
            content = json.dumps(value)
        prompt_tokens = 500 if condition in (
            "exact_draft_challenge", "draft_prompt_mass_control"
        ) else 100
        if self.mass_token_mismatch and condition == "draft_prompt_mass_control":
            prompt_tokens = 501
        return provider_attempt(call, attempt_index, content, prompt_tokens)


def available_world_data():
    data = {}
    counter = ByteTokenCounter()
    for world in WORLDS:
        occurrence = acquisition_occurrence(
            world.state, world.profile, world.state.controls
        )
        source = json.dumps(candidate(f"{world.world_id}-direct"))
        material = {"draft_content": source}
        target = counter(
            CANDIDATE_SYSTEM,
            candidate_user_prompt(occurrence, material, "challenge"),
        )
        mass = construct_mass_control(target, occurrence, counter)
        assert mass is not None
        data[world.world_id] = {
            "occurrence": occurrence,
            "controls": world.state.controls,
            "source_content": source,
            "source_material": material,
            "mass_control": mass,
        }
    return data


class DraftChallengeExploratoryContactTests(unittest.TestCase):
    def run_fake(self, fake=None, token_counter=None):
        fake = fake or FakeInvoker()
        token_counter = ByteTokenCounter() if token_counter is None else token_counter
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        evidence = Path(temporary.name) / "evidence"
        summary = run_contact(fake, evidence, {"valid": True}, token_counter)
        return fake, evidence, summary

    def test_model_worlds_settings_and_budget_arithmetic_are_frozen(self):
        self.assertEqual(MODEL, "ai/qwen3:14B-Q6_K")
        self.assertEqual(
            MODEL_DIGEST,
            "sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219",
        )
        self.assertEqual((PLANNED_LOGICAL_CALLS, PHYSICAL_CALL_CEILING), (39, 42))
        self.assertEqual(SAME_RESPONSE_BUDGET, 512)
        self.assertEqual(MAX_COMPLETION_ALLOWANCE, 3 * 128 + 32 * 256 + 4 * 512)
        self.assertEqual(AUTHOR_SETTINGS["max_tokens"], 256)
        self.assertEqual(ACTOR_SETTINGS["max_tokens"], 128)
        self.assertEqual(AUTHOR_SETTINGS["response_format"], {"type": "json_object"})
        expected = {
            "world-g": ("cd32522fbc89d0cc", "fde26f170afcc3ae", "ccdabc1e1f6ca491", ("7e81cf4ce9afe7ad", "183609a9f5e6b701"), 0),
            "world-h": ("04a6549a17c2f498", "e52fe06ac648cd96", "b1a356711b7c0edf", ("aa94f3ae24c6630b", "a3dd902b2fe11658"), 1),
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
        self.assertEqual(INTERFACE_STATE.device, "764226e12f57f878")

    def test_actor_and_candidate_prompts_use_exact_null_and_hide_harness_labels(self):
        for state, count in ((INTERFACE_STATE, 1), (WORLD_G.state, 2), (WORLD_H.state, 2)):
            user = actor_envelope(state, count)["messages"][1]["content"]
            self.assertIn(offer_envelope(None).decode("utf-8"), user)
            self.assertTrue(user.endswith("/no_think"))
        occurrence = acquisition_occurrence(
            WORLD_G.state, WORLD_G.profile, WORLD_G.state.controls
        )
        direct = candidate_envelope(occurrence, None)
        direct_user = direct["messages"][1]["content"]
        self.assertIn("AUTHORSHIP RESPONSIBILITY\n" + AUTHORSHIP_RESPONSIBILITY, direct_user)
        self.assertIn('{"material":null}', direct_user)
        challenge = candidate_envelope(
            occurrence, {"draft_content": "awkward"}, "challenge"
        )["messages"][1]["content"]
        static = candidate_envelope(occurrence, None, "static")["messages"][1]["content"]
        self.assertIn(CHALLENGE_RESPONSIBILITY, challenge)
        self.assertIn(STATIC_RESPONSIBILITY, static)
        for forbidden in ("world-g", "exact_draft_challenge", "governor", "round-1"):
            self.assertNotIn(forbidden, direct_user)
            self.assertNotIn(forbidden, challenge)
        self.assertTrue(challenge.endswith("/no_think"))

    def test_candidate_parsers_are_strict_and_nested_order_is_observable(self):
        self.assertEqual(
            parse_candidate('{"change":"c","counterevidence":"e"}').candidate,
            {"change": "c", "counterevidence": "e"},
        )
        self.assertEqual(
            parse_candidate('{"change":null,"counterevidence":null}').candidate,
            {"change": None, "counterevidence": None},
        )
        for bad in (
            '{"change":"c","change":"d","counterevidence":"e"}',
            '{"change":NaN,"counterevidence":"e"}',
            '{"change":"c","counterevidence":"e","extra":1}',
            "null",
            "",
        ):
            self.assertIsNone(parse_candidate(bad).candidate)
        good = '{"draft":{"change":"d","counterevidence":"de"},"final":{"change":"f","counterevidence":"fe"}}'
        parsed = parse_candidate(good, same_response=True)
        self.assertEqual(parsed.candidate, {"change": "f", "counterevidence": "fe"})
        self.assertEqual(parsed.account, '{"change":"d","counterevidence":"de"}')
        wrong_order = '{"final":{"change":"f","counterevidence":"fe"},"draft":{"change":"d","counterevidence":"de"}}'
        self.assertEqual(
            parse_candidate(wrong_order, same_response=True).refusal,
            "invalid_same_response_key_order",
        )

    def test_source_material_keeps_every_scalar_string_and_rejects_other_values(self):
        for value in ("", "not-json", "é\nawkward", "{}"):
            self.assertTrue(unicode_scalar_string(value))
            self.assertEqual(draft_material(value), {"draft_content": value})
        for value in (None, {"x": 1}, "\ud800", "\udfff"):
            self.assertFalse(unicode_scalar_string(value))
            self.assertIsNone(draft_material(value))

    def test_renderer_matches_frozen_no_tools_non_thinking_template_branch(self):
        template = """{%- if tools %}TOOLS{% else %}{%- if messages[0].role == 'system' %}{{- '<|im_start|>system\\n' + messages[0].content + '<|im_end|>\\n' }}{%- endif %}{%- endif %}{%- for message in messages %}{%- if message.role == 'user' %}{{- '<|im_start|>user\\n' + message.content + '<|im_end|>\\n' }}{%- endif %}{%- endfor %}{%- if add_generation_prompt %}{{- '<|im_start|>assistant\\n' }}{%- if enable_thinking is defined and enable_thinking is false %}THINKING-DISABLED{%- endif %}{%- endif %}"""
        try:
            rendered = render_chat(template, "SYSTEM", "USER")
        except ValueError as error:
            if str(error) == "jinja2_package_unavailable":
                self.skipTest("frozen renderer dependency is isolated in the live venv")
            raise
        self.assertEqual(
            rendered,
            "<|im_start|>system\nSYSTEM<|im_end|>\n"
            "<|im_start|>user\nUSER<|im_end|>\n"
            "<|im_start|>assistant\n",
        )
        self.assertNotIn("<tools>", rendered)
        self.assertNotIn("<think>", rendered)

    def test_mass_control_is_deterministic_first_exact_prefix_and_source_blind(self):
        occurrence = acquisition_occurrence(
            WORLD_G.state, WORLD_G.profile, WORLD_G.state.controls
        )
        counter = ByteTokenCounter()
        source = json.dumps(candidate("world-g-direct"))
        target = counter(
            CANDIDATE_SYSTEM,
            candidate_user_prompt(
                occurrence, {"draft_content": source}, "challenge"
            ),
        )
        first = construct_mass_control(target, occurrence, counter)
        second = construct_mass_control(target, occurrence, counter)
        self.assertEqual(first, second)
        self.assertIsNotNone(first)
        self.assertEqual(first.target_prompt_tokens, first.control_prompt_tokens)
        self.assertTrue(set(first.value) <= set(MASS_CONTROL_ALPHABET))
        self.assertFalse(set(first.value) & set("0123456789abcdef"))
        parameters = tuple(inspect.signature(construct_mass_control).parameters)
        self.assertEqual(parameters, ("target_prompt_tokens", "occurrence", "token_counter"))
        for length in range(first.prefix_length):
            user = candidate_user_prompt(
                occurrence, {"draft_content": first.value[:length]}, "challenge"
            )
            self.assertNotEqual(counter(CANDIDATE_SYSTEM, user), target)

    def test_schedule_freezes_direct_slots_round_order_lineage_and_identity(self):
        data = available_world_data()
        direct = direct_calls(data)
        self.assertEqual(
            [(call.logical_index, call.call_id) for call in direct],
            [
                (4, "candidate-g-direct-1"),
                (5, "candidate-h-direct-1"),
                (6, "candidate-g-direct-2"),
                (7, "candidate-h-direct-2"),
            ],
        )
        downstream = downstream_calls(data)
        self.assertEqual((len(downstream), downstream[0].logical_index, downstream[-1].logical_index), (32, 8, 39))
        for round_number in (1, 2):
            for world in WORLDS:
                actual = [
                    call.offer_key
                    for call in downstream
                    if call.repetition == round_number and call.world_id == world.world_id
                ]
                aliases = ROUND_ORDERS[(round_number, world.world_id)]
                expected = [
                    {
                        "withheld": "draft_withheld",
                        "replay": "exact_draft_replay",
                        "static": "static_challenge_withheld_draft",
                        "challenge": "exact_draft_challenge",
                        "same response": "same_response_draft_challenge",
                        "repeated": "occurrence_repeated",
                        "restatement": "deterministic_restatement",
                        "mass": "draft_prompt_mass_control",
                    }[alias]
                    for alias in aliases
                ]
                self.assertEqual(actual, expected)
        for world in WORLDS:
            world_direct = [call for call in direct if call.world_id == world.world_id]
            withheld = [
                call for call in downstream
                if call.world_id == world.world_id and call.offer_key == "draft_withheld"
            ]
            self.assertEqual(
                {call.request_body for call in world_direct + withheld},
                {world_direct[0].request_body},
            )
            draft_group = [call for call in downstream if call.world_id == world.world_id and call.draft_receipt]
            self.assertTrue(all(call.draft_receipt == DIRECT_IDENTIFIERS[world.world_id][0] for call in draft_group))
            parents = {call.offer_key for call in draft_group if call.draft_is_request_parent}
            self.assertEqual(parents, {"exact_draft_replay", "exact_draft_challenge"})

    def test_full_fake_contact_completes_with_delayed_governance_and_weak_labels(self):
        events = []
        fake = FakeInvoker(event_log=events)

        def governed(parsed, occurrence, controls):
            events.append(("govern", None))
            return real_govern_candidate(parsed, occurrence, controls)

        with patch(
            "contact.draft_challenge_exploratory_contact.govern_candidate",
            side_effect=governed,
        ):
            fake, evidence, summary = self.run_fake(fake)
        self.assertEqual(summary["contact_state"], "completed")
        self.assertEqual(summary["completed_logical_calls"], 39)
        self.assertEqual(summary["physical_attempts"], 39)
        self.assertTrue(summary["governance_applied_after_authorship"])
        first_govern = next(index for index, event in enumerate(events) if event[0] == "govern")
        self.assertTrue(all(event[0] == "invoke" for event in events[:first_govern]))
        self.assertEqual(sum(event[0] == "invoke" for event in events), 39)
        self.assertTrue(summary["integrity"]["valid"])
        self.assertEqual(summary["integrity"]["attempts_checked"], 39)
        for comparison in summary["world_comparisons"]:
            self.assertEqual(
                comparison["mechanism_label"],
                "draft-challenge-associated exact candidate revision",
            )
            self.assertEqual(comparison["collapse_labels"], [])
            self.assertTrue(comparison["source_candidate_member_of_stable_direct"])
            self.assertTrue(comparison["prompt_mass_comparison_available"])
        self.assertIsNone(summary["formation_verdict"])
        self.assertIsNone(summary["validation_verdict"])
        retained = json.loads((evidence / "world-g-mass-control.json").read_text())
        self.assertIn("value_utf8", retained)
        self.assertEqual(retained["value_utf8_length"], len(retained["value_utf8"].encode()))
        self.assertEqual(retained["tokenizer_implementation"], "fake-byte-counter")
        self.assertEqual(retained["template_renderer_implementation"], "fake-byte-renderer")
        protocol = json.loads((evidence / "protocol.json").read_text())
        self.assertEqual(protocol["tokenizer_implementation"], TOKENIZER_IMPLEMENTATION)
        self.assertEqual(
            protocol["template_renderer_implementation"],
            TEMPLATE_RENDERER_IMPLEMENTATION,
        )

    def test_exact_double_null_is_withdrawal_not_revision(self):
        _, _, summary = self.run_fake(FakeInvoker(challenge_mode="withdrawal"))
        for comparison in summary["world_comparisons"]:
            self.assertEqual(
                comparison["mechanism_label"],
                "draft-challenge-associated exact candidate withdrawal",
            )

    def test_challenge_equal_to_source_reports_match_without_collapse_or_label(self):
        _, _, summary = self.run_fake(FakeInvoker(challenge_mode="source_match"))
        for comparison in summary["world_comparisons"]:
            self.assertTrue(comparison["exact_challenge_source_candidate_match"])
            self.assertEqual(comparison["collapse_labels"], [])
            self.assertIsNone(comparison["mechanism_label"])

    def test_each_exact_control_collapse_is_reported_and_suppresses_label(self):
        collapses = {
            "exact_draft_replay",
            "static_challenge_withheld_draft",
            "same_response_draft_challenge",
            "occurrence_repeated",
            "deterministic_restatement",
            "draft_prompt_mass_control",
        }
        _, _, summary = self.run_fake(FakeInvoker(collapsed_conditions=collapses))
        expected = {
            "draft-priming-equivalent",
            "static-review-equivalent",
            "generated-intermediate-equivalent",
            "repetition-equivalent",
            "restatement-equivalent",
            "prompt-mass-equivalent",
        }
        for comparison in summary["world_comparisons"]:
            self.assertEqual(set(comparison["collapse_labels"]), expected)
            self.assertIsNone(comparison["mechanism_label"])

    def test_malformed_scalar_source_still_enters_all_draft_dependent_requests(self):
        fake, _, summary = self.run_fake(FakeInvoker(source_content="malformed"))
        called = {call.offer_key for call, _ in fake.calls}
        self.assertTrue(
            {"exact_draft_replay", "exact_draft_challenge", "draft_prompt_mass_control"}
            <= called
        )
        for comparison in summary["world_comparisons"]:
            self.assertFalse(comparison["source_candidate_member_of_stable_direct"])
            self.assertIsNone(comparison["mechanism_label"])

    def test_missing_nonstring_and_nonscalar_sources_omit_only_dependent_cells(self):
        for source_content in ("missing", "object", "surrogate"):
            with self.subTest(source_content=source_content):
                fake, evidence, summary = self.run_fake(
                    FakeInvoker(source_content=source_content)
                )
                self.assertEqual(summary["contact_state"], "completed")
                self.assertEqual(summary["completed_logical_calls"], 27)
                called = {call.offer_key for call, _ in fake.calls}
                self.assertFalse(
                    {"exact_draft_replay", "exact_draft_challenge", "draft_prompt_mass_control"}
                    & called
                )
                unaffected = set(CONDITIONS) - {
                    "exact_draft_replay", "exact_draft_challenge", "draft_prompt_mass_control"
                }
                self.assertTrue(unaffected <= called)
                self.assertTrue((evidence / "summary.json").exists())

    def test_instability_carryover_and_prompt_token_mismatch_forbid_label(self):
        cases = (
            FakeInvoker(unstable_condition="exact_draft_challenge"),
            FakeInvoker(carryover=True),
            FakeInvoker(mass_token_mismatch=True),
        )
        for fake in cases:
            with self.subTest(fake=fake):
                _, _, summary = self.run_fake(fake)
                self.assertTrue(
                    all(item["mechanism_label"] is None for item in summary["world_comparisons"])
                )
        _, _, carryover = self.run_fake(FakeInvoker(carryover=True))
        self.assertTrue(
            all(
                item["carryover_pattern_challenge_contrast_invalid"]
                for item in carryover["world_comparisons"]
            )
        )
        _, _, mismatch = self.run_fake(FakeInvoker(mass_token_mismatch=True))
        self.assertTrue(
            all(
                not item["prompt_mass_comparison_available"]
                for item in mismatch["world_comparisons"]
            )
        )

    def test_tokenizer_failure_marks_only_mass_unavailable(self):
        def broken_counter(system, user):
            raise ValueError("fake tokenizer failure")

        fake, _, summary = self.run_fake(FakeInvoker(), token_counter=broken_counter)
        self.assertEqual(summary["contact_state"], "completed")
        self.assertEqual(summary["completed_logical_calls"], 35)
        called = {call.offer_key for call, _ in fake.calls}
        self.assertNotIn("draft_prompt_mass_control", called)
        self.assertIn("exact_draft_challenge", called)

    def test_invalid_acquisition_skips_one_world_and_invalid_interface_stops_packet(self):
        _, _, one_world = self.run_fake(FakeInvoker(invalid_world="world-g"))
        self.assertEqual(one_world["contact_state"], "completed")
        self.assertEqual(one_world["completed_logical_calls"], 21)
        comparisons = {item["world_id"]: item for item in one_world["world_comparisons"]}
        self.assertEqual(comparisons["world-g"]["reason"], "acquisition_occurrence_unavailable")
        self.assertEqual(
            comparisons["world-h"]["mechanism_label"],
            "draft-challenge-associated exact candidate revision",
        )
        _, _, stopped = self.run_fake(FakeInvoker(invalid_interface=True))
        self.assertEqual(stopped["contact_state"], "stopped")
        self.assertEqual(stopped["stop_reason"], "interface_action_unobservable")
        self.assertEqual(stopped["physical_attempts"], 1)

    def test_provider_receipt_retry_and_cli_live_gate_are_frozen(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid = run_contact(
                FakeInvoker(), Path(directory) / "invalid", {"valid": False}, ByteTokenCounter()
            )
        self.assertEqual((invalid["stop_reason"], invalid["physical_attempts"]), ("provider_receipt_invalid", 0))
        _, _, retry = self.run_fake(FakeInvoker(retry_first=True))
        self.assertEqual((retry["contact_state"], retry["physical_attempts"]), ("completed", 40))
        with patch(
            "sys.argv",
            ["runner", "--evidence-dir", "unused", "--tokenizer-json", "unused"],
        ):
            with self.assertRaisesRegex(SystemExit, "live contact requires --live"):
                main()

    def test_live_invoker_preserves_missing_and_nonstring_content_as_evidence(self):
        class Response:
            status = 200

            def __init__(self, body):
                self.body = body

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return self.body

        call = LogicalCall(1, "test", "candidate", {"model": MODEL})
        envelopes = ({"choices": []}, {"choices": [{"message": {"content": {"x": 1}}}]})
        for envelope in envelopes:
            body = json.dumps(envelope).encode()
            with patch(
                "contact.draft_challenge_exploratory_contact.urlopen",
                return_value=Response(body),
            ):
                attempt = DraftLiveInvoker()(call, 1)
            expected = None if envelope["choices"] == [] else {"x": 1}
            self.assertEqual(attempt.content, expected)
            self.assertEqual(attempt.response_body, body)

    def test_provider_receipt_freezes_versions_backend_digest_and_model_artifact(self):
        inspection = {
            "id": MODEL_DIGEST,
            "tags": [INSPECT_TAG],
            "config": {
                "gguf": {
                    "tokenizer.chat_template": "x" * 4100,
                }
            },
        }
        # Replace the synthetic template with bytes matching the frozen constants by
        # patching the hash function only for this receipt plumbing test. The renderer
        # itself is tested independently above.
        records = {
            ("docker", "model", "version"): {"command": [], "returncode": 0, "stdout": "v1.2.6 v1.2.6", "stderr": ""},
            ("docker", "model", "status"): {"command": [], "returncode": 0, "stdout": f"{LLAMA_BACKEND_BUILD} {LLAMA_BACKEND_DIGEST}", "stderr": ""},
            ("docker", "model", "list"): {"command": [], "returncode": 0, "stdout": "qwen3:14B-Q6_K", "stderr": ""},
            ("docker", "model", "inspect", MODEL): {"command": [], "returncode": 0, "stdout": json.dumps(inspection), "stderr": ""},
            ("docker", "version", "--format", "{{json .}}"): {"command": [], "returncode": 0, "stdout": json.dumps({"Server": {"Platform": {"Name": DOCKER_DESKTOP_PLATFORM}}}), "stderr": ""},
        }

        def command(args):
            return records[args]

        real_sha256 = __import__("hashlib").sha256

        class Digest:
            def hexdigest(self):
                return "57f1fd00f0013a2be96aa79b857391f27e23df5b5f847072b524c897e24d0361"

        def selective_sha256(value=b""):
            if value == b"x" * 4100:
                return Digest()
            return real_sha256(value)

        with (
            patch("contact.draft_challenge_exploratory_contact._run_command", side_effect=command),
            patch("contact.draft_challenge_exploratory_contact._endpoint_receipt", return_value={"status": 200}),
            patch("contact.draft_challenge_exploratory_contact._tokenizer_receipt", return_value={"valid": True, "sha256": TOKENIZER_SHA256}),
            patch("contact.draft_challenge_exploratory_contact.hashlib.sha256", side_effect=selective_sha256),
        ):
            receipt = collect_provider_receipt(Path("unused"))
        self.assertTrue(receipt["valid"])
        self.assertTrue(receipt["mass_instrument_available"])
        self.assertEqual(receipt["parsed_inspection"]["id"], MODEL_DIGEST)


if __name__ == "__main__":
    unittest.main()
