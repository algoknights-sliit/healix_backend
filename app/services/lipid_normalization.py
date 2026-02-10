"""
Lipid profile normalization functions.
Helper module for lipid-specific normalization logic.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.config.biomarker_config import (
    LIPID_PROFILE_BIOMARKER_MAPPING,
    UNIT_MAPPING,
    OCR_NOISE_PATTERNS,
    FLAG_MAPPING,
)


def extract_lipid_patient_info(raw_text: str) -> Dict[str, Optional[Any]]:
    """Extract patient demographic information for lipid profile reports."""
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
    
    # Extract age and gender
    # Pattern: "58 Y/F 25/09/1966"
    age_match = re.search(r'AGE\s*:\s*(\d+)\s*Y[/\s]*([MF])', raw_text, re.IGNORECASE)
    if age_match:
        patient["age_years"] = int(age_match.group(1))
        gender_code = age_match.group(2).upper()
        patient["gender"] = "Male" if gender_code == "M" else "Female"
    
    # Extract UHID
    uhid_match = re.search(r'UHID\s*:?\s*(\d+)', raw_text, re.IGNORECASE)
    if uhid_match:
        patient["uhid"] = uhid_match.group(1).strip()
    
    # Extract reference number - pattern like "AHH2006215 / AHH2011800"  
    # It's usually before PATIENT field in the text
    ref_match = re.search(r'([A-Z]{3}\d+\s*/\s*[A-Z]{3}\d+)', raw_text)
    if ref_match:
        patient["reference_no"] = ref_match.group(1).strip()
    
    return patient


def extract_lipid_report_metadata(raw_text: str) -> Dict[str, Optional[str]]:
    """Extract lipid report metadata including sample type and dates."""
    metadata = {
        "type": "Serum Lipid Profile",
        "sample_type": None,
        "sample_collected_at": None,
        "reported_at": None
    }
    
    # Extract sample type
    sample_type_match = re.search(r'SAMPLE TYPE\s*:\s*(\w+)', raw_text, re.IGNORECASE)
    if sample_type_match:
        metadata["sample_type"] = sample_type_match.group(1).strip()
    
    # Extract sample date & time - may be on separate lines or after other text
    # Look for two dates near each other
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


def parse_datetime_24h(date_str: str, time_str: str) -> Optional[str]:
    """
    Parse date and time (24-hour format) into ISO-8601 format.
    
    Args:
        date_str: Date in format DD/MM/YYYY
        time_str: Time in format HH:MM (24-hour)
        
    Returns:
        ISO-8601 formatted datetime string
    """
    try:
        datetime_str = f"{date_str} {time_str}"
        dt = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None


def normalize_lipid_biomarkers(tables: List[List[List[str]]]) -> List[Dict[str, Any]]:
    """
    Extract and normalize lipid biomarkers from OCR tables.
    
    Args:
        tables: List of tables from OCR
        
    Returns:
        List of normalized biomarker dictionaries
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
            value_str = row[1].strip() if len(row) > 1 and row[1] else ""
            unit_str = row[2].strip() if len(row) > 2 and row[2] else ""
            ref_range_str = row[3].strip() if len(row) > 3 and row[3] else ""
            
            # Skip header/comment rows
            if not test_name or test_name.upper() in ["TEST", "RESULT", "COMMENT", "TEST/PROFILE"]:
                continue
            
            # Check if test name matches a known lipid biomarker
            standard_name = get_standard_lipid_name(test_name)
            if not standard_name:
                continue
            
            # Clean and parse the value
            clean_value = clean_numeric_value(value_str)
            if clean_value is None:
                continue
            
            # Extract flag and clean reference range
            flag, cleaned_ref_range = extract_flag(ref_range_str)
            
            # Normalize unit (ratios have no unit)
            if "Ratio" in standard_name:
                normalized_unit = None
            else:
                normalized_unit = normalize_unit(unit_str)
            
            # Parse reference range
            ref_range = parse_reference_range(cleaned_ref_range)
            
            # Create biomarker entry
            biomarker = {
                "name": standard_name,
                "value": clean_value,
                "unit": normalized_unit,
                "flag": flag,
                "ref_range": ref_range
            }
            
            biomarkers.append(biomarker)
    
    return biomarkers


def get_standard_lipid_name(test_name: str) -> Optional[str]:
    """Map lab test name to standard lipid biomarker name."""
    clean_name = test_name.strip().upper()
    
    # Remove newlines and extra spaces
    clean_name = re.sub(r'\s+', ' ', clean_name)
    
    # Try exact match
    if clean_name in LIPID_PROFILE_BIOMARKER_MAPPING:
        return LIPID_PROFILE_BIOMARKER_MAPPING[clean_name]
    
    # Try case-insensitive match
    for key, value in LIPID_PROFILE_BIOMARKER_MAPPING.items():
        if key.upper() == clean_name:
            return value
    
    # Try partial match
    for key, value in LIPID_PROFILE_BIOMARKER_MAPPING.items():
        if key.upper() in clean_name or clean_name in key.upper():
            return value
    
    return None


def extract_flag(ref_range_str: str) -> tuple[Optional[str], str]:
    """
    Extract H/L flag from reference range string and return cleaned range.
    
    Args:
        ref_range_str: Raw reference range string (may contain H or L)
        
    Returns:
        Tuple of (flag, cleaned_range_str)
    """
    if not ref_range_str:
        return (None, "")
    
    flag = None
    cleaned = ref_range_str
    
    # Check for flag indicators
    for flag_code, flag_value in FLAG_MAPPING.items():
        # Look for standalone H or L
        pattern = r'\b' + flag_code + r'\b'
        if re.search(pattern, ref_range_str, re.IGNORECASE):
            flag = flag_value
            # Remove the flag from the string
            cleaned = re.sub(pattern, '', ref_range_str, flags=re.IGNORECASE)
            break
    
    return (flag, cleaned.strip())


def normalize_unit(unit_str: str) -> Optional[str]:
    """Normalize unit string."""
    if not unit_str:
        return None
    
    # Remove OCR noise
    cleaned = unit_str
    for noise in OCR_NOISE_PATTERNS:
        cleaned = cleaned.replace(noise, "")
    
    cleaned = cleaned.strip()
    
    if not cleaned:
        return None
    
    # Check mapping
    if cleaned in UNIT_MAPPING:
        return UNIT_MAPPING[cleaned]
    
    # Try case-insensitive match
    for key, value in UNIT_MAPPING.items():
        if key.lower() == cleaned.lower():
            return value
    
    return cleaned


def clean_numeric_value(value_str: str) -> Optional[float]:
    """Clean OCR noise from numeric values and convert to float."""
    if not value_str:
        return None
    
    # Remove OCR noise patterns
    cleaned = value_str
    for noise in OCR_NOISE_PATTERNS:
        cleaned = cleaned.replace(noise, "")
    
    cleaned = cleaned.strip()
    
    # Extract only numeric characters and decimal point
    numeric_str = re.sub(r'[^0-9.]', '', cleaned)
    
    if not numeric_str:
        return None
    
    try:
        return float(numeric_str)
    except ValueError:
        return None


def parse_reference_range(range_str: str) -> Optional[List[float]]:
    """Parse reference range string into [min, max] array."""
    if not range_str:
        return None
    
    # Remove OCR noise
    cleaned = range_str
    for noise in OCR_NOISE_PATTERNS:
        cleaned = cleaned.replace(noise, "")
    
    # Extract numbers
    numbers = re.findall(r'[\d.]+', cleaned)
    
    if len(numbers) >= 2:
        try:
            min_val = float(numbers[0])
            max_val = float(numbers[1])
            return [min_val, max_val]
        except ValueError:
            return None
    
    return None
