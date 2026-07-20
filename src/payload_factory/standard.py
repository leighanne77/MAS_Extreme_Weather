"""Standard loader + validator — enforces ADR-0013/0015 across ALL Standards.

Two invariants, checked for every Standard yaml in standards/:
1. It inherits _core (extends: _core_sections) — so it has every mandatory section.
2. The inherited citation policy requires URLs — citations are part of the deal.

A Standard that drops a required_with_content section, or fails to inherit the
citation policy, is INVALID (compile-time failure, not a review miss).
"""
from __future__ import annotations

from pathlib import Path

import yaml

STANDARDS_DIR = Path(__file__).resolve().parent / "standards"
CORE_FILE = "_core_sections.yaml"

REQUIRED_WITH_CONTENT = {
    "how_to_read", "overview", "metadata_typology", "hazard_evidence",
    "stakeholders", "scope_exclusions", "disclosure_screening", "amendment_history",
}


def load_core() -> dict:
    return yaml.safe_load((STANDARDS_DIR / CORE_FILE).read_text())


def resolve_standard(path: Path) -> dict:
    """Return a Standard with its _core sections merged in (riders appended)."""
    std = yaml.safe_load(path.read_text())
    if std.get("extends") == "_core_sections":
        core = load_core()
        std["_effective_sections"] = list(core["sections"]) + list(std.get("riders", []))
        std["_citation_policy"] = core["citation_policy"]
    else:
        std["_effective_sections"] = std.get("sections", [])
        std["_citation_policy"] = std.get("citation_policy")
    return std


def validate_standard(path: Path) -> list[str]:
    """Return a list of violations ([] means valid)."""
    std = resolve_standard(path)
    problems: list[str] = []
    ids = {s["id"] for s in std["_effective_sections"]}
    missing = REQUIRED_WITH_CONTENT - ids
    if missing:
        problems.append(f"{path.name}: missing required_with_content sections {sorted(missing)}")
    pol = std.get("_citation_policy")
    if not pol or not pol.get("url_required"):
        problems.append(f"{path.name}: citation policy absent or url_required != true")
    return problems


def all_standards() -> list[Path]:
    return sorted(p for p in STANDARDS_DIR.glob("*.yaml") if p.name != CORE_FILE)


def validate_all() -> dict[str, list[str]]:
    return {p.name: validate_standard(p) for p in all_standards()}
