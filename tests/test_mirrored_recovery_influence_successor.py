import json

from contact import mirrored_recovery_influence_successor as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 15, "completion_tokens": 5},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    return envelope, user, json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])


def scope_for_description(description: str):
    if description == subject.VISIBLE_DESIGN.source_description:
        return subject.VISIBLE_SCOPE
    for case in subject.LATER_CASES.values():
        if case.description == description:
            return case.scope
    raise AssertionError(description)


def state_for_device(device_id: str):
    for case in subject.LATER_CASES.values():
        if case.state.device == device_id:
            return case.state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, user, record = request_record(body)
    if envelope["model"] == subject.learned.INSTRUMENT_MODEL:
        if user.startswith("SENSORY REPORT"):
            observed = (
                subject.learned.INCREASES
                if "rose" in record["gauge_report"]
                else subject.learned.DECREASES
            )
            return provider(json.dumps({
                "observed_actuator": "first",
                "observed_effect": observed,
                "scope": scope_for_description(record["device_report"]),
            }))
        if user.startswith("RECORD REQUEST"):
            transcript = json.loads(record["normalized_sensory_transcript"])
            first = (
                "increases"
                if transcript["observed_effect"] == subject.learned.INCREASES
                else "decreases"
            )
            second = "decreases" if first == "increases" else "increases"
            return provider(
                f"The first displayed control {first} position. "
                f"The second displayed control {second} position."
            )
        if user.startswith("PROSE PARSE REQUEST"):
            parsed = subject.prose_parser.parse_explicit_sentence(
                record["explicit_effect_account"]
            )
            return provider(json.dumps(parsed))
        if user.startswith("FIELD PROJECTION REQUEST"):
            field = f"{record['observed_actuator']}_control_effect"
            effect = record["proposed_effect_record"].get(field)
            return provider(json.dumps({"claimed_selected_effect": effect}))
        if user.startswith("NORMALIZATION REQUEST"):
            return provider(json.dumps({
                "scope": scope_for_description(record["current_device_description"]),
            }))
        raise AssertionError(user)

    state = state_for_device(record["device"]["device"])
    material = record["retained_material"]
    action = state.controls[0]
    if "The first displayed control" in material:
        first_increases = "first displayed control increases" in material
        wants_increase = state.target > state.position
        action = state.controls[0 if wants_increase == first_increases else 1]
    return provider(json.dumps({"action": action}))


def test_mirrored_specimen_has_public_identical_later_cases():
    specimen = subject.specimen()
    assert specimen["predecessor_packet_sha256"] == subject.PREDECESSOR_PACKET_SHA256
    assert subject.PLANNED_LOGICAL_CALLS == 324
    assert len(subject.post_schedule()) == 288
    assert len(subject.MATCHING_CASES) == 8
    assert len(subject.UNRELATED_CASES) == 4
    for case in specimen["cases"].values():
        device = case["public_device"]
        assert device == case["public_device"]
        if case["matching"]:
            assert len(set(case["world_expected_actions"].values())) == 2


def test_fake_mirrored_recovery_is_supported():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 324
    assert packet["physical_attempts"] == 324
    assert packet["components"] == {
        "composed_source_admissions": 6,
        "exact_clerk_records": 6,
        "exact_governance_histories": 2,
        "exact_later_assignments": 288,
        "exact_later_normalizations": 12,
        "exact_ordered_sources": 2,
        "exact_selected_effect_projections": 6,
        "exploration_actions_exact": 6,
        "opposite_current_records": True,
        "source_movements_exact": 6,
    }
    assert packet["request_identity"] == {
        "cold_removal_mirror_groups": 36,
        "recovered_supplied_within_world_pairs": 72,
        "unrelated_all_condition_groups": 12,
    }
    assert packet["matching_scores"] == {
        subject.COLD: 24,
        subject.RECOVERED: 48,
        subject.REMOVED: 24,
        subject.SUPPLIED: 48,
    }
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["formation_verdict"] is None


def test_empty_and_guided_request_identities_are_real():
    packet = subject.execute(fake_transport)
    rows = [
        row for row in packet["calls"]
        if row["responsibility"] == "comparison_action"
    ]
    for repeat in range(1, subject.REPEATS + 1):
        for case_name in subject.CASES:
            hashes = {
                row["request_sha256"] for row in rows
                if row["repeat"] == repeat
                and row["case"] == case_name
                and row["branch"] in {subject.COLD, subject.REMOVED}
            }
            assert len(hashes) == 1
    for world in subject.WORLDS:
        for case_name in subject.MATCHING_CASES:
            recovered = {
                row["request_sha256"] for row in rows
                if row["world"] == world
                and row["case"] == case_name
                and row["branch"] == subject.RECOVERED
            }
            supplied = {
                row["request_sha256"] for row in rows
                if row["world"] == world
                and row["case"] == case_name
                and row["branch"] == subject.SUPPLIED
            }
            assert recovered == supplied


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.learned,
        "collect_provider_receipt",
        lambda: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out)["side_effects_entered"] is False
