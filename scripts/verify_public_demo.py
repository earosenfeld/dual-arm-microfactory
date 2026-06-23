from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

from microfactory.demo.package import build_demo_package


TIMESTAMP_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+00:00")
TEXT_SUFFIXES = {".html", ".json", ".md", ".txt", ".js", ".css", ".svg"}


def normalized_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return data
    text = data.decode("utf-8")
    return TIMESTAMP_RE.sub("<TIMESTAMP>", text).encode("utf-8")


def relative_files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and path.name not in {".DS_Store"}
    }


def compare_trees(expected: Path, actual: Path) -> list[str]:
    expected_files = relative_files(expected)
    actual_files = relative_files(actual)
    errors: list[str] = []

    for missing in sorted(expected_files - actual_files):
        errors.append(f"missing generated file: {missing}")
    for extra in sorted(actual_files - expected_files):
        errors.append(f"unexpected generated file: {extra}")

    for relative in sorted(expected_files & actual_files):
        expected_bytes = normalized_bytes(expected / relative)
        actual_bytes = normalized_bytes(actual / relative)
        if expected_bytes != actual_bytes:
            errors.append(f"generated file differs: {relative}")

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    committed_demo = repo_root / "docs" / "demo"
    if not committed_demo.exists():
        print("docs/demo does not exist; run PYTHONPATH=src python3 -m microfactory demo", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        generated_demo = Path(tmp) / "demo"
        build_demo_package(generated_demo)
        errors = compare_trees(generated_demo, committed_demo)

    if errors:
        print("Committed docs/demo is out of sync with the demo generator:", file=sys.stderr)
        for error in errors[:40]:
            print(f"- {error}", file=sys.stderr)
        if len(errors) > 40:
            print(f"- ... {len(errors) - 40} more differences", file=sys.stderr)
        print(
            "Regenerate with: PYTHONPATH=src python3 -m microfactory demo --output-dir docs/demo",
            file=sys.stderr,
        )
        return 1

    print("docs/demo matches a freshly generated demo package.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
