import json

from contact import accumulated_table_container_diagnostic as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 9, "completion_tokens": 3},
    }).encode()


def fake_transport(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    state = next(
        state
        for lineage in subject.LINEAGE_DATA.values()
        for state in lineage.cases.values()
        if state.device == record["device"]["device"]
    )
    family = record["device"]["controller_family"]
    material = record["retained_material"]
    table = ""
    if material:
        parsed = json.loads(material)
        if "retained_effect_tables" in parsed:
            table = parsed["retained_effect_tables"][0]
        elif "effect_tables_by_controller_family" in parsed:
            table = parsed["effect_tables_by_controller_family"].get(family, "")
        elif parsed.get("controller_family") == family:
            table = material
    second_increases = (
        '"second_displayed_control_effect":"increases_position"' in table
    )
    if second_increases:
        action = state.controls[1] if state.target > state.position else state.controls[0]
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_source_and_frozen_schedule():
    tables = subject.load_source_tables()
    assert all(set(families) == {"a", "b"} for families in tables.values())
    assert subject.PLANNED_LOGICAL_CALLS == 320
    assert subject.PHYSICAL_CALL_CEILING == 328
    assert len(subject.schedule()) == 320
    assert len(set(subject.schedule())) == 320


def test_fake_packet_finds_order_bias_and_keyed_repair(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert packet["container_verdict"]["class"] == "keyed_repairs_order_bias"
    assert packet["logical_calls"] == packet["physical_attempts"] == 320
    assert packet["family_scores"][subject.LIST_AB] == {"a": 32, "b": 0}
    assert packet["family_scores"][subject.LIST_BA] == {"a": 0, "b": 32}
    assert packet["scores"][subject.KEYED] == packet["scores"][subject.GATED] == 64
    assert subject.replay_evidence(evidence_dir) == packet


def test_keyed_material_uses_exact_family_keys():
    tables = subject.load_source_tables()[subject.LINEAGES[0]]
    parsed = json.loads(subject.keyed_material(tables["a"], tables["b"]))
    keyed = parsed["effect_tables_by_controller_family"]
    assert set(keyed) == {
        json.loads(tables["a"])["controller_family"],
        json.loads(tables["b"])["controller_family"],
    }


def test_malformed_output_is_not_engaged(tmp_path):
    packet = subject.execute(lambda body: provider("bad"), tmp_path / "bad")
    assert packet["container_verdict"]["class"] == "not_engaged"
    assert packet["logical_calls"] == 320


def test_smoke_path_makes_no_contact(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 320,
        "side_effects_entered": False,
    }
