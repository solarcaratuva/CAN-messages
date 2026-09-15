#!/usr/bin/env python3
"""Run generate.py (which now also runs cantools generate_c_source) for every DBC file in the repo."""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def find_dbc_files(root: Path) -> list[Path]:
    """Locate all .dbc files to process."""
    return sorted(root.glob("*.dbc"))


def run_generate(dbc_path: Path) -> None:
    """Equivalent of `python generate.py {path}`, which produces both the
    cantools pack/unpack .c/.h and the <Name>CanStructs.h wrapper header."""
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "generate.py"), str(dbc_path)],
        cwd=REPO_ROOT,
        check=True,
    )


def main() -> None:
    dbc_files = find_dbc_files(REPO_ROOT)
    if not dbc_files:
        print("ERROR: no .dbc files found in REPO ROOT")
        return

    failures = []
    for dbc_path in dbc_files:
        print(f"=== {dbc_path.name} ===")
        try:
            run_generate(dbc_path)
        except subprocess.CalledProcessError as exc:
            failures.append(dbc_path.name)
            print(f"ERROR: {dbc_path.name} failed: {exc}")

    print("Done" if not failures else f"Done, but failed: {failures}")


if __name__ == "__main__":
    main()
