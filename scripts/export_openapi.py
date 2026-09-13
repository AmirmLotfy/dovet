"""Export the authoritative FastAPI contract for TypeScript generation."""

from __future__ import annotations

import json
from pathlib import Path

from dovet.api import app


def main() -> None:
    target = Path(__file__).resolve().parents[1] / "packages" / "contracts" / "openapi.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {target.relative_to(target.parents[2])}")


if __name__ == "__main__":
    main()
