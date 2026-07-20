"""Site spec — the declarative description of a site's payload inputs.

Promoted FROM sites/sr37-vallejo-ca (2026-07-15): the brief builder hand-listed
file→block-model bindings and embedded NBI segment_map/station config as literals.
This module makes that a data file (site.yaml) + one loader, so site #2 is a spec
plus curated JSONs — not a copied script. The B2 coordinator reads the same spec.

The loader validates blocks through their typed models (nothing enters unvalidated);
adapter configs (nbi/observations) are EXPOSED, not executed — the assembler decides.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from payload_factory import models as _models


class BlockFile(BaseModel):
    """One curated JSON file and the typed model(s) that validate it."""
    model_config = ConfigDict(frozen=True)
    path: str
    # EITHER a single role/model, OR a container dict of role->model (multi-block file)
    role: str | None = None
    model: str | None = None
    container: str | None = None                     # top-level key holding {role: block}
    roles: dict[str, str] = Field(default_factory=dict)  # role -> model name


class NbiConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    file: str
    route: int
    county_codes: list[int]
    segment_map: dict[str, str] = Field(default_factory=dict)


class ObservationConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    file: str
    stations: str                                    # adapter station-set name, e.g. SR37_STATIONS
    hazard: str
    accessed: date


class SiteSpec(BaseModel):
    model_config = ConfigDict(frozen=True)
    site_id: str
    name: str
    standard: str                                    # Payload Standard id (e.g. coastal_corridor)
    as_of: date
    block_files: list[BlockFile]
    observations: ObservationConfig | None = None
    nbi: NbiConfig | None = None


def load_site_spec(site_dir: str | Path) -> SiteSpec:
    return SiteSpec.model_validate(yaml.safe_load((Path(site_dir) / "site.yaml").read_text()))


def _model(name: str):
    cls = getattr(_models, name, None)
    if cls is None:
        raise ValueError(f"site.yaml references unknown block model: {name}")
    return cls


def load_site_blocks(site_dir: str | Path) -> dict:
    """Load + VALIDATE every declared block: {role: typed block instance}."""
    site_dir = Path(site_dir)
    spec = load_site_spec(site_dir)
    out: dict = {}
    for bf in spec.block_files:
        raw = (site_dir / bf.path).read_text()
        if bf.container:
            import json
            payload = json.loads(raw)[bf.container]
            for role, model_name in bf.roles.items():
                out[role] = _model(model_name).model_validate(payload[role])
        else:
            out[bf.role] = _model(bf.model).model_validate_json(raw)
    return out
