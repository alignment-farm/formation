import json

import pytest

from contact import same_request_variation as subject


def envelope(action):
    return 200, json.dumps({"choices": [{"message": {"content": json.dumps({"action": action})}}], "usage": {"completion_tokens": 3}}).encode()


def test_sources_are_exact_retained_requests():
    sources = subject.load_sources()
    assert tuple(source.invocation for source in sources) == subject.SOURCE_INVOCATIONS
    assert all(subject.sha256(source.request) == source.request_sha256 for source in sources)
    assert sources[0].original_correctness == (False, True)
    assert len(set(sources[0].original_outputs)) == 2


def test_schedule_interleaves_four_requests_for_eight_rounds():
    schedule = subject.schedule(subject.load_sources())
    assert len(schedule) == subject.PLANNED_LOGICAL_CALLS == 32
    assert [source.invocation for _, source in schedule[:4]] == list(subject.SOURCE_INVOCATIONS)
    assert [repeat for repeat, _ in schedule[::4]] == list(range(1, 9))


def test_run_retains_distribution_and_exact_request_bytes(tmp_path):
    seen = []
    counts = {}
    def fake(body):
        seen.append(body)
        digest = subject.sha256(body)
        counts[digest] = counts.get(digest, 0) + 1
        parsed = json.loads(body)
        actions = json.loads(parsed["messages"][1]["content"].split("\n", 1)[1].rsplit("\n", 1)[0])["device"]["allowed_actions"]
        return envelope(actions[counts[digest] % 2])
    packet = subject.run(fake, tmp_path / "evidence")
    assert packet["logical_calls"] == 32
    assert packet["physical_attempts"] == 32
    assert all(item["distinct_outcomes"] == 2 for item in packet["request_distributions"].values())
    first_saved = next((tmp_path / "evidence" / "attempts").glob("001-*.request.json")).read_bytes()
    assert first_saved == subject.load_sources()[0].request
    assert packet["formation_verdict"] is packet["validation_verdict"] is None


def test_transport_failure_retries_once(tmp_path):
    calls = 0
    def fake(body):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ConnectionError("temporary")
        parsed = json.loads(body)
        action = json.loads(parsed["messages"][1]["content"].split("\n", 1)[1].rsplit("\n", 1)[0])["device"]["allowed_actions"][0]
        return envelope(action)
    packet = subject.run(fake, tmp_path / "evidence")
    assert packet["logical_calls"] == 32
    assert packet["physical_attempts"] == 33
    assert packet["attempts"][0]["retryable"] is True


def test_invalid_output_is_retained_without_retry(tmp_path):
    packet = subject.run(lambda body: (200, b'{"choices":[]}'), tmp_path / "evidence")
    assert packet["physical_attempts"] == 32
    assert all(row["availability"] == "invalid" for row in packet["calls"])


def test_existing_destination_refuses_overwrite(tmp_path):
    destination = tmp_path / "evidence"
    destination.mkdir()
    with pytest.raises(FileExistsError):
        subject.run(lambda body: envelope("hold"), destination)
