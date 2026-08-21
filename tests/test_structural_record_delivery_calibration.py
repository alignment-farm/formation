import json

from contact import structural_record_delivery_calibration as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 7, "completion_tokens": 3},
    }).encode()


def fake_transport(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    device = record["device"]
    case = next(
        case
        for lineage in subject.LINEAGE_DATA.values()
        for case in lineage.cases.values()
        if case.state.device == device["device"]
    )
    material = record["retained_material"]
    action = case.state.controls[0]
    first_increases = None
    if material:
        if material.startswith("The first"):
            first_increases = "first displayed control increases" in material
        else:
            parsed = json.loads(material)
            if "instrument_records" in parsed:
                parsed = json.loads(parsed["instrument_records"][0])
                first_increases = (
                    parsed["first_displayed_actuator_effect"] == subject.learned.INCREASES
                )
            else:
                table = parsed.get("effect_table", parsed)
                first_increases = (
                    table["first_displayed_control_effect"] == subject.learned.INCREASES
                )
    if first_increases is not None:
        wants_increase = case.state.target > case.state.position
        action = case.state.controls[0 if wants_increase == first_increases else 1]
    return provider(json.dumps({"action": action}))


def test_frozen_schedule_and_fresh_identities():
    assert subject.PLANNED_LOGICAL_CALLS == 192
    assert subject.PHYSICAL_CALL_CEILING == 200
    assert len(subject.schedule()) == 192
    old_families = {
        later.state.controller_family
        for lineage in subject.learned.LINEAGE_DATA.values()
        for later in lineage.cases.values()
    }
    assert all(
        case.state.controller_family not in old_families
        for lineage in subject.LINEAGE_DATA.values()
        for case in lineage.cases.values()
    )
    case = subject.LINEAGE_DATA[subject.LINEAGES[0]].cases["a_up"]
    materials = {
        condition: subject.material_for(condition, case)
        for condition in subject.CONDITIONS
    }
    assert len(set(materials.values())) == len(subject.CONDITIONS)


def test_fake_delivery_calibration_finds_all_forms():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 192
    assert packet["physical_attempts"] == 192
    assert packet["scores"][subject.CURRENT_FAMILY_TABLE] == 32
    assert set(packet["usable_forms"]) == {
        subject.PRIOR_STRING_CONTAINER,
        subject.SCOPED_CONTROL_RECORD,
        subject.DIRECT_EFFECT_TABLE,
        subject.EFFECT_SENTENCE,
    }
    assert packet["calibration_verdict"]["class"] == "usable_form_found"
    assert packet["formation_verdict"] is None


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.base,
        "collect_provider_receipt",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "smoke_no_contact"
    assert output["side_effects_entered"] is False
