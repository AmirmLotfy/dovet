"""Supported managed Codex adapter. It never touches Codex auth storage."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai_codex import ApprovalMode, Codex, CodexConfig, Sandbox, TurnHandle


@dataclass(frozen=True)
class ManagedCodexResult:
    thread_id: str
    turn_id: str | None
    final_response: str


@dataclass(frozen=True)
class ManagedCodexTurn:
    thread_id: str
    turn_id: str


class ManagedCodexAdapter:
    def __init__(self, codex_bin: str | None = None) -> None:
        self.config = CodexConfig(
            codex_bin=codex_bin,
            client_name="dovet",
            client_title="Dovet managed worker",
            client_version="0.1.0",
            experimental_api=False,
        )
        self._codex: Codex | None = None
        self._threads: dict[str, Any] = {}
        self._turns: dict[str, TurnHandle] = {}

    def __enter__(self) -> ManagedCodexAdapter:
        self._codex = Codex(self.config)
        self._codex.__enter__()
        return self

    def __exit__(self, *args: object) -> None:
        if self._codex is not None:
            self._codex.__exit__(*args)
            self._codex = None

    def start(self, *, cwd: Path, prompt: str, model: str | None = None) -> ManagedCodexResult:
        managed = self.start_turn(cwd=cwd, prompt=prompt, model=model)
        return self.finish(managed)

    def start_turn(
        self, *, cwd: Path, prompt: str, model: str | None = None
    ) -> ManagedCodexTurn:
        """Start an owned turn and return before its event stream completes."""
        if self._codex is None:
            raise RuntimeError("adapter must be used as a context manager")
        thread = self._codex.thread_start(
            cwd=str(cwd),
            model=model,
            sandbox=Sandbox.workspace_write,
            approval_mode=ApprovalMode.deny_all,
            base_instructions=(
                "You are a Dovet-managed coding worker. Stay inside the supplied "
                "task and workspace. "
                "Do not commit, push, deploy, change credentials, or modify protected tests."
            ),
        )
        thread_id = str(thread.id)
        turn = thread.turn(prompt)
        self._threads[thread_id] = thread
        self._turns[thread_id] = turn
        return ManagedCodexTurn(thread_id=thread_id, turn_id=turn.id)

    def finish(self, managed: ManagedCodexTurn) -> ManagedCodexResult:
        turn = self._turns.get(managed.thread_id)
        if turn is None or turn.id != managed.turn_id:
            raise KeyError("Dovet does not own this Codex turn")
        result = turn.run()
        return ManagedCodexResult(
            thread_id=managed.thread_id,
            turn_id=managed.turn_id,
            final_response=result.final_response or "",
        )

    def interrupt(self, thread_id: str) -> None:
        turn = self._turns.get(thread_id)
        if turn is None:
            raise KeyError("Dovet does not own this Codex thread")
        turn.interrupt()
