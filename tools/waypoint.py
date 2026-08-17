"""Expose research-route drift before a proposed task begins.

Waypoint is a project-process instrument. It is not part of the Formation
runtime, trajectory harness, developmental lineage, or evidence plane.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Sequence


INSTRUMENT = "waypoint-v0"
KINDS = (
    "lifecycle_step",
    "lifecycle_repair",
    "support",
    "model_catalog_search",
    "generic_competence_gate",
    "model_admission",
    "model_contact",
)
ALWAYS_PROHIBITED = (
    "model_catalog_search",
    "generic_competence_gate",
    "model_admission",
)
CLAIM_LEVELS = ("wire", "mechanism", "formation")
VERDICT_EXIT = {"ON_ROUTE": 0, "SUPPORT_ONLY": 1, "ROUTE_DRIFT": 2}
QUESTION = (
    "If this succeeds, does a Formation lifecycle edge run, or does it only "
    "authorize another gate?"
)


@dataclass(frozen=True)
class RouteState:
    current_boundary: str
    next_boundary: str
    permitted_claim_level: str
    model_contact_allowed: bool
    named_responsibilities: tuple[str, ...]
    prohibited_work_kinds: tuple[str, ...]
    historical_pressure: tuple[str, ...]


@dataclass(frozen=True)
class Proposal:
    summary: str
    kind: str
    target: str
    success: str
    failure: str
    claim: str
    unblocks: str = "none"
    responsibility: str = "none"


@dataclass(frozen=True)
class Inspection:
    instrument: str
    verdict: str
    current_boundary: str
    next_boundary: str
    proposal: Proposal
    findings: tuple[str, ...]
    historical_pressure: tuple[str, ...]
    question: str = QUESTION

    @property
    def exit_code(self) -> int:
        return VERDICT_EXIT[self.verdict]

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["exit_code"] = self.exit_code
        return value


def _nonempty_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def load_route_state(path: Path) -> RouteState:
    raw = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "instrument",
        "current_boundary",
        "next_boundary",
        "permitted_claim_level",
        "model_contact",
        "prohibited_work_kinds",
        "historical_pressure",
    }
    if not isinstance(raw, dict) or set(raw) != required:
        raise ValueError("route state fields do not match waypoint-v0")
    if raw["instrument"] != INSTRUMENT:
        raise ValueError("route state instrument mismatch")
    contact = raw["model_contact"]
    if not isinstance(contact, dict) or set(contact) != {"allowed", "named_responsibilities"}:
        raise ValueError("model_contact fields do not match waypoint-v0")
    if not isinstance(contact["allowed"], bool):
        raise ValueError("model_contact.allowed must be boolean")
    sequences = {
        "named_responsibilities": contact["named_responsibilities"],
        "prohibited_work_kinds": raw["prohibited_work_kinds"],
        "historical_pressure": raw["historical_pressure"],
    }
    for name, values in sequences.items():
        if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
            raise ValueError(f"{name} must be a list of non-empty strings")
        if len(values) != len(set(values)):
            raise ValueError(f"{name} must not contain duplicates")
    prohibited = tuple(sequences["prohibited_work_kinds"])
    if any(kind not in KINDS for kind in prohibited):
        raise ValueError("prohibited_work_kinds contains an unknown kind")
    if not set(ALWAYS_PROHIBITED).issubset(prohibited):
        raise ValueError("route state must prohibit catalog search, generic gates, and model admission")
    if contact["allowed"] == ("model_contact" in prohibited):
        raise ValueError("model contact permission contradicts prohibited_work_kinds")
    claim = _nonempty_string(raw["permitted_claim_level"], "permitted_claim_level")
    if claim not in CLAIM_LEVELS:
        raise ValueError("unknown permitted_claim_level")
    return RouteState(
        current_boundary=_nonempty_string(raw["current_boundary"], "current_boundary"),
        next_boundary=_nonempty_string(raw["next_boundary"], "next_boundary"),
        permitted_claim_level=claim,
        model_contact_allowed=contact["allowed"],
        named_responsibilities=tuple(sequences["named_responsibilities"]),
        prohibited_work_kinds=prohibited,
        historical_pressure=tuple(sequences["historical_pressure"]),
    )


def inspect_proposal(state: RouteState, proposal: Proposal) -> Inspection:
    if not proposal.summary.strip():
        raise ValueError("proposal summary must not be empty")
    if proposal.kind not in KINDS:
        raise ValueError(f"unknown work kind: {proposal.kind}")
    if proposal.claim not in CLAIM_LEVELS:
        raise ValueError(f"unknown claim level: {proposal.claim}")

    findings: list[str] = []
    drift = False

    if proposal.kind in state.prohibited_work_kinds:
        drift = True
        findings.append(
            f"{proposal.kind} is prohibited on the current route; it adds pre-contact selection instead of exercising the lifecycle."
        )

    if proposal.claim != state.permitted_claim_level:
        drift = True
        findings.append(
            f"claim level {proposal.claim} exceeds the current {state.permitted_claim_level} boundary."
        )

    if proposal.kind == "lifecycle_step":
        if proposal.target != state.current_boundary:
            drift = True
            findings.append(
                f"target {proposal.target} skips the current boundary {state.current_boundary}."
            )
        if proposal.success != state.next_boundary:
            drift = True
            findings.append(
                f"success must reach {state.next_boundary}, not {proposal.success}; success that earns another gate is not lifecycle progress."
            )
        if proposal.failure != state.current_boundary:
            drift = True
            findings.append(
                f"failure must return to {state.current_boundary}, not open {proposal.failure}."
            )
        if not drift:
            findings.append(
                f"the proposal exercises {state.current_boundary} and advances directly to {state.next_boundary}."
            )

    elif proposal.kind == "lifecycle_repair":
        if proposal.target != state.current_boundary or proposal.unblocks != state.current_boundary:
            drift = True
            findings.append(
                f"a repair must target and unblock the current boundary {state.current_boundary}."
            )
        if proposal.success != state.current_boundary or proposal.failure != state.current_boundary:
            drift = True
            findings.append("a repair must stay with the contacted boundary on both success and failure.")
        if not drift:
            findings.append(f"the repair stays attached to {state.current_boundary}.")

    elif proposal.kind == "support":
        if proposal.unblocks != state.current_boundary:
            drift = True
            findings.append(
                f"support work must name how it unblocks {state.current_boundary}."
            )
        if proposal.success != state.current_boundary or proposal.failure != state.current_boundary:
            drift = True
            findings.append("support work may not create a successor route of its own.")
        if not drift:
            findings.append(
                f"this is support for {state.current_boundary}; it does not itself advance the Formation lifecycle."
            )

    elif proposal.kind == "model_contact":
        if not state.model_contact_allowed:
            drift = True
            findings.append("model contact is closed until a lifecycle component names an untestable deterministic responsibility.")
        if proposal.responsibility not in state.named_responsibilities:
            drift = True
            findings.append("the proposed inference responsibility is not named in the current route state.")
        if proposal.target != state.current_boundary or proposal.unblocks != state.current_boundary:
            drift = True
            findings.append(
                f"a permitted model contact must target and unblock {state.current_boundary}."
            )
        if proposal.success != state.current_boundary or proposal.failure != state.current_boundary:
            drift = True
            findings.append("a model interface check may not create a successor route of its own.")
        if not drift:
            findings.append(
                f"this model contact supports the named responsibility at {state.current_boundary}; it is not lifecycle progress."
            )

    if drift:
        verdict = "ROUTE_DRIFT"
    elif proposal.kind in ("support", "model_contact"):
        verdict = "SUPPORT_ONLY"
    else:
        verdict = "ON_ROUTE"

    return Inspection(
        instrument=INSTRUMENT,
        verdict=verdict,
        current_boundary=state.current_boundary,
        next_boundary=state.next_boundary,
        proposal=proposal,
        findings=tuple(findings),
        historical_pressure=state.historical_pressure,
    )


def render_text(inspection: Inspection) -> str:
    lines = [
        f"WAYPOINT: {inspection.verdict}",
        f"Current lifecycle boundary: {inspection.current_boundary}",
        f"Next lifecycle boundary: {inspection.next_boundary}",
        f"Proposal: {inspection.proposal.summary}",
        (
            "Declared path: "
            f"{inspection.proposal.target} --success--> {inspection.proposal.success}; "
            f"--failure--> {inspection.proposal.failure}"
        ),
        "Findings:",
        *(f"- {finding}" for finding in inspection.findings),
        "Historical pressure:",
        *(f"- {item}" for item in inspection.historical_pressure),
        f"Question: {inspection.question}",
    ]
    if inspection.verdict == "ROUTE_DRIFT":
        lines.append(f"Action: stop and return the proposal to {inspection.current_boundary}.")
    elif inspection.verdict == "SUPPORT_ONLY":
        lines.append(f"Action: do not count this as progress; return to {inspection.current_boundary}.")
    else:
        lines.append(f"Action: proceed within the declared {inspection.proposal.claim}-level boundary.")
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="waypoint", description=__doc__)
    parser.add_argument(
        "--state",
        type=Path,
        default=Path(__file__).with_name("waypoint_route.json"),
        help="reviewed current-route state",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    show = subparsers.add_parser("show", help="show the current route and historical pressure")
    show.add_argument("--json", action="store_true", help="emit JSON")
    inspect = subparsers.add_parser("inspect", help="inspect one proposed task")
    inspect.add_argument("--summary", required=True)
    inspect.add_argument("--kind", required=True, choices=KINDS)
    inspect.add_argument("--target", required=True)
    inspect.add_argument("--success", required=True)
    inspect.add_argument("--failure", required=True)
    inspect.add_argument("--claim", required=True, choices=CLAIM_LEVELS)
    inspect.add_argument("--unblocks", default="none")
    inspect.add_argument("--responsibility", default="none")
    inspect.add_argument("--json", action="store_true", help="emit JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        state = load_route_state(args.state)
        if args.command == "show":
            value = {
                "instrument": INSTRUMENT,
                "current_boundary": state.current_boundary,
                "next_boundary": state.next_boundary,
                "permitted_claim_level": state.permitted_claim_level,
                "model_contact_allowed": state.model_contact_allowed,
                "historical_pressure": state.historical_pressure,
            }
            if args.json:
                print(json.dumps(value, indent=2, sort_keys=True))
            else:
                print(f"WAYPOINT: {state.current_boundary} -> {state.next_boundary}")
                print(f"Permitted claim level: {state.permitted_claim_level}")
                print(f"Model contact allowed: {str(state.model_contact_allowed).lower()}")
                print("Historical pressure:")
                for item in state.historical_pressure:
                    print(f"- {item}")
                print(f"Question: {QUESTION}")
            return 0
        proposal = Proposal(
            summary=args.summary,
            kind=args.kind,
            target=args.target,
            success=args.success,
            failure=args.failure,
            claim=args.claim,
            unblocks=args.unblocks,
            responsibility=args.responsibility,
        )
        inspection = inspect_proposal(state, proposal)
        if args.json:
            print(json.dumps(inspection.to_dict(), indent=2, sort_keys=True))
        else:
            print(render_text(inspection))
        return inspection.exit_code
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
