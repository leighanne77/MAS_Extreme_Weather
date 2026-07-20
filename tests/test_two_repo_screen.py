"""Two-repo screen guard — private-side names must NEVER appear in this public repo.

Scans every git-tracked text file for the screened names. The names are
assembled from parts so this file cannot flag itself. Runs under pytest or
standalone:  python3 tests/test_two_repo_screen.py
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

# Screened names, split so this file never matches its own patterns.
_SCREENED = [
    "E" + "VE",          # former private product name (still screened)
    "EG" + "ON",         # private product name
    "Aus" + "tal",       # customer/site name
    "D" + "IN",          # private network name
    "A" + "RA",          # private project name
    "Rip" + "ley",       # private brand/account name
]
# Word-bounded, case-sensitive (uppercase acronyms; 'Austal'/'Ripley' as proper nouns).
_PATTERN = re.compile(r"\b(?:" + "|".join(_SCREENED) + r")\b")

_SELF = Path(__file__).resolve()


def _tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=_ROOT, capture_output=True,
                         text=True, check=True).stdout
    return [_ROOT / line for line in out.splitlines() if line]


def test_no_screened_names_in_tracked_files():
    offenders: list[str] = []
    for path in _tracked_files():
        if path == _SELF or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable — filenames are still checked below
        for i, line in enumerate(text.splitlines(), 1):
            if _PATTERN.search(line):
                offenders.append(f"{path.relative_to(_ROOT)}:{i}: {line.strip()[:100]}")
    assert not offenders, (
        "Two-repo screen violation — screened private names found in public tracked files:\n"
        + "\n".join(offenders[:40])
    )


def test_no_screened_names_in_tracked_filenames():
    bad = [str(p.relative_to(_ROOT)) for p in _tracked_files() if _PATTERN.search(p.name)]
    assert not bad, "Screened names in tracked filenames:\n" + "\n".join(bad)


if __name__ == "__main__":
    test_no_screened_names_in_tracked_files()
    test_no_screened_names_in_tracked_filenames()
    print("two-repo screen: CLEAN")
