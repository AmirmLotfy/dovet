from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dovet.artifacts import ArtifactStore
from dovet.checkpoints import CheckpointEngine
from dovet.processes import ProcessManager


def test_owned_interruption_leaves_recoverable_checkpoint(tmp_path: Path) -> None:
    source = tmp_path / "managed"
    source.mkdir()
    target = source / "work.txt"
    script = (
        "from pathlib import Path; import time; "
        "Path('work.txt').write_text('preserved working state'); time.sleep(30)"
    )
    manager = ProcessManager()
    owned = manager.start(
        (sys.executable, "-c", script),
        cwd=source,
        environment={"PATH": os.environ["PATH"], "PYTHONDONTWRITEBYTECODE": "1"},
    )
    deadline = time.monotonic() + 5
    while not target.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert target.read_text() == "preserved working state"
    assert manager.stop_confirmed(owned)

    engine = CheckpointEngine(ArtifactStore(tmp_path / "store"))
    checkpoint = engine.capture(
        root=source,
        paths=["work.txt"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    recovered = tmp_path / "recovered"
    engine.restore(checkpoint, recovered)
    assert (recovered / "work.txt").read_text() == "preserved working state"
    assert target.read_text() == "preserved working state"
