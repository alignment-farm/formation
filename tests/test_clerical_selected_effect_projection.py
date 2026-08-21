import json

from contact import clerical_selected_effect_projection as subject
from contact import learned_clerical_revision_exploration as revision


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 3},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    return envelope, user, record


def fake_transport(body: bytes):
    _, _, record = request_record(body)
    field = f"{record['observed_actuator']}_control_effect"
    effect = record["proposed_effect_record"][field]
    return provider(json.dumps({"claimed_selected_effect": effect}))


def test_frozen_cases_schedule_and_information_separation():
    cases = subject.load_cases()
    assert len(cases) == 16
    assert subject.PLANNED_LOGICAL_CALLS == 48
    assert subject.PHYSICAL_CALL_CEILING == 56
    assert len(subject.schedule(cases)) == 48
    assert {case.observed_actuator for case in cases} == {"first", "second"}
    assert {case.expected_effect for case in cases} == {
        subject.learned.INCREASES,
        subject.learned.DECREASES,
    }
    assert len({case.combination for case in cases}) == 4

    envelope, user, record = request_record(subject.projection_body(cases[0]))
    assert envelope["model"] == subject.learned.INSTRUMENT_MODEL
    assert set(record) == {"observed_actuator", "proposed_effect_record"}
    assert "gauge" not in user
    assert "observed_effect" not in user
    encoded = subject.base.canonical_json_bytes(record).decode()
    for lineage in revision.LINEAGE_DATA.values():
        for case in lineage.post_cases.values():
            assert case.state.device not in encoded
            assert all(control not in encoded for control in case.state.controls)
            assert str(case.state.target) not in encoded


def test_fake_projection_reaches_candidate():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 48
    assert packet["physical_attempts"] == 48
    assert packet["valid_outputs"] == 48
    assert packet["exact_projections"] == 48
    assert all(cell["correct"] == 12 for cell in packet["class_scores"].values())
    assert all(
        cell["correct"] == cell["assigned"]
        for cell in packet["combination_scores"].values()
    )
    assert packet["projection_verdict"]["class"] == "projection_candidate"
    assert packet["formation_verdict"] is None


def test_repeat_requests_are_exact_within_pair():
    packet = subject.execute(fake_transport)
    hashes = {}
    for row in packet["calls"]:
        hashes.setdefault(row["pair_id"], set()).add(row["request_sha256"])
    assert len(hashes) == 16
    assert all(len(items) == 1 for items in hashes.values())


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.learned,
        "collect_provider_receipt",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "smoke_no_contact"
    assert output["side_effects_entered"] is False
