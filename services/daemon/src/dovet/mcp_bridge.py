"""Small stdio MCP bridge to the independent local Dovet daemon."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

from . import __version__

SERVER_URL = "http://127.0.0.1:4317"
DATA_ROOT = Path.home() / "Library" / "Application Support" / "Dovet"

server = MCPServer(
    name="dovet",
    title="Dovet",
    description="Inspect Dovet-managed coding work and open the local evidence console.",
    version=__version__,
)


class DaemonUnavailable(RuntimeError):
    pass


def _token() -> str:
    try:
        token = (DATA_ROOT / "bridge-token").read_text(encoding="utf-8").strip()
    except OSError as error:
        raise DaemonUnavailable(
            "Dovet service is not initialized. Run `dovet init-state` and `dovet serve`."
        ) from error
    if len(token) < 32:
        raise DaemonUnavailable("Dovet bridge credential is invalid; reinstall the local service.")
    return token


def _request(path: str, *, method: str = "GET") -> dict[str, Any]:
    request = urllib.request.Request(
        SERVER_URL + path,
        method=method,
        headers={"Accept": "application/json", "X-Dovet-Bridge": _token()},
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:  # noqa: S310
            value = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.HTTPError, json.JSONDecodeError) as error:
        raise DaemonUnavailable(
            "The independent Dovet service is unavailable. Run `dovet service status`."
        ) from error
    if not isinstance(value, dict):
        raise DaemonUnavailable("Dovet service returned an invalid response.")
    return value


@server.tool(structured_output=True)
def dovet_status() -> dict[str, Any]:
    """Return current persisted Dovet work, decisions and history readiness."""
    return _request("/api/v1/status")


@server.tool(structured_output=True)
def dovet_open_console() -> dict[str, Any]:
    """Return a short-lived owner pairing URL for the loopback Dovet console."""
    return _request("/api/v1/session/issue", method="POST")


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
