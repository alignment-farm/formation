"""Run the single Muse successor on the consumed calibration packet."""

from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path

from contact import calibration_mechanism_discovery as base
from contact.exploratory_developmental_contact import (
    ENDPOINT,
    LiveInvoker,
    _run_command,
)


PROTOCOL_VERSION = "muse-counter-prior-successor-v0"
MODEL = "huggingface.co/meta-models/muse-glimmer-30b-gguf:Q4_K_XL"
MODEL_DIGEST = "sha256:ad54b4b4122ee8e98fd5528a4e26bcbf59034b3b8d0d6d0d1acda98a5f759b6e"
MODEL_ARCHITECTURE = "muse-glimmer"
ACTOR_SETTINGS: dict[str, object] = {
    "max_tokens": 256,
    "temperature": 0.6,
    "top_p": 0.95,
    "stream": False,
    "response_format": {"type": "json_object"},
}
INTERPRETER_SETTINGS: dict[str, object] = {
    **ACTOR_SETTINGS,
    "max_tokens": 384,
}


def _successor_envelope(
    envelope: dict[str, object], settings: dict[str, object]
) -> dict[str, object]:
    messages = []
    for message in envelope["messages"]:
        content = message["content"]
        if type(content) is str:
            content = content.replace("\n/no_think", "")
        messages.append({"role": message["role"], "content": content})
    return {"model": MODEL, "messages": messages, **settings}


def actor_envelope(
    state: base.CalibrationState, offer: str = base.NONE_OFFER
) -> dict[str, object]:
    return _successor_envelope(base.actor_envelope(state, offer), ACTOR_SETTINGS)


def interpretation_envelope(experience: dict[str, object]) -> dict[str, object]:
    return _successor_envelope(
        base.interpretation_envelope(experience), INTERPRETER_SETTINGS
    )


def later_schedule(
    world_material: dict[str, dict[str, object]], start_index: int = 6
) -> tuple[base.LogicalCall, ...]:
    calls = base.later_schedule(world_material, start_index)
    transformed = []
    for call in calls:
        envelope = _successor_envelope(call.envelope, ACTOR_SETTINGS)
        transformed.append(replace(call, envelope=envelope))
    return tuple(transformed)


def collect_provider_receipt() -> dict[str, object]:
    version = _run_command(("docker", "model", "version"))
    status = _run_command(("docker", "model", "status"))
    inventory = _run_command(("docker", "model", "list"))
    inspection = _run_command(("docker", "model", "inspect", MODEL))
    reasons: list[str] = []
    for name, record in (
        ("version", version),
        ("status", status),
        ("inventory", inventory),
        ("inspection", inspection),
    ):
        if record["returncode"] != 0:
            reasons.append(f"{name}_command_failed")
    parsed_inspection: object = None
    if not reasons:
        try:
            parsed_inspection = json.loads(str(inspection["stdout"]))
            if type(parsed_inspection) is not dict:
                raise ValueError("inspection_object_required")
            if parsed_inspection.get("id") != MODEL_DIGEST:
                reasons.append("model_digest_mismatch")
            tags = parsed_inspection.get("tags")
            if type(tags) is not list or MODEL not in tags:
                reasons.append("model_tag_mismatch")
            config = parsed_inspection.get("config")
            if (
                type(config) is not dict
                or config.get("architecture") != MODEL_ARCHITECTURE
            ):
                reasons.append("model_architecture_mismatch")
        except (json.JSONDecodeError, ValueError):
            reasons.append("inspection_invalid")
    if "llama.cpp" not in str(status["stdout"]) or "Running" not in str(
        status["stdout"]
    ):
        reasons.append("llama_runner_not_running")
    if MODEL not in str(inventory["stdout"]):
        reasons.append("model_not_in_inventory")
    return {
        "valid": not reasons,
        "refusals": reasons,
        "endpoint": ENDPOINT,
        "version": version,
        "status": status,
        "inventory": inventory,
        "inspection": inspection,
        "parsed_inspection": parsed_inspection,
    }


def _protocol_record() -> dict[str, object]:
    record = base._protocol_record()
    record.update(
        {
            "protocol": PROTOCOL_VERSION,
            "model": MODEL,
            "inspect_tag": MODEL,
            "model_digest": MODEL_DIGEST,
            "actor_settings": ACTOR_SETTINGS,
            "interpreter_settings": INTERPRETER_SETTINGS,
            "predecessor_protocol": base.PROTOCOL_VERSION,
            "predecessor_evidence": "../calibration-mechanism-discovery-20260817",
            "model_native_adjustments": [
                "qwen_no_think_instruction_omitted",
                "actor_max_tokens_256",
                "interpreter_max_tokens_384",
            ],
        }
    )
    return record


def _successor_summary(
    runner: base.ContactRunner, state: str, stop_reason: str | None
) -> dict[str, object]:
    summary = runner.summary(state, stop_reason)
    summary.update(
        {
            "protocol": PROTOCOL_VERSION,
            "model": MODEL,
            "model_digest": MODEL_DIGEST,
            "predecessor_protocol": base.PROTOCOL_VERSION,
        }
    )
    return summary


def run_contact(
    invoker: base.Invoker,
    directory: Path,
    provider_receipt: dict[str, object],
    physical_ceiling: int = base.PHYSICAL_CALL_CEILING,
) -> dict[str, object]:
    writer = base.EvidenceWriter(directory)
    writer.write_json("protocol.json", _protocol_record())
    writer.write_json("provider.json", provider_receipt)
    runner = base.ContactRunner(invoker, writer, physical_ceiling)
    if provider_receipt.get("valid") is not True:
        summary = _successor_summary(runner, "stopped", "provider_receipt_invalid")
        writer.write_json("summary.json", summary)
        return summary

    try:
        interface = base.LogicalCall(
            1,
            "interface-disposable",
            "actor",
            actor_envelope(base.INTERFACE_STATE),
            state=base.INTERFACE_STATE,
            profile=base.INTERFACE_PROFILE,
        )
        interface_record = runner.record_actor(interface, runner.invoke(interface))
        if interface_record["surfaced_action"] is None:
            summary = _successor_summary(
                runner, "stopped", "interface_action_unobservable"
            )
            writer.write_json("summary.json", summary)
            return summary

        world_material: dict[str, dict[str, object]] = {}
        logical_index = 2
        for world in base.WORLDS:
            acquisition_call = base.LogicalCall(
                logical_index,
                f"{world.world_id}-acquisition",
                "actor",
                actor_envelope(world.acquisition),
                state=world.acquisition,
                profile=world.acquisition_profile,
                world_id=world.world_id,
            )
            acquisition = runner.record_actor(
                acquisition_call, runner.invoke(acquisition_call)
            )
            if acquisition["surfaced_action"] is None:
                summary = _successor_summary(
                    runner,
                    "stopped",
                    f"{world.world_id}_acquisition_action_unobservable",
                )
                writer.write_json("summary.json", summary)
                return summary
            experience = {
                "state": acquisition["state"],
                "model_message": acquisition["message"],
                "surfaced_action": acquisition["surfaced_action"],
                "environment_result": acquisition["environment_result"],
            }
            writer.write_json(f"{world.world_id}-acquisition.json", experience)
            logical_index += 1

            interpreter_call = base.LogicalCall(
                logical_index,
                f"{world.world_id}-interpretation",
                "interpreter",
                interpretation_envelope(experience),
                world_id=world.world_id,
            )
            interpreter_attempt = runner.invoke(interpreter_call)
            interpretation = (
                "" if interpreter_attempt.content is None else interpreter_attempt.content
            )
            governance = base.govern_candidate(interpretation, experience)
            interpreter_record = {
                "logical_index": logical_index,
                "call_id": interpreter_call.call_id,
                "responsibility": "interpreter",
                "world_id": world.world_id,
                "message": interpreter_attempt.message,
                "content": interpretation,
                "author": "cold_model",
                "source_experience": f"{world.world_id}-acquisition.json",
            }
            runner.logical_records.append(interpreter_record)
            writer.write_logical(interpreter_call, interpreter_record)
            writer.write_json(f"{world.world_id}-interpretation.json", interpreter_record)
            writer.write_json(f"{world.world_id}-governance.json", governance)
            runner.governance[world.world_id] = governance
            world_material[world.world_id] = {
                "experience": experience,
                "interpretation": interpretation,
                "governance": governance,
                "offers": base.offer_materials(experience, interpretation, governance),
            }
            logical_index += 1

        for call in later_schedule(world_material, logical_index):
            runner.record_actor(call, runner.invoke(call))
    except base.ContactStop as stop:
        summary = _successor_summary(runner, "stopped", str(stop))
        writer.write_json("summary.json", summary)
        return summary

    summary = _successor_summary(runner, "complete", None)
    writer.write_json("summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    if not args.live:
        raise SystemExit("live contact requires --live")
    receipt = collect_provider_receipt()
    summary = run_contact(LiveInvoker(), args.evidence_dir, receipt)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
