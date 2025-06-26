This is included in gitignore

# Do Not Do Guidelines

## Related Documentation

- [Draft_value_propositions.md](Draft_value_propositions.md) - Common value propositions across all prototype users
- `DRAFT_prototypes_user_journeys.md` - Defines the scope of value propositions
- `agent_guidelines.md` - Agent behavior guidelines
- `terms_used.md` - Approved terminology and definitions

---

## Core Restrictions

### 1. Carbon or Climate References
- **DO NOT** reference carbon markets, carbon credits, carbon trading, or carbon-related financial instruments
- **DO NOT** Use the word "climate" or variations but insteaad use terms like "extreme weather-related risk" 
- **DO NOT** promise carbon sequestration outcomes or carbon reduction metrics
- **DO NOT** use carbon-related terminology in user communications or documentation
- **USE INSTEAD**: Risks, risk mitigation, biodiversity, ecosystem services, and environmental benefits

### 2. Proprietary Data Restrictions
- **DO NOT** promise results that require access to user's proprietary data that we cannot use
- **DO NOT** promise features that rely on user's proprietary data that we cannot access
- **DO NOT** suggest integrations that would require user to share confidential business information
- **DO NOT** promise personalized recommendations based on user's internal data without explicit permission
- **DO NOT** promise data integration with user's proprietary systems or databases
- **DO NOT** suggest that Pythia will access, store, or process user's proprietary data
- **INSTEAD**: Pythia provides expert and external data sources (weather, environmental, scientific) to enhance user's existing proprietary data and decision-making processes
- **INSTEAD**: Users can combine Pythia's external data insights with their own proprietary data for enhanced risk assessment and decision-making

### 3. Value Proposition Boundaries
- **DO NOT** go beyond the value propositions outlined in `DRAFT_prototypes_user_journeys.md`
- **DO NOT** promise features not explicitly mentioned in the user journey documentation
- **DO NOT** suggest capabilities that exceed the scope defined in the prototype documentation
- **STAY WITHIN** the defined user personas: Loan Officers, Private Equity Investors, and Property Owners

## Additional Guidelines

### 4. Data Privacy & Security
- **DO NOT** promise to store or process user's personal financial information
- **DO NOT** suggest features that would require access to user's banking or investment data
- **DO NOT** promise integration with user's internal systems without explicit permission
- **DO NOT** suggest features that would require user to share client information

### 5. Technical Limitations
- **DO NOT** promise real-time data feeds without confirming API availability
  - See [`src/multi_agent_system/data/weather_data.py`](../src/multi_agent_system/data/weather_data.py) for current NOAA data integration capabilities
  - See [`src/multi_agent_system/data/data_sources.py`](../src/multi_agent_system/data/data_sources.py) for supported data source integrations
- **DO NOT** suggest integrations with third-party services without verifying access
  - See [`src/multi_agent_system/data/nature_based_solutions_source.py`](../src/multi_agent_system/data/nature_based_solutions_source.py) for current nature-based solutions data structure
- **DO NOT** promise features that require significant infrastructure changes
  - See [`src/multi_agent_system/coordinator.py`](../src/multi_agent_system/coordinator.py) for current agent coordination architecture
  - See [`src/multi_agent_system/agent_team.py`](../src/multi_agent_system/agent_team.py) for current multi-agent system capabilities
- **DO NOT** suggest capabilities that exceed current technical architecture
  - See [`src/multi_agent_system/agents/base_agent.py`](../src/multi_agent_system/agents/base_agent.py) for current agent capabilities and limitations
  - See [`src/multi_agent_system/a2a/`](../src/multi_agent_system/a2a/) for current A2A protocol implementation
- **DO NOT** promise real-time data - will be on the roadmap later

### 6. User Experience Boundaries
- **DO NOT** promise fully automated decision-making capabilities
- **DO NOT** suggest features that would replace professional judgment
- **DO NOT** promise instant results or immediate implementation
- **DO NOT** suggest features that require extensive user training

### 7. Environmental Claims
- **DO NOT** make specific environmental impact promises without data validation
- **DO NOT** promise quantifiable environmental outcomes without measurement capabilities
- **DO NOT** suggest features that would require environmental certification
- **DO NOT** promise compliance with specific environmental standards

### 8. Financial Promises
- **DO NOT** promise specific financial returns or ROI guarantees
- **DO NOT** suggest features that would require financial licensing
- **DO NOT** promise access to specific financial products or services
- **DO NOT** suggest features that would require financial advisor certification

### 9. Integration Limitations
- **DO NOT** promise seamless integration with user's existing systems
- **DO NOT** suggest features that would require API access to user's internal databases
- **DO NOT** promise features that would require user to modify their existing workflows
- **DO NOT** suggest capabilities that would require user to share their proprietary algorithms
- **DO NOT** promise direct integration with user's proprietary data systems
- **INSTEAD**: Pythia provides external data feeds and insights that users can incorporate into their existing workflows and decision-making processes
- **INSTEAD**: Users can export Pythia's analysis results and integrate them into their own proprietary systems as needed

## Enforcement

- All documentation should reference this file when discussing new features
- All development should be validated against these guidelines
- All user communications should be reviewed for compliance
- Regular audits should be conducted to ensure adherence 