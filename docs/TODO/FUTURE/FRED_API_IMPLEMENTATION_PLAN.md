# FRED API Implementation Plan

**Date Created**: December 14, 2025  
**Priority**: 🔴 HIGH  
**Status**: Ready to Implement

---

## Overview

**FRED API (Federal Reserve Economic Data)** provides comprehensive economic indicators, interest rates, inflation data, and regional economic data essential for:
- IRR (Internal Rate of Return) calculations
- Economic risk assessments
- Regional economic analysis
- Investment decision support

---

## Implementation Steps

### **Step 1: Create FRED API Integration File** ✅
- **File**: `src/multi_agent_system/data/fred_api.py`
- **Class**: `FREDDataSource` (inherits from `DataSource`)
- **Package**: `fredapi>=0.5.0` (already in requirements.txt)

### **Step 2: Core Methods to Implement**
1. **`get_economic_indicators(series_ids: list, start_date: str, end_date: str)`**
   - Fetch multiple economic indicators by series ID
   - Returns time series data for indicators like:
     - GDP (GDP)
     - Unemployment Rate (UNRATE)
     - Inflation (CPIAUCSL)
     - Interest Rates (FEDFUNDS, DGS10)

2. **`get_regional_economic_data(state: str, indicators: list)`**
   - Get state-specific economic data
   - Uses FRED's regional series (e.g., state unemployment, state GDP)

3. **`get_irr_calculation_data()`**
   - Returns data needed for IRR calculations:
     - Risk-free rate (10-Year Treasury: DGS10)
     - Inflation rate (CPI: CPIAUCSL)
     - Federal funds rate (FEDFUNDS)

4. **`search_series(query: str, limit: int = 20)`**
   - Search for FRED series by keyword
   - Useful for discovering available data

5. **`get_series_info(series_id: str)`**
   - Get metadata about a specific series

### **Step 3: Register in Enhanced Data Manager**
- **File**: `src/multi_agent_system/data/enhanced_data_sources.py`
- **Action**: Add `self.sources["fred"] = FREDDataSource()` in `_initialize_sources()`

### **Step 4: Update EconomicData Class**
- **File**: `src/multi_agent_system/data/enhanced_data_sources.py`
- **Action**: Replace placeholder `get_regional_economic_data()` with actual FRED API calls

### **Step 5: Add Agent Tools**
- **File**: `src/multi_agent_system/agents/tools.py`
- **Tools to Add**:
  - `get_fred_economic_indicators_tool()`
  - `get_fred_regional_data_tool()`
  - `get_fred_irr_data_tool()`
  - `search_fred_series_tool()`

### **Step 6: Export in Module**
- **File**: `src/multi_agent_system/data/__init__.py`
- **Action**: Export `FREDDataSource`

---

## API Key Configuration

**Environment Variable**: `FRED_API_KEY`  
**Registration**: [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org)  
**Documentation**: [FRED API Key Documentation](https://fred.stlouisfed.org/docs/api/api_key.html)  
**Format**: 32-character lowercase alphanumeric string

**Add to `.env`**:
```bash
FRED_API_KEY=your_fred_api_key_here
```

---

## Common FRED Series IDs

### **National Economic Indicators**
- **GDP**: `GDP` - Gross Domestic Product
- **Unemployment**: `UNRATE` - Unemployment Rate
- **Inflation**: `CPIAUCSL` - Consumer Price Index
- **Federal Funds Rate**: `FEDFUNDS` - Federal Funds Effective Rate
- **10-Year Treasury**: `DGS10` - 10-Year Treasury Constant Maturity Rate
- **30-Year Treasury**: `DGS30` - 30-Year Treasury Constant Maturity Rate

### **Regional Indicators**
- **State Unemployment**: `[STATE]UR` (e.g., `ALUR` for Alabama)
- **State GDP**: `[STATE]NGSP` (e.g., `ALNGSP` for Alabama)
- **Metro Area Unemployment**: `[METRO]UR` (e.g., `BIRMUR` for Birmingham)

---

## Implementation Reference

- **Source**: `docs/TODO/IMPLEMENTATION_TODO_AL_AND_NBS.md` - Section 1.5, Task 1
- **AL_Suggestions.md**: Lines 384-401
- **2.1_First_Data_Sources.md**: Lines 241-248

---

## Change Log

### **December 14, 2025**
- **Plan Created**: Implementation plan documented
- **Status**: Ready to implement

