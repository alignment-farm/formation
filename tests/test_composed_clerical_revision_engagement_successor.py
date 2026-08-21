import json

from contact import composed_clerical_revision_engagement_successor as subject


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
    for lineage in subject.base_validation.LINEAGE_DATA.values():
        for design in lineage.designs.values():
            if description in {design.source_description, design.later_description}:
                return {"beacon_class": design.beacon, "housing_class": design.housing}
        for case in lineage.post_cases.values():
            if case.description == description:
                return case.scope
    raise AssertionError(description)


def state_for_device(device_id: str):
    for lineage in subject.base_validation.LINEAGE_DATA.values():
        for state in (*lineage.old_sources.values(), *lineage.counter_sources.values()):
            if state.device == device_id:
                return state
        for case in (*lineage.pre_cases.values(), *lineage.post_cases.values()):
            if case.state.device == device_id:
                return case.state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    validation = subject.base_validation
    envelope, user, record = request_record(body)
    if envelope["model"] == validation.learned.INSTRUMENT_MODEL:
        if user.startswith("SENSORY REPORT"):
            selected = "first" if "first displayed" in record["actuator_report"] else "second"
            observed = (
                validation.learned.INCREASES if "rose" in record["gauge_report"]
                else validation.learned.DECREASES if "fell" in record["gauge_report"]
                else "unavailable"
            )
            return provider(json.dumps({
                "observed_actuator": selected,
                "observed_effect": observed,
                "scope": scope_for_description(record["device_report"]),
            }))
        if user.startswith("RECORD REQUEST"):
            transcript = json.loads(record["normalized_sensory_transcript"])
            if transcript["observed_effect"] not in {
                validation.learned.INCREASES,
                validation.learned.DECREASES,
            }:
                return provider("No complete effect account.")
            first_increases = (
                (transcript["observed_actuator"] == "first")
                == (transcript["observed_effect"] == validation.learned.INCREASES)
            )
            first = "increases" if first_increases else "decreases"
            second = "decreases" if first_increases else "increases"
            return provider(
                f"The second displayed control {second} position. "
                f"The first displayed control {first} position."
            )
        if user.startswith("PROSE PARSE REQUEST"):
            parsed = validation.prose_parser.parse_explicit_sentence(
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
    if material.startswith("The first displayed control") and "\n" not in material:
        first_increases = "first displayed control increases" in material
        wants_increase = state.target > state.position
        action = state.controls[0 if wants_increase == first_increases else 1]
    return provider(json.dumps({"action": action}))


def invalid_raw_control_transport(body: bytes):
    envelope, _, record = request_record(body)
    if (
        envelope["model"] == subject.base.MODEL
        and record["retained_material"].startswith('{"raw_counterexperiences"')
        and record["device"]["device"]
        == subject.LINEAGE_DATA["engagement_01"].post_cases["b_down"].state.device
    ):
        return provider(json.dumps({"action": "old-action-not-on-this-device"}))
    return fake_transport(body)


def test_fresh_successor_and_only_engagement_rule_changed():
    specimen = subject.specimen()
    assert subject.LINEAGES == (
        "engagement_01", "engagement_02", "engagement_03", "engagement_04"
    )
    assert specimen["protocol_version"] == subject.PROTOCOL_VERSION
    assert specimen["planned_logical_calls"] == 768
    assert subject.ENGAGEMENT_BRANCHES == (
        subject.base_validation.SUPPLIED,
        subject.base_validation.ADMITTED,
    )


def test_fake_successor_is_supported():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 768
    assert packet["physical_attempts"] == 768
    assert packet["matching_scores"][subject.base_validation.ADMITTED] == 48
    assert packet["validation_verdict"] == {
        "class": "supported",
        "scope": subject.VERDICT_SCOPE,
    }
    assert packet["engagement_invalid_participant_cells"] == []
    assert packet["formation_verdict"] is None


def test_invalid_raw_cell_remains_wrong_without_vetoing_engagement():
    packet = subject.execute(invalid_raw_control_transport)
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["engagement_invalid_participant_cells"] == []
    assert packet["invalid_participant_cells"] == [{
        "branch": subject.base_validation.RAW,
        "case": "b_down",
        "lineage": "engagement_01",
        "invalid": 3,
    }]
    raw_cell = packet["request_distributions"][subject.base_validation.RAW]["b_down"]
    assert raw_cell["assigned"] == 12
    assert raw_cell["invalid_or_unavailable"] == 3
    assert raw_cell["correct_actions"] <= 9


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
