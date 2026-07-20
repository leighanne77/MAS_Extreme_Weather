"""Deterministic opportunity tools — the matchers recommendation_agent calls.

PURE: no ADK, no agent import (dependency direction — the agent imports these).
Numbers/eligibility come from the data files here, never from the LLM.
"""
from payload_factory.tools.match import match_opportunities  # noqa: F401
from payload_factory.tools.capital import attach_capital  # noqa: F401
from payload_factory.tools.recognition import attach_recognition  # noqa: F401
from payload_factory.tools.assemble import assemble_opportunity_menu, gate_opportunity_menu  # noqa: F401
from payload_factory.tools.opportunity_zone import check_opportunity_zone, oz_payload_contribution, qof_benefits  # noqa: F401
