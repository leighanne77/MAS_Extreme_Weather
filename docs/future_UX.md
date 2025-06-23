# Future UX Updates for Pythia

This document outlines the suggested updates needed for the UX mockup and UX ideas documents based on recent changes to the prototypes and terminology.

## **Critical Updates Needed:**

### 1. **Terminology Updates**
- Replace all instances of "climate" with "extreme weather-related risk" throughout the document
- Update scenario titles, descriptions, and user journey examples
- Modify filter names and descriptions to use the new terminology

### 2. **User Type Alignment with Prototypes**
- Update user types to match the specific prototypes from `prototypes.md`
- Add missing user types (e.g., "Crop Insurance Officers", "Operating Note Lending Officers")
- Update example prompts to be more specific to the geographic prototypes
- Align user type device preferences with the actual user types

### 3. **Geographic Prototype Integration**
- Update the UX requirements sections to reflect the specific geographic prototypes
- Include prototype-specific risk factors and data sources
- Add regional context to scenarios and derisking strategies
- Update user journey examples to use specific geographic locations

### 4. **Economic Problem Focus**
- Align scenarios with the specific economic problems from the prototypes
- Update filter descriptions to reflect the economic optimization goals
- Include ROI calculations that match the user type's economic challenges
- Add risk-adjusted return metrics for investment-focused users

### 5. **Data Source Integration**
- Reference the specific data sources from `Draft_Prototypes_data_sources.md`
- Include confidence levels based on data quality and availability
- Add data source attribution in scenarios and strategies
- Update the "Data Limitations" section to reflect current constraints

### 6. **Risk Definitions Integration**
- Reference the risk categories from `risk_definitions.py`
- Include risk scoring based on the defined risk levels
- Add risk factor correlations and dependencies
- Update risk assessment frameworks to use the standardized definitions

## **Specific Sections That Need Updates:**

### **User Type Device Preferences Section**
- Update to include all user types from the prototypes
- Add missing user types like "Crop Insurance Officers" and "Operating Note Lending Officers"
- Align with the actual user types in the system

### **Example Prompts Section**
- Update all example prompts to use specific geographic locations from the prototypes
- Include more detailed asset descriptions that match the prototype scenarios
- Add economic context to the prompts

### **Filter System Section**
- Update filter names to use "extreme weather-related risk" terminology
- Align filters with the economic problems from the prototypes
- Add prototype-specific filters for each geographic region

### **UX Requirements Sections**
- Update each prototype section to reflect the specific user types and their needs
- Include regional context and challenges
- Add prototype-specific data sources and risk factors

### **Notification System Section**
- Update to reflect the new terminology
- Include prototype-specific monitoring scenarios
- Add regional context to notification examples

## **Files to Update:**

### **pythia_ux_mockup.py**
- Update user type configurations to match prototypes
- Replace "climate" terminology with "extreme weather-related risk"
- Update example prompts with geographic specificity
- Add prototype-specific scenarios and derisking strategies
- Integrate risk definitions from `risk_definitions.py`

### **DRAFT_UX_ideas.md**
- Update terminology throughout the document
- Align user types with prototype definitions
- Update geographic prototype sections
- Modify filter systems to reflect economic problems
- Integrate data sources from `Draft_Prototypes_data_sources.md`

## **Implementation Priority:**

### **Phase 1: Critical Terminology Updates**
1. Replace "climate" with "extreme weather-related risk" in all files
2. Update user type names to match prototypes
3. Update example prompts with geographic specificity

### **Phase 2: User Type Alignment**
1. Update user type configurations in UX mockup
2. Align device preferences with actual user types
3. Update filter systems to match economic problems

### **Phase 3: Geographic Integration**
1. Add prototype-specific scenarios
2. Update UX requirements sections
3. Include regional context in user journeys

### **Phase 4: Data Integration**
1. Reference specific data sources
2. Add confidence levels and attribution
3. Integrate risk definitions

## **Related Documentation:**
- [prototypes.md](prototypes.md) - Geographic prototypes and user types
- [DRAFT_prototypes_user_journeys.md](DRAFT_prototypes_user_journeys.md) - Detailed user journeys
- [Draft_Prototypes_data_sources.md](Draft_Prototypes_data_sources.md) - Data sources
- [risk_definitions.py](../risk_definitions.py) - Risk definitions and categories
- [Draft_value_propositions.md](Draft_value_propositions.md) - Value propositions

---

*This document serves as a roadmap for future UX updates to align with the current prototype definitions and terminology changes.* 