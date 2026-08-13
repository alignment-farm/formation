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
    run_id: str
    source_head: str
    binding: PrefixBinding
    artifact: bytes
    _issuer: object


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
        self._root_issuer = object()
        self._current_witness: PrefixWitness | None = None
        self._issued_roots: list[FrozenBranchRoot] = []
        self._root_snapshots: list[
            tuple[FrozenBranchRoot, str, str, str, str, PrefixBinding, bytes, object]
        ] = []
        self._consumed_roots: list[FrozenBranchRoot] = []
        self._roots_sealed = False
        self._runtime_roots_claimed = False
        self._assignment_controller: object | None = None
        self._assigned_roots: list[FrozenBranchRoot] = []
        self._assigned_labels: list[str] = []

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
        if self._roots_sealed:
            raise ForkRefusal("fork_set_already_sealed")
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

        root = FrozenBranchRoot(
            witness_coordinate=witness.coordinate,
            handoff_id=current.handoff_id,
            run_id=current.run_id,
            source_head=current.source_head,
            binding=recomputed,
            artifact=branch_artifact,
            _issuer=self._root_issuer,
        )
        self._issued_roots.append(root)
        self._root_snapshots.append(
            (
                root,
                root.witness_coordinate,
                root.handoff_id,
                root.run_id,
                root.source_head,
                PrefixBinding(
                    root.binding.materializer,
                    root.binding.identity_contract,
                    root.binding.algorithm,
                    root.binding.digest,
                    root.binding.byte_length,
                ),
                root.artifact,
                root._issuer,
            )
        )
        return root

    def seal_roots(self) -> None:
        """Freeze the fixture's three label-blind roots before assignment."""

        if self._roots_sealed:
            raise ForkRefusal("fork_set_already_sealed")
        if len(self._issued_roots) != 3:
            raise ForkRefusal("fixture_requires_three_roots")
        self._roots_sealed = True

    def require_issued_root(self, root: object) -> FrozenBranchRoot:
        if type(root) is not FrozenBranchRoot:
            raise ForkRefusal("exact_issued_root_required")
        if not self._roots_sealed:
            raise ForkRefusal("fork_set_not_sealed")
        if root._issuer is not self._root_issuer:
            raise ForkRefusal("exact_issued_root_required")
        if not any(root is issued for issued in self._issued_roots):
            raise ForkRefusal("exact_issued_root_required")
        snapshot = next(item for item in self._root_snapshots if item[0] is root)
        if (
            root.witness_coordinate != snapshot[1]
            or root.handoff_id != snapshot[2]
            or root.run_id != snapshot[3]
            or root.source_head != snapshot[4]
            or root.binding != snapshot[5]
            or root.artifact is not snapshot[6]
            or root._issuer is not snapshot[7]
        ):
            raise ForkRefusal("issued_root_changed")
        if root.run_id != self._runtime.run_id or root.source_head != SOURCE_HEAD:
            raise ForkRefusal("root_run_or_head_mismatch")
        return root

    def claim_runtime_roots(self) -> tuple[FrozenBranchRoot, ...]:
        """Return the sealed roots once, in label-blind issuance order."""

        if not self._roots_sealed:
            raise ForkRefusal("fork_set_not_sealed")
        if self._assignment_controller is not None:
            raise ForkRefusal("runtime_roots_must_precede_assignment")
        if self._runtime_roots_claimed:
            raise ForkRefusal("runtime_roots_already_claimed")
        self._runtime_roots_claimed = True
        return tuple(self.require_issued_root(root) for root in self._issued_roots)

    def consume_root(self, root: object) -> FrozenBranchRoot:
        current = self.require_issued_root(root)
        if any(current is consumed for consumed in self._consumed_roots):
            raise ForkRefusal("root_already_consumed")
        self._consumed_roots.append(current)
        return current

    def register_assignment_controller(self, controller: object) -> None:
        if not self._runtime_roots_claimed:
            raise ForkRefusal("runtime_roots_not_claimed")
        if self._assignment_controller is not None:
            raise ForkRefusal("assignment_controller_already_registered")
        self._assignment_controller = controller

    def reserve_assignment(
        self, root: object, label: str, controller: object
    ) -> FrozenBranchRoot:
        current = self.require_issued_root(root)
        if controller is not self._assignment_controller:
            raise ForkRefusal("exact_assignment_controller_required")
        if any(current is assigned for assigned in self._assigned_roots):
            raise ForkRefusal("root_already_assigned")
        if label in self._assigned_labels:
            raise ForkRefusal("fixture_label_already_assigned")
        self._assigned_roots.append(current)
        self._assigned_labels.append(label)
        return current

    def require_roots_in_issuance_order(
        self, controller: object
    ) -> tuple[FrozenBranchRoot, ...]:
        """Return the complete assigned root set in its label-blind order."""

        if controller is not self._assignment_controller:
            raise ForkRefusal("exact_assignment_controller_required")
        if len(self._assigned_roots) != 3 or len(self._assigned_labels) != 3:
            raise ForkRefusal("fixture_assignments_incomplete")
        return tuple(self.require_issued_root(root) for root in self._issued_roots)
