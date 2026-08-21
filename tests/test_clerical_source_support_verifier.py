import json

from contact import clerical_source_support_verifier as subject
from contact import learned_clerical_revision_exploration as revision


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 3},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    return envelope, user, record


def fake_transport(body: bytes):
    _, _, record = request_record(body)
    report = record["source_sensory_report"]
    proposed = record["proposed_effect_record"]
    if "rose" in report["gauge_report"]:
        observed = subject.learned.INCREASES
    elif "fell" in report["gauge_report"]:
        observed = subject.learned.DECREASES
    else:
        return provider(json.dumps({"source_support": subject.UNSUPPORTED}))
    if "first displayed" in report["actuator_report"]:
        selected = "first_control_effect"
    elif "second displayed" in report["actuator_report"]:
        selected = "second_control_effect"
    else:
        return provider(json.dumps({"source_support": subject.UNSUPPORTED}))
    label = subject.SUPPORTED if proposed[selected] == observed else subject.UNSUPPORTED
    return provider(json.dumps({"source_support": label}))


def test_frozen_pairs_schedule_and_information_separation():
    pairs = subject.load_pairs()
    assert len(pairs) == 16
    assert subject.PLANNED_LOGICAL_CALLS == 48
    assert subject.PHYSICAL_CALL_CEILING == 56
    assert len(subject.schedule(pairs)) == 48
    for pair_class in subject.PAIR_CLASSES:
        rows = [pair for pair in pairs if pair.pair_class == pair_class]
        assert len(rows) == 4
        expected = (
            subject.SUPPORTED
            if pair_class in {"old_supported", "revision_supported"}
            else subject.UNSUPPORTED
        )
        assert {pair.expected_label for pair in rows} == {expected}

    envelope, user, record = request_record(subject.verification_body(pairs[0]))
    assert envelope["model"] == subject.learned.INSTRUMENT_MODEL
    assert set(record) == {"proposed_effect_record", "source_sensory_report"}
    encoded = subject.base.canonical_json_bytes(record).decode()
    for lineage in revision.LINEAGE_DATA.values():
        for case in lineage.post_cases.values():
            assert case.state.device not in encoded
            assert all(control not in encoded for control in case.state.controls)
            assert str(case.state.target) not in encoded
    assert "expected_label" not in user
    assert "pair_class" not in user


def test_fake_verifier_reaches_candidate():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 48
    assert packet["physical_attempts"] == 48
    assert packet["valid_outputs"] == 48
    assert all(
        cell["correct"] == 12 for cell in packet["distributions"].values()
    )
    assert packet["distributions"]["stale_contradicted"]["labels"] == {
        subject.UNSUPPORTED: 12
    }
    assert packet["distributions"]["missing_movement"]["labels"] == {
        subject.UNSUPPORTED: 12
    }
    assert packet["verifier_verdict"]["class"] == "verifier_candidate"
    assert packet["formation_verdict"] is None


def test_repeat_requests_are_exact_within_each_pair():
    packet = subject.execute(fake_transport)
    hashes = {}
    for row in packet["calls"]:
        hashes.setdefault(row["pair_id"], set()).add(row["request_sha256"])
    assert len(hashes) == 16
    assert all(len(values) == 1 for values in hashes.values())


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
