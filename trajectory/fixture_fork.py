"""Harness-owned validation and fork check for the first fixture prefix."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from formation.fixture_prefix import (
    FrozenPrefixHandoff,
    MATERIALIZER,
    RuntimePrefixMaterializer,
    SOURCE_HEAD,
    expected_fixture_artifact,
)


IDENTITY_CONTRACT = "fixture-v0-prefix-identity-v0"
ALGORITHM = "sha-256"
WITNESS_COORDINATE = "T-C-002"


class PrefixValidationRefusal(ValueError):
    """The producer artifact is not the frozen fixture artifact."""


class ForkRefusal(ValueError):
    """A branch cannot bind to the witnessed prefix."""


@dataclass(frozen=True)
class PrefixBinding:
    materializer: str
    identity_contract: str
    algorithm: str
    digest: str
    byte_length: int

    def require_valid(self) -> None:
        if self.materializer != MATERIALIZER:
            raise ForkRefusal("unknown_materializer")
        if self.identity_contract != IDENTITY_CONTRACT:
            raise ForkRefusal("unknown_identity_contract")
        if self.algorithm != ALGORITHM:
            raise ForkRefusal("unknown_digest_algorithm")
        if (
            not isinstance(self.digest, str)
            or len(self.digest) != 64
            or self.digest != self.digest.lower()
            or any(character not in "0123456789abcdef" for character in self.digest)
        ):
            raise ForkRefusal("invalid_digest_encoding")
        if not isinstance(self.byte_length, int) or isinstance(self.byte_length, bool):
            raise ForkRefusal("invalid_byte_length_type")
        if self.byte_length < 0:
            raise ForkRefusal("invalid_byte_length")


@dataclass(frozen=True)
class PrefixWitness:
    coordinate: str
    handoff_id: str
    run_id: str
    source_head: str
    binding: PrefixBinding
    _issuer: object


@dataclass(frozen=True)
class FrozenBranchRoot:
    witness_coordinate: str
    handoff_id: str
    source_head: str
    binding: PrefixBinding
    artifact: bytes


def validate_fixture_prefix(artifact: object) -> str:
    """Fail closed without parsing, normalizing, or repairing producer bytes."""

    if not isinstance(artifact, bytes) or artifact != expected_fixture_artifact():
        raise PrefixValidationRefusal("invalid_fixture_prefix_bytes")
    return "valid_fixture_prefix_bytes"


def compute_binding(artifact: bytes) -> PrefixBinding:
    return PrefixBinding(
        materializer=MATERIALIZER,
        identity_contract=IDENTITY_CONTRACT,
        algorithm=ALGORITHM,
        digest=hashlib.sha256(artifact).hexdigest(),
        byte_length=len(artifact),
    )


class ForkController:
    """Harness controller constrained to one runtime-issued handoff."""

    def __init__(self, runtime: RuntimePrefixMaterializer) -> None:
        self._runtime = runtime
        self._issuer = object()
        self._current_witness: PrefixWitness | None = None

    def witness(self, handoff: object) -> PrefixWitness:
        if self._current_witness is not None:
            raise ForkRefusal("prefix_witness_already_issued")
        current = self._runtime.require_current(handoff)
        validate_fixture_prefix(current.artifact)
        binding = compute_binding(current.artifact)
        binding.require_valid()
        witness = PrefixWitness(
            coordinate=WITNESS_COORDINATE,
            handoff_id=current.handoff_id,
            run_id=current.run_id,
            source_head=current.source_head,
            binding=binding,
            _issuer=self._issuer,
        )
        self._current_witness = witness
        return witness

    def fork(
        self,
        handoff: object,
        witness: object,
        claimed_binding: object,
    ) -> FrozenBranchRoot:
        current = self._runtime.require_current(handoff)
        if not isinstance(witness, PrefixWitness):
            raise ForkRefusal("exact_prefix_witness_required")
        if witness is not self._current_witness or witness._issuer is not self._issuer:
            raise ForkRefusal("exact_prefix_witness_required")
        if type(claimed_binding) is not PrefixBinding:
            raise ForkRefusal("complete_prefix_binding_required")
        claimed_binding.require_valid()

        if (
            witness.coordinate != WITNESS_COORDINATE
            or witness.handoff_id != current.handoff_id
            or witness.run_id != current.run_id
            or witness.source_head != SOURCE_HEAD
        ):
            raise ForkRefusal("witness_handoff_mismatch")
        if witness.binding != claimed_binding:
            raise ForkRefusal("claimed_binding_mismatch")

        branch_artifact = current.artifact
        if branch_artifact != current.artifact:
            raise ForkRefusal("branch_bytes_differ")
        recomputed = compute_binding(branch_artifact)
        if recomputed != witness.binding:
            raise ForkRefusal("branch_binding_mismatch")

        return FrozenBranchRoot(
            witness_coordinate=witness.coordinate,
            handoff_id=current.handoff_id,
            source_head=current.source_head,
            binding=recomputed,
            artifact=branch_artifact,
        )
