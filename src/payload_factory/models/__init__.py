"""Typed block models — the schema layer of Briefing Standards."""

from payload_factory.models.blocks import (  # noqa: F401
    CalcTrace,
    Citation,
    Figure,
    GaugeEventObservation,
    GaugeStation,
    HazardObsBlock,
    ModelRef,
    SensitivityEntry,
)
from payload_factory.models.corridor import (  # noqa: F401
    ClosureEvent,
    ClosureHistoryBlock,
    CorridorSegment,
    DemandAnchor,
    DemandBlock,
    SegmentationBlock,
    StructurePoint,
    StructuresBlock,
)
from payload_factory.models.asset import (  # noqa: F401
    AssetBlock,
    AssetZone,
)
from payload_factory.models.opportunity import (  # noqa: F401
    OpportunityMenuBlock,
    OpportunityScenario,
    SelectableOpportunity,
)
from payload_factory.models.money import (  # noqa: F401
    CapitalSource,
    MoneyShelfBlock,
    RevenueStream,
)
from payload_factory.models.stakeholder import (  # noqa: F401
    LocalEconomyVIP,
    LocalEconomyVIPBlock,
)
from payload_factory.models.knowledge import (  # noqa: F401
    KnowledgeProvider,
    ProviderDataset,
    KnowledgeProvidersBlock,
    haversine_km,
)
from payload_factory.models.bioregion import (  # noqa: F401
    BioregionClassification,
    IucnGet,
    MoneyPath,
    UsEpa,
    UnElu,
    UsaceLayer,
)


def cite(source, url, accessed, provenance=None, note=None):
    """Citation shorthand — promoted from the SR-37 builders (3 duplicated copies).
    Defaults provenance to STATIC (curated); pass explicitly for API-pulled data."""
    from enums import DataProvenance
    kw = dict(source=source, url=url, accessed=accessed,
              provenance=provenance or DataProvenance.STATIC)
    if note is not None:
        kw["note"] = note
    return Citation(**kw)
