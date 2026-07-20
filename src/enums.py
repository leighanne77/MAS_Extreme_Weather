"""
General enums for use across all src/ modules in MAS.

Naming conventions:
- Prefix with domain if needed for clarity (e.g., DataLoadStatus, AgentRole, ArtifactType).
- Use clear, descriptive names and docstrings for each enum and value.

See documentation in docs/Definitions.md for usage examples and integration guidance.
"""
from enum import Enum

class DataLoadStatus(Enum):
    """Status of a data loader or agent operation."""
    SUCCESS = "success"
    PARTIAL = "partial"                    # batch: some requests succeeded, some failed
    ERROR = "error"

class DataProvenance(Enum):
    """Origin of the data used or produced."""
    API = "api"
    MCP = "mcp"
    STATIC = "static"
    MANUAL = "manual"

class DataDomain(Enum):
    """Domain/type of the data source."""
    AGRICULTURE = "agriculture"
    WATER = "water"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"

class DataErrorType(Enum):
    """Type of error encountered during data operations."""
    NETWORK = "network"
    PARSING = "parsing"
    VALIDATION = "validation"
    PERMISSION = "permission"
    UNKNOWN = "unknown"

class DataUpdateFrequency(Enum):
    """How often the data is updated or refreshed."""
    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    MANUAL = "manual"

class DataFormat(Enum):
    """Format of the data returned or processed."""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"
    OTHER = "other"

class DataAccessLevel(Enum):
    """Access permissions for the data."""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    INTERNAL = "internal"

class ArtifactType(Enum):
    """Type of artifact produced by agents or loaders."""
    DATASET = "dataset"
    MODEL = "model"
    REPORT = "report"
    VISUALIZATION = "visualization"
    LOG = "log"

# System/Agent/Observability enums
class ErrorSeverity(Enum):
    """Severity of an error for logging and recovery."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentRole(Enum):
    """Role of an agent in the system."""
    ANALYST = "analyst"
    VALIDATOR = "validator"
    INGESTOR = "ingestor"
    REPORTER = "reporter"
    ADMIN = "admin"

class InteractionType(Enum):
    """Pattern of agent interaction."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    BRANCHING = "branching"
    RECURSIVE = "recursive"

class DecisionPattern(Enum):
    """Pattern of agent decision-making."""
    LINEAR = "linear"
    BRANCHING = "branching"
    BACKTRACKING = "backtracking"
    OPTIMIZATION = "optimization"

class MessageType(Enum):
    """Type of A2A message.
    
    Note: This is the canonical MessageType enum. The A2A module
    (multi_agent_system/a2a/enums.py) re-exports this for backward compatibility.
    """
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_UPDATE = "task_update"
    TASK_COMPLETION = "task_completion"
    ARTIFACT_CREATED = "artifact_created"
    ARTIFACT_REQUESTED = "artifact_requested"
    OTHER = "other"

class PriorityLevel(Enum):
    """Priority of a message or task (string values).
    
    For numeric priority values, see multi_agent_system/a2a/enums.Priority.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Communication status constants - use instead of string literals
class CommunicationStatus(Enum):
    """Status values for agent communication responses."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


# =============================================================================
# A2A Protocol Enums
# =============================================================================
# These enums are used by the A2A (Agent-to-Agent) protocol implementation.
# The A2A module (multi_agent_system/a2a/enums.py) re-exports these for
# backward compatibility.

class Priority(Enum):
    """A2A Message Priority Levels (numeric for sorting/comparison).
    
    Use these for A2A protocol messages where numeric priority is needed.
    For general-purpose string priorities, see PriorityLevel.
    """
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class StatusCode(Enum):
    """A2A Protocol Status Codes.
    
    HTTP-style status codes plus A2A-specific codes for agent communication.
    """
    # Success codes
    OK = 200
    CREATED = 201
    ACCEPTED = 202

    # Client error codes
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409

    # Server error codes
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503

    # A2A specific codes
    AGENT_NOT_FOUND = 1001
    MESSAGE_FORMAT_ERROR = 1002
    ROUTING_ERROR = 1003
    TASK_NOT_FOUND = 1004
    ARTIFACT_NOT_FOUND = 1005


class PartType(Enum):
    """A2A Message Part Types for multipart messages."""
    TEXT = "text"
    DATA = "data"
    FILE = "file"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    BINARY = "binary"


# Status code descriptions for human-readable messages
STATUS_DESCRIPTIONS: dict[StatusCode, str] = {
    StatusCode.OK: "Request completed successfully",
    StatusCode.CREATED: "Resource created successfully",
    StatusCode.ACCEPTED: "Request accepted for processing",
    StatusCode.BAD_REQUEST: "Invalid request format or parameters",
    StatusCode.UNAUTHORIZED: "Authentication required",
    StatusCode.FORBIDDEN: "Access denied",
    StatusCode.NOT_FOUND: "Resource not found",
    StatusCode.CONFLICT: "Resource conflict",
    StatusCode.INTERNAL_ERROR: "Internal server error",
    StatusCode.NOT_IMPLEMENTED: "Feature not implemented",
    StatusCode.SERVICE_UNAVAILABLE: "Service temporarily unavailable",
    StatusCode.AGENT_NOT_FOUND: "Target agent not found",
    StatusCode.MESSAGE_FORMAT_ERROR: "Invalid message format",
    StatusCode.ROUTING_ERROR: "Message routing failed",
    StatusCode.TASK_NOT_FOUND: "Task not found",
    StatusCode.ARTIFACT_NOT_FOUND: "Artifact not found",
}


def get_status_description(status_code: StatusCode) -> str:
    """Get human-readable description for a status code."""
    return STATUS_DESCRIPTIONS.get(status_code, "Unknown status code")


# ── Brief factory enums (Briefing Standards / Briefs) ──────────────────────

class FigureStatus(Enum):
    """Lifecycle/trust status of a figure in a Brief."""
    VERIFIED = "verified"                  # confirmed against source of record
    ESTIMATE = "estimate"                  # MAS-computed, directional, cited basis
    CARRIED_FORWARD = "carried-forward"    # from a prior doc; re-verify before Room_Ready
    TO_BE_FILLED = "to-be-filled"          # clause open; sources named
    TO_COME = "to-come"                    # capability placeholder (e.g., Sealed Exchange)
    REPORTED_NEGATIVE = "reported-negative"  # checked; nothing to report (closed-world)


class Grade(Enum):
    """Backtest-derived confidence grade on a figure or model (cf. GRADE)."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNGRADED = "ungraded"


class PreferenceClass(Enum):
    """Composite trust class of a data source (profile stays visible)."""
    P1_PREFERENCED = "p1-preferenced"
    P2_STANDARD = "p2-standard"
    P3_USE_WITH_CAVEAT = "p3-use-with-caveat"


class EvidenceType(Enum):
    """Kind of evidence behind a citation (multimodal-ready)."""
    SCALAR = "scalar"
    DOCUMENT = "document"
    IMAGE = "image"
    SCENE = "scene"          # satellite/aerial scene (STAC item)
    DERIVED = "derived"      # algorithm-derived from other evidence


class SourceContinuity(Enum):
    """Post-2026 continuity status of a (federal) source."""
    STABLE = "stable"
    TRUSTED_EXCEPTION = "trusted-exception"  # e.g., USACE, observational networks
    WATCH = "watch"
    AT_RISK = "at-risk"
    RETIRED = "retired"


class IlkTier(Enum):
    """Indigenous & Local Knowledge provider tier (A1 → A2 → B ladder)."""
    A1_TRIBAL = "a1-tribal"
    A2_NATURE_PROXIMATE = "a2-nature-proximate"
    B_NONPROFIT_PUBLISHED = "b-nonprofit-published"


class CoordConfidence(Enum):
    """Coordinate confidence (site-of-sites legend). Applies to lat/long only,
    not the site's existence."""
    HIGH = "high"          # >=80%
    MED = "med"            # 50-80%
    LOW_MED = "low-med"    # 20-50% upper band
    LOW = "low"            # 20-50%
    GUESS = "guess"        # <20%, no basis


class ClaimTag(Enum):
    """Provenance of a stated fact (site-of-sites legend)."""
    KNOWN = "known"        # training/public fact
    INFERRED = "inferred"  # deduction
    GUESS = "guess"        # no basis
    PLAN = "plan"          # from a published plan
    THESIS = "thesis"      # investor framing, no named source
    SECONDARY = "secondary"  # analyst/press context


class DemandStatus(Enum):
    """Funding/demand maturity. Per house discipline, ONLY OBLIGATED
    counts as anchor demand."""
    OBLIGATED = "obligated"
    APPROPRIATED = "appropriated"
    AUTHORIZED = "authorized"
    HYPOTHETICAL = "hypothetical"


class ProviderClass(Enum):
    """Knowledge-provider class. Two tracks: ILK (practice-based) + scientific
    (formal/credentialed). All are hyper-local and geolocation-linked."""
    # ILK track (practice-based observation)
    TRIBAL = "tribal"                          # tier A1 — CARE, consent-first
    NATURE_PROXIMATE = "nature-proximate"      # tier A2 — fishers, regen-ag co-ops
    CITIZEN_SCIENCE = "citizen-science"        # tier B  — non-profit w/ published data
    # Scientific-expert track (formal methods)
    ACADEMIC = "academic"                      # tier S1 — local university / field station
    RESEARCH_INSTITUTE = "research-institute"  # tier S2 — regional research institute
    CONSULTING_SCIENTIST = "consulting-scientist"  # tier S3 — non-federal lab/consultant


class OperatingStatus(Enum):
    """Ground-truthed liveness of an entity (VIP/employer). A benefit anchor
    must be ACTIVE — a closing/closed entity is regional LOSS/context, not benefit."""
    ACTIVE = "active"
    AT_RISK = "at-risk"                    # distress signals; watch
    ANNOUNCED_CLOSURE = "announced-closure"  # public closure announcement
    CEASED = "ceased"                      # closed
    VERIFY = "verify"                      # not yet ground-truthed


class RiskLevel(str, Enum):
    """Hazard severity grades (moved from risk_definitions.py 2026-07-15 — enum-sync rule: enums live HERE)."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"
    SUPER_EXTREME = "super_extreme"  # e.g., frequent 100-year flood levels


class ContactStatus(str, Enum):
    """Consent-first contact ladder for hyperlocal experts (2026-07-15).
    Outreach NEVER advances past IDENTIFIED/QUALIFIED without a human decision."""
    IDENTIFIED = "identified"            # known to exist; no contact
    QUALIFIED = "qualified"              # meets provider criteria; still no contact
    CONSENT_REQUESTED = "consent_requested"  # human-approved outreach sent
    ENGAGED = "engaged"                  # active collaborator
    DECLINED = "declined"                # decline != missing — recorded, respected
    DO_NOT_CONTACT = "do_not_contact"    # standing instruction (e.g., Graton Rancheria 2026-07-15)


class BeneficiaryClass(str, Enum):
    """Shared-table beneficiary lenses (2026-07-15): facts about an opportunity —
    registers ORDER these columns for the reader, never hide them (doc 8)."""
    LAND_VALUE = "land_value"                        # investor lens
    INFRASTRUCTURE_SERVICE = "infrastructure_service"  # agency lens: works longer, protects value + people
    BIOREGION_HEALTH = "bioregion_health"            # scientist lens: measurable repair
    TRADITIONAL_USE_ACCESS = "traditional_use_access"  # indigenous lens: access, fishing, traditional activities


# ── Bioregion classification enums (2026-07-17) ────────────────────────────
# The ECOLOGICAL axis (archetype) is orthogonal to the STRUCTURE axis; together
# they select a Payload Standard + HTML map variant (EVE_Two_Inventories).
# Crosswalk of frameworks lives in standards/reference/bioregions.yaml (single source).

class EcologicalArchetype(str, Enum):
    """MAS's operative ecological bucket — resolved from the IUCN GET biome (the
    global pivot). Selects the payload's hazard signature + ecology + NbS menu.
    A US site and an international site of the SAME functional type share one value."""
    COASTAL_ESTUARINE = "coastal-estuarine"
    ARID_DESERT = "arid-desert"
    RIVERINE_INLAND_WATERWAY = "riverine-inland-waterway"
    MONTANE = "montane"
    ARCTIC_COLD = "arctic-cold"
    GREAT_PLAINS = "great-plains"


class SiteStructure(str, Enum):
    """The geometry/shape axis — selects the geometry block + the 4_map__* HTML
    render. Orthogonal to EcologicalArchetype. single-asset preserves the
    single-asset payload template (asset{footprint,zones[]}, ebitda_at_risk)."""
    SINGLE_ASSET = "single-asset"
    CORRIDOR = "corridor"
    GROUP = "group"


class HgmClass(str, Enum):
    """USACE Hydrogeomorphic (HGM) wetland class (ERDC) — reused, not invented.
    Selects the §404 permitting + beneficial-use / mitigation-bank funding path
    on the money_shelf. Archetype-stable; verify per USACE district."""
    RIVERINE = "riverine"
    DEPRESSIONAL = "depressional"
    SLOPE = "slope"
    TIDAL_FRINGE = "tidal-fringe"                 # estuarine / tidal fringe
    LACUSTRINE_FRINGE = "lacustrine-fringe"
    MINERAL_SOIL_FLATS = "mineral-soil-flats"
    ORGANIC_SOIL_FLATS = "organic-soil-flats"


class RegulatoryGate(str, Enum):
    """Which regulatory determination UNLOCKS an archetype's NbS funding path.
    Funding is archetype-level (money_path) and NOT owned by USACE — this names
    the gate WHEN one applies (US §404) and marks the non-USACE / international
    cases explicitly, so nothing is falsely attributed to USACE."""
    USACE_404_BUDM = "usace_404_budm"        # §404 + Beneficial Use of Dredged Material (navigation dredging)
    USACE_404_MITBANK = "usace_404_mitbank"  # §404 + wetland/species mitigation banking (no dredging)
    STATE_MAR = "state_mar"                   # state managed-aquifer-recharge / water-reuse (arid)
    LOCAL_REGULATOR = "local_regulator"       # non-US: local regulator equivalent (no USACE)
    NONE = "none"                             # no funding gate identified yet
