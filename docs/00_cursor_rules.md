# Cursor Rules for Pythia Development Work

**Date Created**: December 14, 2025

Cursor is required to follow these rules:

## Architecture Constraints

- **DO NOT** make whole new architectures to make more data sources fit, use what we have
- **DO NOT** suggest capabilities that exceed current Pythia technical architecture
- See [`src/multi_agent_system/agents/base_agent.py`](src/multi_agent_system/agents/base_agent.py) for current agent capabilities
- See [`src/multi_agent_system/a2a/`](src/multi_agent_system/a2a/) for current A2A protocol implementation

## Do Not Make Up Anything

- Do not create or reference data sources, files, or code that do not exist in the Pythia codebase
- Only reference real, existing data sources with verified URLs
- Do not create fictional APIs, datasets, data providers, or files
- Do not make up user personas, user stories, or test users for prototypes that do not belong in that prototype
- Verify all data source links and access methods before suggesting them
- If unsure about a data source, state that it needs verification
- All references must point to actual files in `src/` or verified external sources

## No File Changes Without Explicit Approval

- **DO NOT** truncate, change, delete, or add to any file unless explicitly approved
- **No Truncation**: Do not truncate or remove anything from this file unless explicitly approved
- **ALWAYS** suggest changes first, then wait for user approval
- Present options and recommendations before making any modifications
- Get explicit confirmation before proceeding with file edits

## No Real-Time Data Feed Promises

- Remember that the system does not provide real-time data feeds
- Data refresh intervals are 1-6 hours, not real-time
- Do not promise or suggest real-time monitoring capabilities
- Focus on scheduled data updates and batch processing

## Documentation Maintenance

- In docs/ files always update the change log but keep the description of changes as short as possible
- In docs/ files always update the date changed at the top

## Development Validation and Communication Review

- **Communication Review**: All user communications should be reviewed for compliance with these constraints
- **Cross-Reference**: When making suggestions or changes, ensure alignment with these rules in `docs/00_cursor_rules.md`

## ADK/A2A Multi-Step Agent Chaining Compliance

- All agent chaining and aggregation must use real, registered AgentCards and skills (no fictional APIs).
- No new architectures: use existing ADK/A2A, agent, and AgentCard structure.
- No real-time promises: update frequency must be documented in AgentCards and enums.
- All error handling, provenance, and metrics must be standardized and documented in AgentCards and system docs.
- All changes to agent workflows or chaining must be documented and approved before implementation.

See [Google Cloud Agent SDK Documentation](https://cloud.google.com/agent-sdk/docs) and [Agent Engine Documentation](https://cloud.google.com/agent-engine/docs) for best practices.

---



