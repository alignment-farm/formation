import json
from contact import staged_observation_action_chain as subject

def provider(c): return 200,json.dumps({"choices":[{"message":{"content":c}}],"usage":{"prompt_tokens":9,"completion_tokens":3}}).encode()
def fake(body):
    e=json.loads(body); u=e["messages"][1]["content"]; r=json.loads(u.split("\n",1)[1].rsplit("\n",1)[0])
    if u.startswith("OBSERVATION REQUEST"):
        w=next(w for w in subject.WORLD_DATA.values() if w.profile.controller_family==r["occurrence"]["public_device"]["controller_family"]); x=r["external_result"]; return provider(subject.staged.expected_observation(w,x["selected_slot"],x["movement_direction"]))
    if u.startswith("TABLE REQUEST"):
        pub=r.get("public_device") or r["occurrence"]["public_device"]; w=next(w for w in subject.WORLD_DATA.values() if w.profile.controller_family==pub["controller_family"]); return provider(subject.table(w) if "authored_observation" in r else subject.staged.expected_table(w,opposite=True))
    state=next(s for w in subject.WORLD_DATA.values() for s in (w.acquisition,*w.cases.values()) if s.device==r["device"]["device"]); m=r["retained_material"]
    correct_mapping=bool(m) and ("second_displayed_control_effect\":\"increases_position" in m)
    action=(state.controls[1] if state.target>state.position else state.controls[0]) if correct_mapping else (state.controls[0] if state.target>state.position else state.controls[1]); return provider(json.dumps({"action":action}))
def test_schedule():
    assert subject.PLANNED_LOGICAL_CALLS==344 and len(subject.schedule())==336
def test_fake_supports_and_replays(tmp_path):
    d=tmp_path/"e"; p=subject.execute(fake,d); assert p["chain_verdict"]["class"]=="candidate_found"; assert p["logical_calls"]==p["physical_attempts"]==344; assert p["scope_errors_prevented"]>=2; assert subject.replay_evidence(d)==p
def test_bad_not_engaged(tmp_path):
    p=subject.execute(lambda body:provider("bad"),tmp_path/"bad"); assert p["chain_verdict"]["class"]=="not_engaged"
def test_smoke(capsys):
    assert subject.main([])==0; assert json.loads(capsys.readouterr().out)["side_effects_entered"] is False
