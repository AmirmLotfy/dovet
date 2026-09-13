"""Remove machine identity from a JUnit report before it becomes release evidence."""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    tree = ET.parse(args.path)  # noqa: S314
    for suite in tree.getroot().iter("testsuite"):
        suite.set("hostname", "local-test-host")
    tree.write(args.path, encoding="utf-8", xml_declaration=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
