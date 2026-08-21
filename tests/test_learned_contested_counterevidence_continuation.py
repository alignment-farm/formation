import json

from contact import learned_contested_counterevidence_continuation as subject


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
    for name, lineage in subject.LINEAGE_DATA.items():
        parent = subject.PARENT_LINEAGES[name]
        for design in parent.designs.values():
            if description in {design.source_description, design.later_description}:
                return {"beacon_class": design.beacon, "housing_class": design.housing}
        for case in lineage.post_cases.values():
            if case.description == description:
                return case.scope
    raise AssertionError(description)


def state_for_device(device_id: str):
    for lineage in subject.LINEAGE_DATA.values():
        for case in lineage.post_cases.values():
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
                if "fell" in record["gauge_report"]
                else subject.learned.INCREASES
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


def test_fresh_specimen_and_fixed_schedule():
    specimen = subject.specimen()
    assert specimen["parent_packet_sha256"] == subject.PARENT_PACKET_SHA256
    assert len(subject.post_schedule()) == 432
    assert subject.PLANNED_LOGICAL_CALLS == 480
    assert subject.PHYSICAL_CALL_CEILING == 492
    assert sum(
        len(lineage.source_events) for lineage in subject.LINEAGE_DATA.values()
    ) == 6
    assert {
        lineage.history_name for lineage in subject.LINEAGE_DATA.values()
    } == set(subject.HISTORIES)


def test_generalized_governor_preserves_order_and_distinguishes_states():
    current = {
        "first_control_effect": subject.learned.INCREASES,
        "second_control_effect": subject.learned.DECREASES,
    }
    opposite = subject.opposite_record(current)
    rows = [{
        "composed_status": subject.admission.ADMITTED,
        "event_id": f"e:{index}",
        "movement": "decreased",
        "movement_status": "complete",
        "order": index,
        "proposed_record": opposite,
        "selected_slot": "first",
    } for index in (1, 2)]
    assert subject.decide_history(current, rows[:1])["governance_state"] == (
        "suspended_pending_corroboration"
    )
    final = subject.decide_history(current, rows)
    assert final["governance_state"] == "superseded"
    assert final["considered_occurrence_ids"] == ["e:1", "e:2"]


def test_fake_learned_continuation_is_supported():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 480
    assert packet["physical_attempts"] == 480
    assert packet["components"] == {
        "complete_composed_admissions": 5,
        "complete_movements_exact": 5,
        "contested_movement_unsettled": 1,
        "contested_proposal_quarantines": 1,
        "exact_complete_records": 5,
        "exact_complete_selected_effect_projections": 5,
        "exact_final_governance_states": 4,
        "exact_intermediate_governance_histories": 4,
        "exact_later_catalog_assignments": 432,
        "exact_later_normalizations": 24,
        "exact_ordered_source_histories": 4,
        "exploration_actions_exact": 6,
        "parent_admitted_version_2_records": 8,
        "suspended_a_deliveries_without_record": 12,
    }
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["formation_verdict"] is None
    assert packet["history_scores"][subject.GOVERNED][subject.REPEATED]["a"] == 6
    assert packet["history_scores"][subject.GOVERNED][subject.SELF_CORRECTING]["a"] == 6
    assert packet["history_scores"][subject.GOVERNED][subject.ISOLATED]["a"] == 3
    assert packet["history_scores"][subject.LATEST][subject.ISOLATED]["a"] == 0


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
