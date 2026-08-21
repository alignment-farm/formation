"""Run the fresh staged-observation-to-action exploratory chain."""
from __future__ import annotations
import argparse, hashlib, json, time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from contact import distributional_developmental_comparison as base
from contact import staged_observation_authorship as staged
from micro_environment.unselected_lineage_behavior import FIRST_INCREASES, SECOND_INCREASES, LineageProfile, LineageState, ProposalReceipt, apply_committed_action
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action

PROTOCOL_VERSION="staged-observation-action-chain-v1"; SPEC_PATH=Path(__file__).parents[1]/"docs"/"STAGED_OBSERVATION_ACTION_CHAIN.md"
WORLDS=("world_a","world_b"); CASES=("same_up","same_down","other_1_up","other_1_down","other_2_up","other_2_down")
COLD="cold"; RAW="raw"; DIRECT="direct_scoped"; STAGED="staged_scoped"; ABLATION="staged_delivery_removed"; UNGATED="staged_ungated"; STATIC="static_scoped"
BRANCHES=(COLD,RAW,DIRECT,STAGED,ABLATION,UNGATED,STATIC); REPEATS=4; PLANNED_LOGICAL_CALLS=8+len(WORLDS)*len(CASES)*len(BRANCHES)*REPEATS; PHYSICAL_CALL_CEILING=352; MAX_RETRIES=8
class ChainRefusal(ValueError): pass
def opaque(x): return hashlib.sha256(f"{PROTOCOL_VERSION}:{x}".encode()).hexdigest()[:20]
@dataclass(frozen=True)
class World:
    name:str; profile:LineageProfile; acquisition:LineageState; cases:dict[str,LineageState]; case_profiles:dict[str,LineageProfile]
def make_world(name,index):
    profile=LineageProfile(opaque(f"{name}:family"),SECOND_INCREASES); p=600+index*173
    acquisition=LineageState(profile.controller_family,opaque(f"{name}:acq-device"),p,p-1,(opaque(f"{name}:acq-first"),opaque(f"{name}:acq-second")))
    cases={}; profiles={}
    for ci,case in enumerate(CASES,1):
        matching=case.startswith("same"); up=case.endswith("up"); prof=profile if matching else LineageProfile(opaque(f"{name}:{case}:family"),FIRST_INCREASES); q=1000+index*401+ci*47
        cases[case]=LineageState(prof.controller_family,opaque(f"{name}:{case}:device"),q,q+(1 if up else -1),(opaque(f"{name}:{case}:first"),opaque(f"{name}:{case}:second"))); profiles[case]=prof
    return World(name,profile,acquisition,cases,profiles)
WORLD_DATA={n:make_world(n,i) for i,n in enumerate(WORLDS,1)}
def table(world): return staged.expected_table(world)
def action_body(state,material):
    record={"device":base.public_device(state),"responsibility":ACTION_RESPONSIBILITY,"retained_material":material}; return base.envelope(base.ACTION_SYSTEM,f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",base.ACTION_SETTINGS)
def direct_body(world,proposal,result):
    record={"external_result":base.exposed_result(result),"occurrence":base.occurrence(world.acquisition,proposal),"responsibility":"Author the complete effect table."}; return base.envelope(staged.forms.AUTHORSHIP_SYSTEMS["effect_table"],f"TABLE REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",{**base.AUTHORSHIP_SETTINGS,"max_tokens":160})
def staged_body(world,observation):
    record={"authored_observation":observation,"public_device":base.public_device(world.acquisition),"responsibility":"Author the complete effect table."}; return base.envelope(staged.STAGED_TABLE_SYSTEM,f"TABLE REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",{**base.AUTHORSHIP_SETTINGS,"max_tokens":160})
def specimen():
    return {"branches":list(BRANCHES),"cases":list(CASES),"model":base.MODEL,"model_digest":base.MODEL_DIGEST,"physical_call_ceiling":PHYSICAL_CALL_CEILING,"planned_logical_calls":PLANNED_LOGICAL_CALLS,"protocol_version":PROTOCOL_VERSION,"repeats":REPEATS,"spec_sha256":base.sha256(SPEC_PATH.read_bytes()),"worlds":{n:{"acquisition":base.public_device(w.acquisition),"cases":{c:{"device":base.public_device(s),"expected_action":oracle_action(s,w.case_profiles[c])} for c,s in w.cases.items()}} for n,w in WORLD_DATA.items()}}
def schedule():
    rows=[]
    for r in range(1,REPEATS+1):
        for ci,c in enumerate(CASES):
            for bi in range(len(BRANCHES)):
                b=BRANCHES[(r-1+bi)%len(BRANCHES)]; order=WORLDS if (r+ci+bi)%2 else tuple(reversed(WORLDS))
                for n in order: rows.append((r,n,c,b))
    return tuple(rows)
Transport=Callable[[bytes],tuple[int,bytes]]
class Recorder:
    def __init__(self,transport,evidence_dir):
        self.transport=transport; self.attempts_dir=None; self.physical=0; self.retries=0; self.attempts=[]
        if evidence_dir is not None: evidence_dir.mkdir(parents=True,exist_ok=False); self.attempts_dir=evidence_dir/"attempts"; self.attempts_dir.mkdir(); (evidence_dir/"specimen.json").write_bytes(base.canonical_json_bytes(specimen()))
    def call(self,i,body):
        final=None
        for a in (1,2):
            if self.physical>=PHYSICAL_CALL_CEILING: raise ChainRefusal("physical_call_ceiling")
            self.physical+=1; status=None; raw=b""; error=None
            try: status,raw=self.transport(body)
            except ConnectionError as e: error=str(e)
            retryable=error is not None or status in {408,429,500,502,503,504}; meta={"attempt":a,"error":error,"http_status":status,"logical_index":i,"request_sha256":base.sha256(body),"response_sha256":base.sha256(raw),"retryable":retryable}; self.attempts.append(meta)
            if self.attempts_dir is not None:
                stem=f"{self.physical:03d}-sc{i:03d}-a{a}"; (self.attempts_dir/f"{stem}.request.json").write_bytes(body); (self.attempts_dir/f"{stem}.response.bin").write_bytes(raw); (self.attempts_dir/f"{stem}.meta.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
            if retryable and a==1 and self.retries<MAX_RETRIES: self.retries+=1; continue
            final=status,error,raw; break
        status,error,raw=final; content,available,provider=base.parse_content(raw,status); return status,error,content,available,provider.get("usage")
def execute(transport,evidence_dir=None):
    rec=Recorder(transport,evidence_dir); calls=[]; artifacts={}
    i=0
    for name in WORLDS:
        w=WORLD_DATA[name]; i+=1; body=action_body(w.acquisition,""); status,error,content,ca,usage=rec.call(i,body); av,action=base.parse_action(content,w.acquisition); provider=status==200 and error is None and ca; proposal=ProposalReceipt(provider,(action or content) if provider else ""); result=apply_committed_action(w.acquisition,w.profile,proposal); calls.append({"responsibility":"acquisition","world":name,"action":action,"external_result":base.exposed_result(result),"provider_usage":usage,"request_sha256":base.sha256(body)})
        i+=1; body=staged.observation_body(w,proposal,result); status,error,obs,ca,usage=rec.call(i,body); obs=obs if status==200 and error is None and ca else ""; fields=base.exposed_result(result); exact_obs=obs==staged.expected_observation(w,fields.get("selected_slot",""),fields.get("movement_direction","")); calls.append({"responsibility":"observation","world":name,"content":obs,"exact":exact_obs,"provider_usage":usage,"request_sha256":base.sha256(body)})
        i+=1; body=direct_body(w,proposal,result); status,error,direct,ca,usage=rec.call(i,body); direct=direct if status==200 and error is None and ca else ""; calls.append({"responsibility":"direct_table","world":name,"content":direct,"exact":direct==table(w),"provider_usage":usage,"request_sha256":base.sha256(body)})
        i+=1; body=staged_body(w,obs); status,error,stage,ca,usage=rec.call(i,body); stage=stage if status==200 and error is None and ca else ""; calls.append({"responsibility":"staged_table","world":name,"content":stage,"exact":stage==table(w),"provider_usage":usage,"request_sha256":base.sha256(body)}); artifacts[name]=(proposal,result,direct,stage,exact_obs)
    later=[]
    for i,(repeat,name,case,branch) in enumerate(schedule(),9):
        w=WORLD_DATA[name]; state=w.cases[case]; proposal,result,direct,stage,_=artifacts[name]; matching=case.startswith("same")
        if branch in (COLD,ABLATION): material=""
        elif branch==RAW: material=base.canonical_json_bytes(base.experience_record(w.acquisition,proposal,result)).decode()
        elif branch==DIRECT: material=direct if matching else ""
        elif branch==STAGED: material=stage if matching else ""
        elif branch==UNGATED: material=stage
        elif branch==STATIC: material=table(w) if matching else ""
        body=action_body(state,material); status,error,content,ca,usage=rec.call(i,body); av,action=base.parse_action(content,state)
        if status!=200 or error is not None: av,action="unavailable",None
        provider=status==200 and error is None and ca; receipt=ProposalReceipt(provider,(action or content) if provider else ""); result2=apply_committed_action(state,w.case_profiles[case],receipt); row={"responsibility":"later_action","world":name,"case":case,"branch":branch,"repeat":repeat,"action":action,"availability":av,"correct_action":av=="available" and action==oracle_action(state,w.case_profiles[case]),"external_result":base.exposed_result(result2),"provider_usage":usage,"request_sha256":base.sha256(body),"retained_material_sha256":base.sha256(material.encode())}; later.append(row); calls.append(row)
    dist={n:{b:{c:{"assigned":len(rows:=[r for r in later if r["world"]==n and r["branch"]==b and r["case"]==c]),"correct_actions":sum(r["correct_action"] for r in rows),"invalid_or_unavailable":sum(r["availability"]!="available" for r in rows),"distinct_outcomes":len(Counter(r["action"] or f"<{r['availability']}>" for r in rows))} for c in CASES} for b in BRANCHES} for n in WORLDS}
    engaged=all(a[4] and a[3]==table(WORLD_DATA[n]) for n,a in artifacts.items()) and all(dist[n][STATIC][c]["correct_actions"]>=3 for n in WORLDS for c in ("same_up","same_down")); harmful=False; supported=engaged; prevented=0
    for n in WORLDS:
        for c in ("same_up","same_down"):
            s=dist[n][STAGED][c]["correct_actions"]; supported &= s>=3 and all(s-dist[n][b][c]["correct_actions"]>=2 for b in (COLD,RAW,DIRECT,ABLATION))
        for c in CASES[2:]:
            s=dist[n][STAGED][c]["correct_actions"]; cold=dist[n][COLD][c]["correct_actions"]; harmful |= s<=cold-2; supported &= s>=cold-1; prevented += max(0,s-dist[n][UNGATED][c]["correct_actions"])
        for b in BRANCHES:
            for c in CASES: supported &= dist[n][b][c]["invalid_or_unavailable"]<=1
    supported &= prevented>=2
    verdict={"class":"not_engaged" if not engaged else "harmful" if harmful else "candidate_found" if supported else "null","scope":"staged_observation_action_chain"}
    packet={"attempts":rec.attempts,"calls":calls,"chain_verdict":verdict,"formation_verdict":None,"logical_calls":len(calls),"model":base.MODEL,"model_digest":base.MODEL_DIGEST,"physical_attempts":rec.physical,"protocol_version":PROTOCOL_VERSION,"request_distributions":dist,"retries":rec.retries,"scope_errors_prevented":prevented,"specimen_sha256":base.sha256(base.canonical_json_bytes(specimen()))}
    if evidence_dir is not None: (evidence_dir/"packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet
def replay_evidence(d):
    if (d/"specimen.json").read_bytes()!=base.canonical_json_bytes(specimen()): raise ChainRefusal("specimen_mismatch")
    retained=json.loads((d/"packet.json").read_bytes()); entries=[]
    for m in sorted((d/"attempts").glob("*.meta.json")):
        stem=m.name.removesuffix(".meta.json"); meta=json.loads(m.read_text()); entries.append(((d/"attempts"/f"{stem}.request.json").read_bytes(),(d/"attempts"/f"{stem}.response.bin").read_bytes(),meta))
    pos=0
    def t(body):
        nonlocal pos
        req,res,meta=entries[pos]; pos+=1
        if req!=body: raise ChainRefusal("request_mismatch")
        if meta["error"] is not None: raise ConnectionError(meta["error"])
        return meta["http_status"],res
    p=execute(t)
    if pos!=len(entries) or base.canonical_json_bytes(p)!=base.canonical_json_bytes(retained): raise ChainRefusal("replay_mismatch")
    return p
def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument("--live",action="store_true"); ap.add_argument("--evidence-dir",type=Path); a=ap.parse_args(argv)
    if not a.live: print(json.dumps({"mode":"smoke_no_contact","planned_logical_calls":PLANNED_LOGICAL_CALLS,"side_effects_entered":False},sort_keys=True)); return 0
    if a.evidence_dir is None: a.evidence_dir=Path("evidence")/f"staged-observation-action-chain-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    start=time.monotonic(); receipt=base.collect_provider_receipt()
    if not receipt["valid"]: raise ChainRefusal("provider_identity_mismatch")
    p=execute(base.live_transport,a.evidence_dir); (a.evidence_dir/"provider.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n"); replay_evidence(a.evidence_dir); print(json.dumps({"chain_verdict":p["chain_verdict"],"elapsed_seconds":time.monotonic()-start,"evidence_dir":str(a.evidence_dir),"logical_calls":p["logical_calls"],"physical_attempts":p["physical_attempts"]},sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
