"""Typed public contracts. These models are the API source of truth."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Sha256 = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
OpaqueId = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")]


def utc_now() -> datetime:
    return datetime.now(UTC)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class KnowledgeKind(StrEnum):
    OBSERVED = "observed"
    REPORTED = "reported"
    INFERRED = "inferred"
    VERIFIED = "verified"


class RunStatus(StrEnum):
    QUEUED = "queued"
    STARTING = "starting"
    RUNNING = "running"
    WAITING_TOOL = "waiting_tool"
    WAITING_HUMAN = "waiting_human"
    PAUSING = "pausing"
    CHECKPOINTING = "checkpointing"
    INTERRUPTED = "interrupted"
    RECOVERING = "recovering"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunEvent(StrictModel):
    id: OpaqueId
    run_id: OpaqueId
    seq: Annotated[int, Field(ge=1)]
    type: Annotated[str, Field(min_length=1, max_length=100)]
    source_kind: Literal[
        "adapter", "filesystem", "verifier", "supervisor", "policy", "human", "system"
    ]
    knowledge_kind: KnowledgeKind
    observed_at: datetime = Field(default_factory=utc_now)
    payload: dict[str, object] = Field(default_factory=dict)
    trace_id: OpaqueId | None = None


class ManifestFile(StrictModel):
    path: Annotated[str, Field(min_length=1, max_length=1024)]
    operation: Literal["add", "modify", "delete", "unchanged"]
    sha256: Sha256 | None
    size_bytes: Annotated[int, Field(ge=0)]
    mode: Annotated[int, Field(ge=0, le=0o777)]

    @field_validator("path")
    @classmethod
    def reject_unsafe_path(cls, value: str) -> str:
        if "\x00" in value or value.startswith(("/", "\\")):
            raise ValueError("manifest path must be relative")
        parts = value.replace("\\", "/").split("/")
        if any(part in {"", ".", ".."} for part in parts):
            raise ValueError("manifest path contains an unsafe segment")
        return "/".join(parts)


class CheckpointManifest(StrictModel):
    version: Literal["DovetManifest/1"] = "DovetManifest/1"
    run_id: OpaqueId
    task_version: Annotated[int, Field(ge=1)]
    policy_sha256: Sha256
    base_commit: Annotated[str, Field(min_length=1, max_length=128)]
    files: Annotated[list[ManifestFile], Field(max_length=5000)]

    @field_validator("files")
    @classmethod
    def sort_and_reject_duplicates(cls, files: list[ManifestFile]) -> list[ManifestFile]:
        paths = [file.path for file in files]
        if len(paths) != len(set(paths)):
            raise ValueError("duplicate manifest paths")
        if paths != sorted(paths):
            raise ValueError("manifest files must be sorted by path")
        return files


class Checkpoint(StrictModel):
    version: Literal["DovetCheckpoint/1"] = "DovetCheckpoint/1"
    id: OpaqueId
    manifest: CheckpointManifest
    snapshot_sha256: Sha256
    completeness: Literal["ready", "incomplete", "corrupt", "quarantined"]
    decisions: list[str] = Field(default_factory=list, max_length=50)
    failed_attempts: list[str] = Field(default_factory=list, max_length=50)
    next_steps: list[str] = Field(default_factory=list, max_length=50)
    evidence_ids: list[OpaqueId] = Field(default_factory=list, max_length=100)


class RecoveryAction(StrEnum):
    RESUME = "resume"
    RESTART = "restart"
    HANDOFF = "handoff"
    VERIFY = "verify"
    PAUSE = "pause"
    ASK_HUMAN = "ask_human"


class RecoveryDecision(StrictModel):
    version: Literal["DovetRecovery/1"] = "DovetRecovery/1"
    incident_id: OpaqueId = Field(alias="incidentId")
    run_id: OpaqueId = Field(alias="runId")
    action: RecoveryAction
    checkpoint_id: OpaqueId | None = Field(alias="checkpointId")
    target_provider_profile_id: OpaqueId | None = Field(alias="targetProviderProfileId")
    expected_snapshot_sha256: Sha256 | None = Field(alias="expectedSnapshotSha256")
    expected_policy_sha256: Sha256 = Field(alias="expectedPolicySha256")
    evidence_ids: Annotated[list[OpaqueId], Field(min_length=1, max_length=30)] = Field(
        alias="evidenceIds"
    )
    explanation: Annotated[str, Field(min_length=1, max_length=1500)]
    uncertainties: Annotated[list[str], Field(max_length=15)] = Field(default_factory=list)
    preconditions: list[
        Literal[
            "writer_stopped",
            "snapshot_valid",
            "policy_unchanged",
            "scope_permitted",
            "provider_ready",
            "budget_reserved",
            "approval_consumable",
            "verification_profile_trusted",
        ]
    ] = Field(default_factory=list, max_length=15)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Capability(StrictModel):
    name: str
    status: Literal["ready", "blocked", "unavailable", "unverified"]
    detail: str


class HealthResponse(StrictModel):
    version: str
    readiness: Literal["ready", "degraded", "blocked"]
    capability_digest: Sha256
    capabilities: list[Capability]


class UsageWindowView(StrictModel):
    limit_id: str
    window: Literal["primary", "secondary"]
    used_percent: Annotated[float, Field(ge=0, le=100)]
    remaining_percent: Annotated[float, Field(ge=0, le=100)]
    window_minutes: Annotated[int, Field(gt=0)] | None
    resets_at: int | None


class UsageAdviceView(StrictModel):
    level: Literal["normal", "prepare", "pause", "critical", "unknown"]
    checkpoint_requested: bool
    pause_managed_run_requested: bool
    reason: str


class UsageResponse(StrictModel):
    observed_at: datetime
    state: Literal["known", "unknown", "stale", "unavailable"]
    windows: list[UsageWindowView]
    source: Literal["codex-app-server"]
    error: str | None
    advice: UsageAdviceView


class RunEvidenceEventView(StrictModel):
    id: OpaqueId
    seq: Annotated[int, Field(ge=1)]
    title: Annotated[str, Field(min_length=1, max_length=160)]
    detail: Annotated[str, Field(min_length=1, max_length=1000)]
    knowledge_kind: KnowledgeKind


class RunVerificationView(StrictModel):
    status: Literal["passed"]
    snapshot_sha256: Sha256
    suite_digest: Sha256
    output_sha256: Sha256
    duration_ms: Annotated[int, Field(ge=0)]


class RunEvidenceView(StrictModel):
    run_id: OpaqueId
    title: Annotated[str, Field(min_length=1, max_length=160)]
    project: Annotated[str, Field(min_length=1, max_length=160)]
    status: Literal["verified"]
    source: Literal["live_receipt"]
    recorded_at: datetime
    release_commit: Annotated[str, Field(pattern=r"^[a-f0-9]{40}$")]
    model_id: Annotated[str, Field(min_length=1, max_length=200)]
    codex_thread_id: OpaqueId
    codex_turn_id: OpaqueId
    initial_snapshot_sha256: Sha256
    final_snapshot_sha256: Sha256
    changed_paths: Annotated[list[str], Field(max_length=30)]
    verification: RunVerificationView
    events: Annotated[list[RunEvidenceEventView], Field(min_length=1, max_length=30)]
