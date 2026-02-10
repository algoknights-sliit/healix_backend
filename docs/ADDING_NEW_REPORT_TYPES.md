# Adding New Report Types - Developer Guide

## Overview

The Healix Backend normalization system is designed to be **easily extensible**. This guide shows you exactly how to add support for new medical report types.

## Current Supported Reports

| Report Type | Biomarkers | Status |
|------------|-----------|--------|
| Full Blood Count (FBC) | 13 | ✅ Production |
| Serum Lipid Profile | 8 | ✅ Production |
| Fasting Plasma Glucose (FBS) | 1 | ✅ Production |

## Quick Start: Adding a New Report Type

Follow these **5 steps** to add a new report type (e.g., "Liver Function Test"):

### Step 1: Add Biomarker Mappings

**File**: `app/config/biomarker_config.py`

```python
# ===== LIVER FUNCTION TEST (LFT) =====

LFT_BIOMARKER_MAPPING = {
    "SERUM BILIRUBIN - TOTAL": "Total Bilirubin",
    "BILIRUBIN - DIRECT": "Direct Bilirubin",
    "BILIRUBIN - INDIRECT": "Indirect Bilirubin",
    "SGOT (AST)": "AST",
    "SGPT (ALT)": "ALT",
    "ALKALINE PHOSPHATASE": "Alkaline Phosphatase",
    "SERUM PROTEIN - TOTAL": "Total Protein",
    "SERUM ALBUMIN": "Albumin",
    "SERUM GLOBULIN": "Globulin",
    "A/G RATIO": "Albumin/Globulin Ratio",
}
```

**Add detection keywords:**

```python
# Report type detection keywords
# Order matters: Check more specific patterns first!
REPORT_TYPE_KEYWORDS = {
    "Fasting Plasma Glucose": [...],
    "Serum Lipid Profile": [...],
    "Liver Function Test": ["LIVER FUNCTION TEST", "LFT", "HEPATIC PANEL"],  # NEW
    "Full Blood Count": [...],
}
```

---

### Step 2: Create Normalization Module

**File**: `app/services/lft_normalization.py` (NEW)

```python
"""
Liver Function Test (LFT) normalization functions.
"""

import re
from typing import Dict, List, Optional, Any
from app.config.biomarker_config import (
    LFT_BIOMARKER_MAPPING,
    UNIT_MAPPING,
    OCR_NOISE_PATTERNS,
    FLAG_MAPPING,
)


def extract_lft_patient_info(raw_text: str) -> Dict[str, Optional[Any]]:
    """Extract patient info - reuse from existing modules if format is similar."""
    # Copy from fbs_normalization.py or lipid_normalization.py
    # Adjust regex patterns as needed for your specific report format
    pass


def extract_lft_report_metadata(raw_text: str) -> Dict[str, Optional[str]]:
    """Extract report metadata."""
    metadata = {
        "type": "Liver Function Test",
        "sample_type": None,
        "sample_collected_at": None,
        "reported_at": None
    }
    # Add extraction logic (copy from existing modules and adapt)
    return metadata


def normalize_lft_biomarkers(tables: List[List[List[str]]], raw_text: str) -> List[Dict[str, Any]]:
    """Extract and normalize LFT biomarkers."""
    biomarkers = []
    
    for table in tables:
        for row in table:
            if len(row) < 2:
                continue
            
            test_name = row[0].strip()
            value_str = row[1].strip()
            unit_str = row[2].strip() if len(row) > 2 else ""
            ref_range_str = row[3].strip() if len(row) > 3 else ""
            
            # Map to standard name
            standard_name = get_standard_lft_name(test_name)
            if not standard_name:
                continue
            
            # Extract value, unit, flag, ref_range
            # (See lipid_normalization.py for examples)
            
            biomarkers.append({
                "name": standard_name,
                "value": value,
                "unit": unit,
                "flag": flag,
                "ref_range": ref_range
            })
    
    return biomarkers


def get_standard_lft_name(test_name: str) -> Optional[str]:
    """Map lab test name to standard LFT biomarker name."""
    clean_name = test_name.strip().upper()
    clean_name = re.sub(r'\s+', ' ', clean_name)
    
    if clean_name in LFT_BIOMARKER_MAPPING:
        return LFT_BIOMARKER_MAPPING[clean_name]
    
    for key, value in LFT_BIOMARKER_MAPPING.items():
        if key.upper() in clean_name or clean_name in key.upper():
            return value
    
    return None
```

---

### Step 3: Add Router Case

**File**: `app/services/normalization_service.py`

```python
def normalize_report(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Auto-detect report type and route to appropriate normalizer."""
    raw_text = raw_data.get("raw_text", "")
    report_type = _detect_report_type(raw_text)
    
    if report_type == "Serum Lipid Profile":
        return _normalize_lipid_profile(raw_data)
    elif report_type == "Fasting Plasma Glucose":
        return _normalize_fbs_report(raw_data)
    elif report_type == "Liver Function Test":  # NEW
        return _normalize_lft_report(raw_data)
    else:
        return _normalize_fbc_report(raw_data)


# Add normalization function
def _normalize_lft_report(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalization function for Liver Function Test reports."""
    from app.services.lft_normalization import (
        extract_lft_patient_info,
        extract_lft_report_metadata,
        normalize_lft_biomarkers
    )
    
    raw_text = raw_data.get("raw_text", "")
    tables = raw_data.get("tables", [])
    
    patient_info = extract_lft_patient_info(raw_text)
    report_metadata = extract_lft_report_metadata(raw_text)
    biomarkers = normalize_lft_biomarkers(tables, raw_text)
    
    return {
        "patient": patient_info,
        "report": report_metadata,
        "biomarkers": biomarkers
    }
```

---

### Step 4: Create Test

**File**: `tests/test_lft_normalization.py` (NEW)

```python
"""Test script for LFT normalization."""

import json
from app.services.normalization_service import normalize_report

# Sample LFT data (from your actual OCR output)
LFT_SAMPLE = {
    "raw_text": "...",  # Paste actual OCR text
    "tables": [...]      # Paste actual table data
}

def test_lft_normalization():
    result = normalize_report(LFT_SAMPLE)
    
    # Validate report type
    assert result["report"]["type"] == "Liver Function Test"
    
    # Validate biomarkers
    biomarkers = result["biomarkers"]
    assert len(biomarkers) == 10  # Expected number
    
    # Check specific biomarkers
    bilirubin = next(b for b in biomarkers if b["name"] == "Total Bilirubin")
    assert bilirubin["value"] > 0
    assert bilirubin["unit"] == "mg/dL"
    
    print("✓ LFT Test Passed!")

if __name__ == "__main__":
    test_lft_normalization()
```

Run test:
```bash
python tests/test_lft_normalization.py
```

---

### Step 5: Document

Create `docs/LFT_NORMALIZATION_EXAMPLE.md` showing before/after comparison.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    normalize_report()                        │
│                   (Main Entry Point)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │ _detect_report_type()│
           │  (Keyword Matching)  │
           └──────────┬───────────┘
                      │
        ┌────────────┼─────────────┬──────────────┐
        │            │             │              │
        ▼            ▼             ▼              ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐   ┌──────────┐
   │  FBC   │  │  Lipid  │  │   FBS    │   │   LFT    │
   │ Module │  │ Module  │  │  Module  │   │  Module  │
   └────────┘  └─────────┘  └──────────┘   └──────────┘
        │            │             │              │
        └────────────┴─────────────┴──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │ Structured   │
              │    JSON      │
              └──────────────┘
```

## File Structure Pattern

```
Healix_Backend/
├── app/
│   ├── config/
│   │   └── biomarker_config.py        # Add mapping & keywords
│   └── services/
│       ├── normalization_service.py   # Add router case
│       ├── fbc_normalization.py       # Example module
│       ├── lipid_normalization.py     # Example module
│       ├── fbs_normalization.py       # Example module
│       └── lft_normalization.py       # NEW: Your module
└── tests/
    ├── test_fbc_normalization.py
    ├── test_lipid_normalization.py
    ├── test_fbs_normalization.py
    └── test_lft_normalization.py       # NEW: Your test
```

## Reusable Code Patterns

### Patient Extraction (Lipid/FBS Pattern)

```python
def extract_patient_info(raw_text: str) -> Dict:
    patient = {" name": None, "age_years": None, "gender": None, "uhid": None}
    
    # Name - adjust pattern as needed
    name_match = re.search(r'PATIENT\s*:\s*(.+?)(?:\n|REFERRED)', raw_text, re.IGNORECASE)
    if name_match:
        patient["name"] = name_match.group(1).strip()
    
    # Age/Gender - handles multi-line
    age_match = re.search(r'AGE.*?:\s*(\d+)\s*Y[/\s]*([MF])', raw_text, re.IGNORECASE | re.DOTALL)
    if age_match:
        patient["age_years"] = int(age_match.group(1))
        patient["gender"] = "Male" if age_match.group(2).upper() == "M" else "Female"
    
    return patient
```

### Date Extraction (24-hour format)

```python
from app.services.lipid_normalization import parse_datetime_24h

# Look for two dates near each other
dates_section = re.search(
    r'(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})(?:.*?\n.*?)?(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})',
    raw_text
)

if dates_section:
    sample_date = parse_datetime_24h(dates_section.group(1), dates_section.group(2))
    report_date = parse_datetime_24h(dates_section.group(3), dates_section.group(4))
```

### Flag Extraction

```python
from app.services.lipid_normalization import extract_flag

flag, cleaned_ref_range = extract_flag(ref_range_str)
# Returns ("High", "10.0 - 200.0") if "H\n10.0\n-\n200.0"
```

## Common Patterns by Report Complexity

### Single Biomarker (Like FBS)
- Simplest to implement
- Use FBS as template
- Main challenge: Parsing combined result cell

### Multiple Biomarkers, No Flags (Like FBC)
- Medium complexity
- Use FBC as template
- Focus on name mapping and unit normalization

### Multiple Biomarkers with Flags (Like Lipid)
- Most complex
- Use Lipid Profile as template
- Handle flag extraction + ratio detection

## Testing Checklist

- [ ] Report type detection works
- [ ] Patient info extracted correctly  
- [ ] Dates converted to ISO-8601
- [ ] All biomarkers extracted
- [ ] Units normalized correctly
- [ ] Flags detected (if applicable)
- [ ] Reference ranges parsed
- [ ] FBC/Lipid/FBS still work (regression test)

## Pro Tips

1. **Start with actual OCR data** - Don't guess the format
2. **Check keyword order** - More specific first in `REPORT_TYPE_KEYWORDS`
3. **Reuse existing functions** - Don't reinvent patient/date extraction
4. **Handle OCR noise** - Use `OCR_NOISE_PATTERNS` and flexible regex
5. **Test edge cases** - Missing values, split names, noise in units
6. **Update docs** - Add example to `docs/` folder

## Minimal Working Example

Here's the absolute minimum to add a new single-biomarker report:

```python
# 1. Config (biomarker_config.py)
CREATININE_BIOMARKER_MAPPING = {"SERUM CREATININE": "Creatinine"}
REPORT_TYPE_KEYWORDS = {
    "Creatinine Test": ["SERUM CREATININE"],
    # ... existing types
}

# 2. Module (creatinine_normalization.py) - copy from FBS and adapt

# 3. Router (normalization_service.py)
elif report_type == "Creatinine Test":
    return _normalize_creatinine_report(raw_data)

# 4. Test (test_creatinine_normalization.py) - copy from FBS test
```

That's it! **~100 lines to add a new report type.**

## Need Help?

Refer to existing modules:
- **FBS** - Single biomarker, simple
- **Lipid Profile** - Multiple biomarkers with flags
- **FBC** - Multiple biomarkers with absolute counts

Each module is fully documented and tested.

---

**The system is designed for rapid expansion. Happy coding!** 🚀
