# pyproject.toml vs requirements.txt Comparison

**Date Created**: December 14, 2025  
**Purpose**: Verify all packages are present in both files and check if they're actually used

---

## ✅ All Packages Are Present in Both Files

### **1. httpx, openpyxl, reportlab, pytest-timeout, pytest-env** (Lines 43-46 suggestion)

| Package | pyproject.toml | requirements.txt | Status |
|---------|---------------|------------------|--------|
| `httpx>=0.24.0` | ✅ Line 62 | ✅ Line 50 | **PRESENT** |
| `openpyxl>=3.1.0` | ✅ Line 101 | ✅ Line 89 | **PRESENT** |
| `reportlab>=4.0.0` | ✅ Line 102 | ✅ Line 90 | **PRESENT** |
| `pytest-timeout>=2.1.0` | ✅ Line 127 (dev) | ✅ Line 102 | **PRESENT** |
| `pytest-env>=1.1.0` | ✅ Line 128 (dev) | ✅ Line 103 | **PRESENT** |

**Verdict**: ✅ **All present** - No updates needed

---

### **2. Security Packages** (Lines 59-62 suggestion)

| Package | pyproject.toml | requirements.txt | Status |
|---------|---------------|------------------|--------|
| `python-jose[cryptography]>=3.3.0,<4.0.0` | ✅ Line 78 | ✅ Line 66 | **PRESENT** |
| `cryptography>=41.0.0,<43.0.0` | ✅ Line 80 | ✅ Line 68 | **PRESENT** |
| `pyjwt>=2.8.0,<3.0.0` | ✅ Line 81 | ✅ Line 69 | **PRESENT** |

**Verdict**: ✅ **All present** - No updates needed

**Note**: These are **actively used** in `src/multi_agent_system/session_manager.py`:
- `import jwt` (from `pyjwt` package)
- Used for JWT token validation and session management

---

### **3. MCP Dependencies** (Lines 73-79 suggestion)

| Package | pyproject.toml | requirements.txt | Status |
|---------|---------------|------------------|--------|
| `mcp[cli]>=1.6.0` | ✅ Line 105 | ✅ Line 27 | **PRESENT** |
| `earthaccess>=0.14.0` | ✅ Line 106 | ✅ Line 28 | **PRESENT** |
| `python-cmr>=0.10.0` | ✅ Line 107 | ✅ Line 29 | **PRESENT** |
| `s3fs>=2022.11` | ✅ Line 108 | ✅ Line 30 | **PRESENT** |
| `tinynetrc>=1.3.1` | ✅ Line 109 | ✅ Line 31 | **PRESENT** |

**Verdict**: ✅ **All present** - No updates needed

**Note**: 
- `earthaccess` is **actively used** in `src/multi_agent_system/data/cmr_mcp.py`
- `s3fs` and `tinynetrc` are likely dependencies of `earthaccess` or other MCP packages
- `mcp[cli]` is required for MCP server integration

---

### **4. fredapi** (Lines 87-88 suggestion)

| Package | pyproject.toml | requirements.txt | Status |
|---------|---------------|------------------|--------|
| `fredapi>=0.5.0` | ✅ Line 112 | ✅ Line 38 | **PRESENT** |

**Verdict**: ✅ **Present** - No updates needed

**Note**: 
- **Not currently used** in codebase (no imports found)
- **Planned for future use** - FRED API integration is in TODO list
- **Keep it** - Will be needed when FRED API integration is implemented

---

## 📊 Usage Analysis

### **Packages Currently Used in Codebase**:
- ✅ `httpx` - Not directly imported, but may be used by other packages
- ❌ `openpyxl` - **Not used** (no imports found)
- ❌ `reportlab` - **Not used** (no imports found)
- ✅ `pytest-timeout`, `pytest-env` - Used for testing (dev dependencies)
- ✅ `python-jose`, `cryptography`, `pyjwt` - **Used** in `session_manager.py`
- ✅ `earthaccess` - **Used** in `cmr_mcp.py`
- ✅ `mcp[cli]` - Required for MCP protocol
- ❌ `fredapi` - **Not yet used** (planned for future)

### **Packages Not Used But May Be Needed**:
- `openpyxl` - For Excel file processing (may be needed for data exports)
- `reportlab` - For PDF generation (may be needed for report generation)
- `fredapi` - For FRED API integration (planned feature)

---

## 🔍 Version Differences

### **google-adk Version Mismatch**:

| Package | pyproject.toml | requirements.txt | Recommendation |
|---------|---------------|------------------|---------------|
| `google-adk` | `>=0.1.0` (Line 43) | `>=1.5.0` (Line 17) | ⚠️ **Update pyproject.toml** |

**Action**: Update `pyproject.toml` line 43 to match `requirements.txt`:
```toml
"google-adk>=1.5.0",  # Instead of >=0.1.0
```

---

## ✅ Recommendations

### **1. No Changes Needed** ✅
All packages mentioned in the suggestions are already present in both files.

### **2. Optional: Remove Unused Packages** (Optional)
If you want to minimize dependencies, you could consider removing:
- `openpyxl` - If you don't plan to process Excel files
- `reportlab` - If you don't plan to generate PDFs

**However**, these are small packages and may be useful for future features, so **keeping them is fine**.

### **3. Fix Version Mismatch** ⚠️
Update `google-adk` version in `pyproject.toml` to match `requirements.txt`:
- Change line 43 from `"google-adk>=0.1.0"` to `"google-adk>=1.5.0"`

### **4. Keep fredapi** ✅
Even though `fredapi` isn't used yet, keep it because:
- FRED API integration is planned (in TODO list)
- It's already in both files
- Small package, minimal overhead

---

## 📝 Summary

| Category | Status | Action Needed |
|----------|--------|---------------|
| **httpx, openpyxl, reportlab** | ✅ Present | None |
| **pytest-timeout, pytest-env** | ✅ Present | None |
| **Security packages** | ✅ Present | None |
| **MCP dependencies** | ✅ Present | None |
| **fredapi** | ✅ Present | None |
| **google-adk version** | ⚠️ Mismatch | Update pyproject.toml |

---

## Change Log

### **December 14, 2025**
- **Initial Comparison**: Compared all suggested packages between pyproject.toml and requirements.txt
- **Result**: All packages are present in both files
- **Finding**: One version mismatch found (google-adk)
- **Recommendation**: Update google-adk version in pyproject.toml to match requirements.txt

