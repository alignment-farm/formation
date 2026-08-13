"""Runtime-owned producer for the first fixture's shared prefix.

This module implements only ``D-C-001`` through ``D-C-006`` under the
``fixture-v0-prefix-jsonl-v0`` contract. It is not a general record schema.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from types import MappingProxyType
from typing import Any, Mapping, Sequence


MATERIALIZER = "fixture-v0-prefix-jsonl-v0"
SOURCE_HEAD = "D-C-006"


class PrefixSourceRefusal(ValueError):
    """The runtime receipt source cannot produce the fixture prefix."""


class HandoffRefusal(ValueError):
    """A handoff is not current and runtime-issued."""


_TOP_LEVEL_FIELDS = (
    "contract",
    "coordinate",
    "record",
    "order",
    "event",
    "authority",
    "parents",
    "retention",
    "payload",
)

_COORDINATES = tuple(f"D-C-{index:03d}" for index in range(1, 7))

_PAYLOAD_FIELDS = {
    "D-C-001": (
        "model_identity",
        "model_configuration",
        "runtime_interface",
        "initial_lineage_head",
        "supported_interfaces",
    ),
    "D-C-002": (
        "encounter",
        "candidate_object",
        "derived_from",
        "artifact_revision",
        "authority_revision",
        "depends_on_current_authority",
        "commit_action",
        "refresh_action",
    ),
    "D-C-003": (
        "encounter",
        "invocation",
        "stub",
        "cold_invocation",
        "request_binding",
        "output_authority",
        "output",
    ),
    "D-C-004": (
        "encounter",
        "invocation",
        "action",
        "action_name",
        "target",
    ),
    "D-C-005": (
        "encounter",
        "action",
        "consequence",
        "source",
        "outcome",
        "reason",
        "observed_rule",
    ),
    "D-C-006": (
        "encounter",
        "included_events",
        "consequence",
        "applicability_claim",
    ),
}

_EXPECTED_ARTIFACT = (
    b'{"contract":"fixture-v0","coordinate":"D-C-001","record":"developmental","order":1,"event":"practitioner_initialized","authority":"formation_runtime","parents":[],"retention":"inline","payload":{"model_identity":"cold-model-stub-v0","model_configuration":"deterministic-v0","runtime_interface":"formation-runtime-v0","initial_lineage_head":null,"supported_interfaces":["practice-v0","formation-procedure-v0","governance-v0","influence-v0","replay-v0"]}}\n'
    b'{"contract":"fixture-v0","coordinate":"D-C-002","record":"developmental","order":2,"event":"encounter_opened","authority":"formation_runtime","parents":["D-C-001"],"retention":"inline","payload":{"encounter":"E-C-001","candidate_object":"render-17","derived_from":"atlas","artifact_revision":41,"authority_revision":42,"depends_on_current_authority":true,"commit_action":"publish","refresh_action":"refresh_then_publish"}}\n'
    b'{"contract":"fixture-v0","coordinate":"D-C-003","record":"developmental","order":3,"event":"model_invoked","authority":"formation_runtime","parents":["D-C-002"],"retention":"inline","payload":{"encounter":"E-C-001","invocation":"I-C-001","stub":"blind-commit-v0","cold_invocation":true,"request_binding":"D-C-002","output_authority":"cold_model","output":"publish"}}\n'
    b'{"contract":"fixture-v0","coordinate":"D-C-004","record":"developmental","order":4,"event":"action_committed","authority":"formation_runtime","parents":["D-C-003"],"retention":"inline","payload":{"encounter":"E-C-001","invocation":"I-C-001","action":"A-C-001","action_name":"publish","target":"render-17"}}\n'
    b'{"contract":"fixture-v0","coordinate":"D-C-005","record":"developmental","order":5,"event":"consequence_observed","authority":"environment","parents":["D-C-004"],"retention":"inline","payload":{"encounter":"E-C-001","action":"A-C-001","consequence":"K-C-001","source":"fixture-environment-v0","outcome":"rejected","reason":"stale_dependency","observed_rule":"artifact_revision_must_equal_authority_revision"}}\n'
    b'{"contract":"fixture-v0","coordinate":"D-C-006","record":"developmental","order":6,"event":"experience_closed","authority":"formation_runtime","parents":["D-C-002","D-C-005"],"retention":"inline","payload":{"encounter":"E-C-001","included_events":["D-C-002","D-C-003","D-C-004","D-C-005"],"consequence":"K-C-001","applicability_claim":null}}\n'
)

_SOURCE_ADAPTER_ISSUER = object()


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise PrefixSourceRefusal("non_string_source_key")
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list | tuple):
        return tuple(_freeze(item) for item in value)
    if value is None or isinstance(value, str | bool | int):
        return value
    raise PrefixSourceRefusal("unsupported_source_value")


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class FixturePrefixSource:
    """Frozen adapter output from the runtime recorder at ``D-C-006``."""

    run_id: str
    source_head: str
    receipts: tuple[Mapping[str, Any], ...]
    _issuer: object


def adapt_fixture_prefix_source(
    run_id: str, receipts: Sequence[Mapping[str, Any]]
) -> FixturePrefixSource:
    """Freeze the actual six runtime receipts as the materializer source."""

    if not isinstance(run_id, str) or not run_id:
        raise PrefixSourceRefusal("invalid_run_id")
    if len(receipts) != 6:
        raise PrefixSourceRefusal("invalid_source_receipt_count")

    frozen_receipts: list[Mapping[str, Any]] = []
    for expected_coordinate, receipt in zip(_COORDINATES, receipts, strict=True):
        if not isinstance(receipt, Mapping):
            raise PrefixSourceRefusal("invalid_source_receipt")
        if set(receipt) != set(_TOP_LEVEL_FIELDS):
            raise PrefixSourceRefusal("invalid_source_envelope")
        if receipt["coordinate"] != expected_coordinate:
            raise PrefixSourceRefusal("invalid_source_coordinate")
        payload = receipt["payload"]
        if not isinstance(payload, Mapping):
            raise PrefixSourceRefusal("invalid_source_payload")
        if set(payload) != set(_PAYLOAD_FIELDS[expected_coordinate]):
            raise PrefixSourceRefusal("invalid_source_payload_fields")
        frozen_receipts.append(_freeze(receipt))

    return FixturePrefixSource(
        run_id=run_id,
        source_head=SOURCE_HEAD,
        receipts=tuple(frozen_receipts),
        _issuer=_SOURCE_ADAPTER_ISSUER,
    )


@dataclass(frozen=True)
class FrozenPrefixHandoff:
    """Typed current-run capability issued by the runtime materializer."""

    handoff_id: str
    run_id: str
    source_head: str
    materializer: str
    artifact: bytes
    _issuer: object


class RuntimePrefixMaterializer:
    """One-shot runtime owner of the fixture prefix handoff."""

    def __init__(self, run_id: str) -> None:
        if not isinstance(run_id, str) or not run_id:
            raise PrefixSourceRefusal("invalid_run_id")
        self.run_id = run_id
        self._issuer = object()
        self._current: FrozenPrefixHandoff | None = None
        self._closed = False

    def materialize(self, source: FixturePrefixSource) -> FrozenPrefixHandoff:
        if self._closed or self._current is not None:
            raise HandoffRefusal("handoff_already_issued_or_closed")
        if not isinstance(source, FixturePrefixSource):
            raise PrefixSourceRefusal("invalid_fixture_prefix_source")
        if source._issuer is not _SOURCE_ADAPTER_ISSUER:
            raise PrefixSourceRefusal("forged_fixture_prefix_source")
        if source.run_id != self.run_id or source.source_head != SOURCE_HEAD:
            raise PrefixSourceRefusal("source_run_or_head_mismatch")

        try:
            artifact = self._encode_source(source)
        except (TypeError, ValueError, UnicodeError) as error:
            raise PrefixSourceRefusal("source_not_encodable") from error
        handoff = FrozenPrefixHandoff(
            handoff_id=f"{self.run_id}:fixture-prefix:D-C-006",
            run_id=self.run_id,
            source_head=SOURCE_HEAD,
            materializer=MATERIALIZER,
            artifact=artifact,
            _issuer=self._issuer,
        )
        self._current = handoff
        return handoff

    @staticmethod
    def _encode_source(source: FixturePrefixSource) -> bytes:
        lines: list[bytes] = []
        for receipt in source.receipts:
            coordinate = receipt["coordinate"]
            payload = receipt["payload"]
            ordered = {
                key: (
                    {
                        payload_key: _thaw(payload[payload_key])
                        for payload_key in _PAYLOAD_FIELDS[coordinate]
                    }
                    if key == "payload"
                    else _thaw(receipt[key])
                )
                for key in _TOP_LEVEL_FIELDS
            }
            lines.append(
                json.dumps(
                    ordered,
                    ensure_ascii=True,
                    separators=(",", ":"),
                ).encode("ascii")
                + b"\n"
            )
        return b"".join(lines)

    def require_current(self, handoff: object) -> FrozenPrefixHandoff:
        if not isinstance(handoff, FrozenPrefixHandoff):
            raise HandoffRefusal("typed_handoff_required")
        if self._closed or self._current is not handoff:
            raise HandoffRefusal("stale_or_forged_handoff")
        if handoff._issuer is not self._issuer:
            raise HandoffRefusal("forged_handoff")
        if (
            handoff.run_id != self.run_id
            or handoff.source_head != SOURCE_HEAD
            or handoff.materializer != MATERIALIZER
        ):
            raise HandoffRefusal("handoff_run_head_or_materializer_mismatch")
        return handoff

    def close(self) -> None:
        self._closed = True


def expected_fixture_artifact() -> bytes:
    """Return the protocol-owned literal used by the fixture validator."""

    return _EXPECTED_ARTIFACT
