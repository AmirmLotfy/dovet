-- Dovet local schema v1. Starting migration, not a cloud tenancy schema.
-- Apply on a fresh database. Use migrations for later changes.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

CREATE TABLE schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL,
  checksum TEXT NOT NULL
);
CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  root_path TEXT NOT NULL UNIQUE,
  root_fingerprint TEXT NOT NULL,
  trust_state TEXT NOT NULL CHECK(trust_state IN ('untrusted','approved','revoked')),
  mode TEXT NOT NULL CHECK(mode IN ('managed','observed')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  archived_at TEXT
);
CREATE TABLE project_policies (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,
  version INTEGER NOT NULL CHECK(version > 0),
  body_json TEXT NOT NULL CHECK(json_valid(body_json)),
  digest TEXT NOT NULL CHECK(length(digest)=64),
  approved_at TEXT,
  approved_by TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(project_id,version)
);
CREATE TABLE provider_profiles (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  provider_kind TEXT NOT NULL CHECK(provider_kind IN ('codex','bedrock')),
  enabled INTEGER NOT NULL DEFAULT 0 CHECK(enabled IN (0,1)),
  config_json TEXT NOT NULL CHECK(json_valid(config_json)),
  credential_ref TEXT,
  capability_json TEXT NOT NULL DEFAULT '{}' CHECK(json_valid(capability_json)),
  last_probed_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,
  policy_id TEXT NOT NULL REFERENCES project_policies(id) ON DELETE RESTRICT,
  title TEXT NOT NULL,
  objective TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0),
  acceptance_json TEXT NOT NULL CHECK(json_valid(acceptance_json)),
  scope_json TEXT NOT NULL CHECK(json_valid(scope_json)),
  status TEXT NOT NULL CHECK(status IN ('draft','ready','running','paused','verified','failed','cancelled')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE runs (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE RESTRICT,
  provider_profile_id TEXT NOT NULL REFERENCES provider_profiles(id) ON DELETE RESTRICT,
  parent_run_id TEXT REFERENCES runs(id) ON DELETE RESTRICT,
  attempt INTEGER NOT NULL CHECK(attempt > 0),
  mode TEXT NOT NULL CHECK(mode IN ('managed','observed','demo_live','demo_replay')),
  status TEXT NOT NULL CHECK(status IN ('queued','starting','running','waiting_tool','waiting_human','pausing','checkpointing','interrupted','recovering','verifying','verified','failed','cancelled')),
  base_commit TEXT NOT NULL,
  worktree_path TEXT,
  external_thread_id TEXT,
  external_turn_id TEXT,
  pid INTEGER,
  process_birth_id TEXT,
  task_version INTEGER NOT NULL,
  started_at TEXT,
  ended_at TEXT,
  stop_reason TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(task_id,attempt)
);
CREATE TABLE run_events (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE RESTRICT,
  seq INTEGER NOT NULL CHECK(seq >= 1),
  event_type TEXT NOT NULL,
  source_kind TEXT NOT NULL CHECK(source_kind IN ('adapter','filesystem','verifier','supervisor','policy','human','system')),
  knowledge_kind TEXT NOT NULL CHECK(knowledge_kind IN ('observed','reported','inferred','verified')),
  source_event_id TEXT,
  payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
  observed_at TEXT NOT NULL,
  duration_ms INTEGER CHECK(duration_ms IS NULL OR duration_ms>=0),
  UNIQUE(run_id,seq),
  UNIQUE(run_id,source_kind,source_event_id)
);
CREATE TABLE artifacts (
  id TEXT PRIMARY KEY,
  sha256 TEXT NOT NULL CHECK(length(sha256)=64),
  size_bytes INTEGER NOT NULL CHECK(size_bytes>=0),
  kind TEXT NOT NULL CHECK(kind IN ('blob','patch','manifest','handoff','log','test_report','trace','recording')),
  media_type TEXT NOT NULL,
  storage_kind TEXT NOT NULL CHECK(storage_kind IN ('local','s3')),
  storage_ref TEXT NOT NULL,
  redaction_state TEXT NOT NULL CHECK(redaction_state IN ('not_reviewed','local_only','cleared','blocked')),
  created_at TEXT NOT NULL,
  expires_at TEXT,
  UNIQUE(storage_kind,storage_ref)
);
CREATE TABLE checkpoints (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE RESTRICT,
  policy_id TEXT NOT NULL REFERENCES project_policies(id) ON DELETE RESTRICT,
  task_version INTEGER NOT NULL,
  format_version TEXT NOT NULL DEFAULT 'DovetCheckpoint/1',
  state TEXT NOT NULL CHECK(state IN ('staging','ready','incomplete','corrupt','quarantined')),
  manifest_artifact_id TEXT REFERENCES artifacts(id) ON DELETE RESTRICT,
  handoff_artifact_id TEXT REFERENCES artifacts(id) ON DELETE RESTRICT,
  snapshot_sha256 TEXT NOT NULL CHECK(length(snapshot_sha256)=64),
  summary TEXT NOT NULL,
  created_at TEXT NOT NULL,
  validated_at TEXT
);
CREATE TABLE checkpoint_files (
  checkpoint_id TEXT NOT NULL REFERENCES checkpoints(id) ON DELETE RESTRICT,
  relative_path TEXT NOT NULL,
  operation TEXT NOT NULL CHECK(operation IN ('add','modify','delete','unchanged')),
  artifact_id TEXT REFERENCES artifacts(id) ON DELETE RESTRICT,
  source_sha256 TEXT CHECK(source_sha256 IS NULL OR length(source_sha256)=64),
  file_mode INTEGER NOT NULL,
  PRIMARY KEY(checkpoint_id,relative_path),
  CHECK(operation='delete' OR artifact_id IS NOT NULL)
);
CREATE TABLE workspace_leases (
  workspace_key TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE RESTRICT,
  generation INTEGER NOT NULL CHECK(generation>0),
  owner_instance_id TEXT NOT NULL,
  process_birth_id TEXT,
  acquired_at TEXT NOT NULL,
  heartbeat_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  prior_writer_stopped_at TEXT
);
CREATE TABLE actions (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE RESTRICT,
  checkpoint_id TEXT REFERENCES checkpoints(id) ON DELETE RESTRICT,
  policy_id TEXT NOT NULL REFERENCES project_policies(id) ON DELETE RESTRICT,
  kind TEXT NOT NULL CHECK(kind IN ('resume','restart','handoff','verify','pause','ask_human')),
  request_json TEXT NOT NULL CHECK(json_valid(request_json)),
  explanation TEXT NOT NULL,
  evidence_ids_json TEXT NOT NULL CHECK(json_valid(evidence_ids_json)),
  digest TEXT NOT NULL CHECK(length(digest)=64),
  idempotency_key TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL CHECK(status IN ('proposed','denied','awaiting_approval','authorized','dispatching','acknowledged','completed','failed','expired')),
  lease_generation INTEGER,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  dispatched_at TEXT
);
CREATE TABLE approvals (
  id TEXT PRIMARY KEY,
  action_id TEXT NOT NULL UNIQUE REFERENCES actions(id) ON DELETE RESTRICT,
  action_digest TEXT NOT NULL CHECK(length(action_digest)=64),
  snapshot_sha256 TEXT NOT NULL CHECK(length(snapshot_sha256)=64),
  nonce_hash TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL CHECK(status IN ('pending','approved','denied','expired','consumed')),
  actor_id TEXT,
  expires_at TEXT NOT NULL,
  decided_at TEXT,
  consumed_at TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE verifications (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE RESTRICT,
  checkpoint_id TEXT NOT NULL REFERENCES checkpoints(id) ON DELETE RESTRICT,
  profile_digest TEXT NOT NULL CHECK(length(profile_digest)=64),
  suite_digest TEXT NOT NULL CHECK(length(suite_digest)=64),
  snapshot_sha256 TEXT NOT NULL CHECK(length(snapshot_sha256)=64),
  status TEXT NOT NULL CHECK(status IN ('queued','running','passed','failed','blocked','tampered')),
  started_at TEXT,
  ended_at TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE verification_checks (
  id TEXT PRIMARY KEY,
  verification_id TEXT NOT NULL REFERENCES verifications(id) ON DELETE RESTRICT,
  criterion_id TEXT NOT NULL,
  command_id TEXT NOT NULL,
  argv_json TEXT NOT NULL CHECK(json_valid(argv_json)),
  status TEXT NOT NULL CHECK(status IN ('queued','running','passed','failed','blocked','timeout')),
  exit_code INTEGER,
  duration_ms INTEGER CHECK(duration_ms IS NULL OR duration_ms>=0),
  output_artifact_id TEXT REFERENCES artifacts(id) ON DELETE RESTRICT,
  started_at TEXT,
  ended_at TEXT
);
CREATE TABLE usage_samples (
  id TEXT PRIMARY KEY,
  provider_profile_id TEXT NOT NULL REFERENCES provider_profiles(id) ON DELETE RESTRICT,
  observed_at TEXT NOT NULL,
  source TEXT NOT NULL,
  limit_id TEXT,
  window_minutes INTEGER CHECK(window_minutes IS NULL OR window_minutes>0),
  used_percent REAL CHECK(used_percent IS NULL OR (used_percent>=0 AND used_percent<=100)),
  resets_at TEXT,
  state TEXT NOT NULL CHECK(state IN ('known','unknown','stale','unavailable')),
  raw_artifact_id TEXT REFERENCES artifacts(id) ON DELETE RESTRICT
);
CREATE TABLE budget_accounts (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,
  period_start TEXT NOT NULL,
  period_end TEXT NOT NULL,
  currency TEXT NOT NULL DEFAULT 'USD' CHECK(currency='USD'),
  ceiling_microusd INTEGER NOT NULL CHECK(ceiling_microusd>=0),
  unknown_cost_action TEXT NOT NULL CHECK(unknown_cost_action IN ('pause','ask_human')),
  approved_at TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE budget_reservations (
  id TEXT PRIMARY KEY,
  budget_account_id TEXT NOT NULL REFERENCES budget_accounts(id) ON DELETE RESTRICT,
  action_id TEXT NOT NULL UNIQUE REFERENCES actions(id) ON DELETE RESTRICT,
  amount_microusd INTEGER NOT NULL CHECK(amount_microusd>=0),
  status TEXT NOT NULL CHECK(status IN ('held','settled','released','uncertain')),
  created_at TEXT NOT NULL,
  settled_at TEXT
);
CREATE TABLE cost_entries (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE RESTRICT,
  provider_profile_id TEXT NOT NULL REFERENCES provider_profiles(id) ON DELETE RESTRICT,
  provider_request_id TEXT,
  reservation_id TEXT REFERENCES budget_reservations(id) ON DELETE RESTRICT,
  basis TEXT NOT NULL CHECK(basis IN ('provider_reported','estimated','unknown')),
  amount_microusd INTEGER CHECK(amount_microusd IS NULL OR amount_microusd>=0),
  input_tokens INTEGER CHECK(input_tokens IS NULL OR input_tokens>=0),
  output_tokens INTEGER CHECK(output_tokens IS NULL OR output_tokens>=0),
  price_card_version TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(provider_profile_id,provider_request_id),
  CHECK(basis!='unknown' OR amount_microusd IS NULL)
);
CREATE INDEX idx_runs_task_status ON runs(task_id,status);
CREATE INDEX idx_events_run_seq ON run_events(run_id,seq);
CREATE INDEX idx_checkpoints_run_time ON checkpoints(run_id,created_at);
CREATE INDEX idx_actions_status ON actions(status,created_at);
CREATE INDEX idx_approvals_pending ON approvals(status,expires_at);
CREATE INDEX idx_usage_profile_time ON usage_samples(provider_profile_id,observed_at);
CREATE INDEX idx_cost_run ON cost_entries(run_id,created_at);
CREATE INDEX idx_artifact_sha ON artifacts(sha256);

-- Source lineage must remain within the task.
CREATE TRIGGER validate_run_parent BEFORE INSERT ON runs
WHEN NEW.parent_run_id IS NOT NULL AND
 (SELECT task_id FROM runs WHERE id=NEW.parent_run_id) != NEW.task_id
BEGIN SELECT RAISE(ABORT,'parent run belongs to another task'); END;
CREATE TRIGGER validate_task_policy BEFORE INSERT ON tasks
WHEN (SELECT project_id FROM project_policies WHERE id=NEW.policy_id) != NEW.project_id
BEGIN SELECT RAISE(ABORT,'policy belongs to another project'); END;
-- Immutable evidence tables are append-only through the application. Deletion is
-- implemented by explicit retention workflows, not cascading source deletion.
