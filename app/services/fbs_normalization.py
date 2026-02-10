"""
Fasting Plasma Glucose (FBS) normalization functions.
Helper module for FBS-specific normalization logic.
"""

import re
from typing import Dict, List, Optional, Any
from app.config.biomarker_config import (
    FBS_BIOMARKER_MAPPING,
    UNIT_MAPPING,
    OCR_NOISE_PATTERNS,
)


def extract_fbs_patient_info(raw_text: str) -> Dict[str, Optional[Any]]:
    """Extract patient demographic information for FBS reports (same as lipid)."""
    patient = {
        "name": None,
        "age_years": None,
        "gender": None,
        "uhid": None,
        "reference_no": None
    }
    
    # Extract patient name
    name_match = re.search(r'PATIENT\s*:\s*(.+?)(?:\n|REFERRED)', raw_text, re.IGNORECASE)
    if name_match:
        patient["name"] = name_match.group(1).strip()
    
    #Extract age and gender
    # Pattern 1: "AGE : 58 Y/F" or "AGE\n...\n: 58 Y/F"
    age_match = re.search(r'AGE.*?:\s*(\d+)\s*Y[/\s]*([MF])', raw_text, re.IGNORECASE | re.DOTALL)
    if not age_match:
        # Pattern 2: Just ": 58 Y/F" after some context
        age_match = re.search(r':\s*(\d+)\s*Y[/\s]*([MF])', raw_text, re.IGNORECASE)
    
    if age_match:
        patient["age_years"] = int(age_match.group(1))
        gender_code = age_match.group(2).upper()
        patient["gender"] = "Male" if gender_code == "M" else "Female"
    
    # Extract UHID - may be on separate line
    uhid_match = re.search(r'UHID.*?(\d{8,})', raw_text, re.IGNORECASE | re.DOTALL)
    if uhid_match:
        patient["uhid"] = uhid_match.group(1).strip()
    
    # Extract reference number - pattern like "AHH2009957 / AHH2011800"
    ref_match = re.search(r'([A-Z]{3}\d+\s*/\s*[A-Z]{3}\d+)', raw_text)
    if ref_match:
        patient["reference_no"] = ref_match.group(1).strip()
    
    return patient


def extract_fbs_report_metadata(raw_text: str) -> Dict[str, Optional[str]]:
    """Extract FBS report metadata including sample type and dates."""
    from app.services.lipid_normalization import parse_datetime_24h
    
    metadata = {
        "type": "Fasting Plasma Glucose",
        "sample_type": None,
        "sample_collected_at": None,
        "reported_at": None
    }
    
    # Extract sample type
    sample_type_match = re.search(r'SAMPLE TYPE\s*:\s*(\w+)', raw_text, re.IGNORECASE)
    if sample_type_match:
        metadata["sample_type"] = sample_type_match.group(1).strip()
    
    # Extract sample date & time - look for two dates near each other
    dates_section = re.search(
        r'(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})(?:.*?\n.*?)?(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})',
        raw_text
    )
    
    if dates_section:
        # First date is usually sample date
        sample_date = dates_section.group(1)
        sample_time = dates_section.group(2)
        metadata["sample_collected_at"] = parse_datetime_24h(sample_date, sample_time)
        
        # Second date is usually report date
        report_date = dates_section.group(3)
        report_time = dates_section.group(4)
        metadata["reported_at"] = parse_datetime_24h(report_date, report_time)
    
    return metadata


def normalize_fbs_biomarkers(tables: List[List[List[str]]], raw_text: str) -> List[Dict[str, Any]]:
    """
    Extract and normalize FBS biomarker from OCR tables.
    
    Args:
        tables: List of tables from OCR
        raw_text: Raw text for fallback reference range extraction
        
    Returns:
        List with single FBS biomarker dictionary
    """
    biomarkers = []
    
    for table in tables:
        if not table:
            continue
            
        for row in table:
            if len(row) < 2:
                continue
            
            # Extract row data
            test_name = row[0].strip() if row[0] else ""
            result_cell = row[1].strip() if len(row) > 1 and row[1] else ""
            
            # Skip header/non-test rows
            if not test_name or test_name.upper() in ["TEST", "RESULT", "SAMPLE TYPE"]:
                continue
            
            # Check if test name matches FBS
            standard_name = get_standard_fbs_name(test_name)
            if not standard_name:
                continue
            
            # Parse the result cell which may contain value, unit, and ref range
            # Example: "102.9\nmg/d\n0.\n-\n99."
            value, unit, ref_range = parse_fbs_result_cell(result_cell, raw_text)
            
            if value is None:
                continue
            
            # Calculate flag based on reference range
            flag = calculate_fbs_flag(value, ref_range)
            
            # Create biomarker entry
            biomarker = {
                "name": standard_name,
                "value": value,
                "unit": unit,
                "flag": flag,
                "ref_range": ref_range
            }
            
            biomarkers.append(biomarker)
            break  # FBS has only one biomarker
    
    return biomarkers


def get_standard_fbs_name(test_name: str) -> Optional[str]:
    """Map lab test name to standard FBS biomarker name."""
    clean_name = test_name.strip().upper()
    
    # Remove newlines and extra spaces
    clean_name = re.sub(r'\s+', ' ', clean_name)
    
    # Try exact match
    if clean_name in FBS_BIOMARKER_MAPPING:
        return FBS_BIOMARKER_MAPPING[clean_name]
    
    # Try case-insensitive match
    for key, value in FBS_BIOMARKER_MAPPING.items():
        if key.upper() == clean_name:
            return value
    
    # Try partial match
    for key, value in FBS_BIOMARKER_MAPPING.items():
        if key.upper() in clean_name or clean_name in key.upper():
            return value
    
    return None


def parse_fbs_result_cell(result_cell: str, raw_text: str) -> tuple[Optional[float], Optional[str], Optional[List[float]]]:
    """
    Parse FBS result cell containing value, unit, and potentially reference range.
    
    Args:
        result_cell: The cell containing result data (e.g., "102.9\nmg/d\n0.\n-\n99.")
        raw_text: Full raw text for fallback reference range extraction
        
    Returns:
        Tuple of (value, unit, ref_range)
    """
    # Clean the cell
    cleaned = result_cell
    for noise in OCR_NOISE_PATTERNS:
        cleaned = cleaned.replace(noise, "")
    
    # Extract numeric value (first number found)
    value_match = re.search(r'([\d.]+)', cleaned)
    value = float(value_match.group(1)) if value_match else None
    
    # Extract unit
    unit_match = re.search(r'mg/d[Ll]?', cleaned, re.IGNORECASE)
    unit = None
    if unit_match:
        unit_str = unit_match.group(0)
        # Normalize unit
        if unit_str.lower() in ['mg/d', 'mg/dl']:
            unit = "mg/dL"
        else:
            for key, val in UNIT_MAPPING.items():
                if key.lower() == unit_str.lower():
                    unit = val
                    break
            if not unit:
                unit = "mg/dL"  # Default for FBS
    else:
        unit = "mg/dL"  # Default unit for FBS
    
    # Extract reference range from cell
    ref_range = extract_ref_range_from_cell(cleaned)
    
    # If reference range looks invalid (e.g., starts with 0), use comment section
    if not ref_range or (ref_range and ref_range[0] < 10):
        # Look for "70 - 99 = Normal" in raw_text
        comment_match = re.search(r'(\d{2,3})\s*-\s*(\d{2,3})\s*=\s*Normal', raw_text, re.IGNORECASE)
        if comment_match:
            min_val = float(comment_match.group(1))
            max_val = float(comment_match.group(2))
            ref_range = [min_val, max_val]
    
    return (value, unit, ref_range)


def extract_ref_range_from_cell(cell_text: str) -> Optional[List[float]]:
    """Extract reference range from result cell."""
    if not cell_text:
        return None
    
    # Look for pattern like "70 - 99" or "0. - 99."
    numbers = re.findall(r'[\d.]+', cell_text)
    
    # Skip first number (it's the result value)
    # Look for next two numbers as range
    if len(numbers) >= 3:
        try:
            # Try last two numbers as range
            min_val = float(numbers[-2])
            max_val = float(numbers[-1])
            
            # Validate range makes sense
            if min_val < max_val and max_val > 50:  # FBS ranges are typically 70-99 or similar
                return [min_val, max_val]
        except ValueError:
            pass
    
    return None


def calculate_fbs_flag(value: float, ref_range: Optional[List[float]]) -> Optional[str]:
    """
    Calculate flag based on FBS reference range.
    
    FBS Guidelines:
    - < 70 mg/dL: Low (Hypoglycemia)
    - 70-99 mg/dL: Normal
    - 100-125 mg/dL: Prediabetes (High)
    - >= 126 mg/dL: Diabetes (High)
    
    Args:
        value: FBS value in mg/dL
        ref_range: Reference range [min, max]
        
    Returns:
        "High", "Low", or None
    """
    if not ref_range or len(ref_range) < 2:
        # Use standard FBS ranges if not provided
        ref_range = [70.0, 99.0]
    
    min_val, max_val = ref_range
    
    if value < min_val:
        return "Low"
    elif value > max_val:
        return "High"
    else:
        return None
