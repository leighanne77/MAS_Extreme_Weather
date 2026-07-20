"""Site Inventory Record (SIR) — the per-site facts backbone.

One record per registered site: canonical FACTS (identity, geometry, the bioregion
classification that carries the two axis selections) + the typed fact-blocks. Nothing
about opportunities/ROI/page copy — the single source every stamp reads FROM
(MAS_Two_Inventories: FROM_SIR). Assembled from pieces that already exist:
  SiteSpec (site.yaml)  ·  load_site_blocks (typed blocks)  ·  classification_for_site.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from enums import EcologicalArchetype, SiteStructure
from payload_factory.axes import geometry_block_class
from payload_factory.models import AssetBlock, BioregionClassification, SegmentationBlock
from payload_factory.site_spec import load_site_blocks, load_site_spec
from payload_factory.tools.bioregion import classification_for_site

_SITES = Path(__file__).resolve().parents[2] / "sites"   # src/payload_factory/sir.py -> repo root = parents[2]


class SiteInventoryRecord(BaseModel):
    """The facts backbone. `classification` carries ecological_archetype + structure (the two
    axes stamp.py reads); `geometry` is the structure-typed shape; `blocks` holds the
    remaining typed fact-blocks (money_shelf, opportunity_menu, vips, hazards …)."""

    model_config = ConfigDict(frozen=True)

    site_id: str
    name: str
    classification: BioregionClassification
    geometry: AssetBlock | SegmentationBlock       # structure-typed (single-asset | corridor)
    blocks: dict = Field(default_factory=dict)      # role -> validated typed block
    as_of: date | None = None
    owner: str | None = None

    @property
    def ecological_archetype(self) -> EcologicalArchetype:
        return self.classification.ecological_archetype

    @property
    def structure(self) -> SiteStructure | None:
        return self.classification.structure


def _pick_geometry(blocks: dict, structure: SiteStructure):
    """The one loaded block that IS this structure's geometry (by type)."""
    cls = geometry_block_class(structure)
    if cls is None:
        raise ValueError(f"structure {structure.value!r} has no geometry block yet (group is TO_BE_DEFINED)")
    for b in blocks.values():
        if isinstance(b, cls):
            return b
    raise ValueError(f"{structure.value}: no {cls.__name__} among the site's blocks")


def sir_for(site_id: str, site_dir: str | Path | None = None) -> SiteInventoryRecord:
    """Build the SIR for a registered site (facts from site.yaml + blocks + the
    bioregion worked-binding classification). Un-bound sites resolve their
    classification via tools.bioregion.resolve_bioregion first (future)."""
    site_dir = Path(site_dir) if site_dir else (_SITES / site_id)
    spec = load_site_spec(site_dir)
    blocks = load_site_blocks(site_dir)
    cls = classification_for_site(site_id)
    if cls is None:
        raise ValueError(f"{site_id}: no bioregion_classification — add a worked_binding or resolve_bioregion first")
    if cls.structure is None:
        raise ValueError(f"{site_id}: classification has no structure axis set")
    geom = _pick_geometry(blocks, cls.structure)
    return SiteInventoryRecord(site_id=site_id, name=spec.name, classification=cls,
                               geometry=geom, blocks=blocks, as_of=spec.as_of)
