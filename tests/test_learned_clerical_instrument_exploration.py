import json

from contact import learned_clerical_instrument_exploration as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 11, "completion_tokens": 5},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    return envelope, json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])


def design_for_source_description(description: str):
    return next(
        design
        for designs in subject.DESIGN_SETS
        for design in designs.values()
        if design.source_description == description
    )


def scope_for_description(description: str):
    for lineage in subject.LINEAGE_DATA.values():
        for design in lineage.designs.values():
            if description in {design.source_description, design.later_description}:
                return {
                    "beacon_class": design.beacon,
                    "housing_class": design.housing,
                }
        for case in lineage.cases.values():
            if case.description == description:
                for housing in (
                    "faceted", "arched", "ribbed", "tapered", "smooth", "dimpled"
                ):
                    if housing in description:
                        break
                for beacon in ("violet", "amber", "cyan", "white", "green", "red"):
                    if beacon in description:
                        break
                return {"beacon_class": beacon, "housing_class": housing}
    raise AssertionError(description)


def state_for_device(device_id: str):
    for lineage in subject.LINEAGE_DATA.values():
        for position in subject.DESIGN_POSITIONS:
            state = lineage.acquisitions[position]
            if state.device == device_id:
                return state
        for later in lineage.cases.values():
            if later.state.device == device_id:
                return later.state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, record = request_record(body)
    user = envelope["messages"][1]["content"]
    if envelope["model"] == subject.INSTRUMENT_MODEL:
        if user.startswith("SENSORY REPORT"):
            design = design_for_source_description(record["device_report"])
            return provider(subject.static_record(design))
        current_scope = scope_for_description(record["current_device_description"])
        selected = [
            row["record_id"]
            for row in record["record_scope_catalog"]
            if row["scope"] == current_scope
        ]
        return provider(json.dumps({"applicable_record_ids": selected}))

    device = record["device"]
    state = state_for_device(device["device"])
    material = record["retained_material"]
    action = state.controls[0]
    if material:
        parsed_material = json.loads(material)
        instrument_records = parsed_material.get("instrument_records", [])
        if len(instrument_records) == 1:
            parsed_record = subject.parse_record(instrument_records[0])
            current_scope = scope_for_description(device["surface_description"])
            if parsed_record is not None and parsed_record["scope"] == current_scope:
                wants_increase = state.target > state.position
                first_increases = (
                    parsed_record["first_displayed_actuator_effect"] == subject.INCREASES
                )
                choose_first = wants_increase == first_increases
                action = state.controls[0 if choose_first else 1]
    return provider(json.dumps({"action": action}))


def test_frozen_counts_and_information_separation():
    assert subject.PLANNED_LOGICAL_CALLS == 368
    assert subject.PHYSICAL_CALL_CEILING == 376
    assert len(subject.classification_schedule()) == 24
    assert len(subject.later_schedule()) == 336

    for lineage in subject.LINEAGE_DATA.values():
        source_families = {
            state.controller_family for state in lineage.acquisitions.values()
        }
        assert all(
            later.state.controller_family not in source_families
            for later in lineage.cases.values()
        )

        design = lineage.designs["a"]
        report = {
            "actuator_report": "The first displayed actuator was engaged.",
            "device_report": design.source_description,
            "gauge_report": "The position gauge rose by one mark.",
        }
        encoder_envelope, encoder_record = request_record(subject.encoder_body(report))
        assert encoder_envelope["model"] == subject.INSTRUMENT_MODEL
        assert encoder_record == report
        forbidden = {
            lineage.acquisitions["a"].controller_family,
            lineage.acquisitions["a"].device,
            *lineage.acquisitions["a"].controls,
            str(lineage.acquisitions["a"].target),
        }
        encoder_bytes = subject.base.canonical_json_bytes(encoder_record).decode()
        assert all(value not in encoder_bytes for value in forbidden)

        rows = subject.catalog(
            lineage.record_ids,
            {position: subject.static_record(lineage.designs[position])
             for position in subject.DESIGN_POSITIONS},
        )
        classifier_envelope, classifier_record = request_record(
            subject.classifier_body(lineage.cases["a_up"].description, rows)
        )
        assert classifier_envelope["model"] == subject.INSTRUMENT_MODEL
        classifier_bytes = subject.base.canonical_json_bytes(classifier_record).decode()
        assert subject.INCREASES not in classifier_bytes
        assert subject.DECREASES not in classifier_bytes
        later = lineage.cases["a_up"].state
        assert later.device not in classifier_bytes
        assert all(control not in classifier_bytes for control in later.controls)
        assert str(later.target) not in classifier_bytes


def test_fake_pipeline_reaches_candidate_and_preserves_controls():
    old_ceiling = subject.prior.PHYSICAL_CALL_CEILING
    old_retries = subject.prior.MAX_RETRIES
    packet = subject.execute(fake_transport)
    assert subject.prior.PHYSICAL_CALL_CEILING == old_ceiling
    assert subject.prior.MAX_RETRIES == old_retries
    assert packet["logical_calls"] == 368
    assert packet["physical_attempts"] == 368
    assert packet["encoding"]["exact_records"] == 4
    assert packet["classification_scores"][subject.CLERK_CATALOG]["exact"] == 12
    assert packet["classification_scores"][subject.STATIC_CATALOG]["exact"] == 12
    assert packet["matching_scores"][subject.CLERK_PIPELINE] == 32
    assert packet["matching_scores"][subject.STATIC_ORACLE_SELECTED] == 32
    assert packet["instrument_verdict"]["class"] == "pipeline_candidate"
    assert packet["formation_verdict"] is None


def test_exact_evidence_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    replayed = subject.replay_evidence(evidence_dir)
    assert replayed == packet


def test_invalid_classifications_are_not_resampled():
    classifier_calls = 0

    def invalid_classifier_transport(body: bytes):
        nonlocal classifier_calls
        envelope = json.loads(body)
        user = envelope["messages"][1]["content"]
        if user.startswith("CLASSIFICATION REQUEST"):
            classifier_calls += 1
            return provider('{"applicable_record_ids":["not-in-catalog"]}')
        return fake_transport(body)

    packet = subject.execute(invalid_classifier_transport)
    rows = [
        row for row in packet["calls"]
        if row["responsibility"] == "clerical_classification"
    ]
    assert classifier_calls == 24
    assert len(rows) == 24
    assert all(row["availability"] == "invalid" for row in rows)
    assert packet["retries"] == 0
    assert packet["instrument_verdict"]["class"] == "encoding_only"


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject,
        "collect_provider_receipt",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "smoke_no_contact"
    assert output["side_effects_entered"] is False
