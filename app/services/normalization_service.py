"""
Medical document normalization service.
Converts noisy OCR output into clean, structured, clinically meaningful JSON.
Supports multiple report types: Full Blood Count and Serum Lipid Profile.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from app.config.biomarker_config import (
    FBC_BIOMARKER_MAPPING,
    LIPID_PROFILE_BIOMARKER_MAPPING,
    BIOMARKER_NAME_MAPPING,  # Alias for FBC_BIOMARKER_MAPPING
    UNIT_MAPPING,
    OCR_NOISE_PATTERNS,
    FLAG_MAPPING,
    REPORT_TYPE_KEYWORDS,
)


def normalize_report(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main normalization function - auto-detects report type and routes to appropriate normalizer.
    
    Args:
        raw_data: Dictionary containing raw_text, tables, entities, page_count
        
    Returns:
        Structured JSON with patient, report, and biomarkers sections
    """
    raw_text = raw_data.get("raw_text", "")
    report_type = _detect_report_type(raw_text)
    
    if report_type == "Serum Lipid Profile":
        return _normalize_lipid_profile(raw_data)
    elif report_type == "Fasting Plasma Glucose":
        return _normalize_fbs_report(raw_data)
    else:
        return _normalize_fbc_report(raw_data)


def _detect_report_type(raw_text: str) -> str:
    """
    Detect report type from raw text using keywords.
    
    Args:
        raw_text: Unstructured OCR text
        
    Returns:
        Report type name (defaults to "Full Blood Count" if unclear)
    """
    text_upper = raw_text.upper()
    
    for report_type, keywords in REPORT_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_upper:
                return report_type
    
    # Default to FBC if unclear
    return "Full Blood Count"


def _normalize_fbc_report(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalization function for Full Blood Count reports.
    
    Args:
        raw_data: Dictionary containing raw_text, tables, entities, page_count
        
    Returns:
        Structured JSON with patient, report, and biomarkers sections
    """
    raw_text = raw_data.get("raw_text", "")
    tables = raw_data.get("tables", [])
    
    # Extract patient information
    patient_info = _extract_patient_info(raw_text)
    
    # Extract report metadata (dates)
    report_metadata = _extract_report_metadata(raw_text)
    report_metadata["type"] = "Full Blood Count"  # Set report type
    
    # Normalize biomarkers from tables
    biomarkers = _normalize_fbc_biomarkers(tables)
    
    return {
        "patient": patient_info,
        "report": report_metadata,
        "biomarkers": biomarkers
    }


def _normalize_lipid_profile(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalization function for Serum Lipid Profile reports.
    
    Args:
        raw_data: Dictionary containing raw_text, tables, entities, page_count
        
    Returns:
        Structured JSON with patient, report, and biomarkers sections
    """
    from app.services.lipid_normalization import (
        extract_lipid_patient_info,
        extract_lipid_report_metadata,
        normalize_lipid_biomarkers
    )
    
    raw_text = raw_data.get("raw_text", "")
    tables = raw_data.get("tables", [])
    
    # Extract patient information (extended for lipid reports)
    patient_info = extract_lipid_patient_info(raw_text)
    
    # Extract report metadata
    report_metadata = extract_lipid_report_metadata(raw_text)
    
    # Normalize lipid biomarkers from tables
    biomarkers = normalize_lipid_biomarkers(tables)
    
    return {
        "patient": patient_info,
        "report": report_metadata,
        "biomarkers": biomarkers
    }


def _normalize_fbs_report(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalization function for Fasting Plasma Glucose (FBS) reports.
    
    Args:
        raw_data: Dictionary containing raw_text, tables, entities, page_count
        
    Returns:
        Structured JSON with patient, report, and biomarkers sections
    """
    from app.services.fbs_normalization import (
        extract_fbs_patient_info,
        extract_fbs_report_metadata,
        normalize_fbs_biomarkers
    )
    
    raw_text = raw_data.get("raw_text", "")
    tables = raw_data.get("tables", [])
    
    # Extract patient information
    patient_info = extract_fbs_patient_info(raw_text)
    
    # Extract report metadata
    report_metadata = extract_fbs_report_metadata(raw_text)
    
    # Normalize FBS biomarker from tables
    biomarkers = normalize_fbs_biomarkers(tables, raw_text)
    
    return {
        "patient": patient_info,
        "report": report_metadata,
        "biomarkers": biomarkers
    }


# Legacy alias for backward compatibility
normalize_fbc_report = normalize_report


def _extract_patient_info(raw_text: str) -> Dict[str, Optional[Any]]:
    """Extract patient demographic information from raw text."""
    patient = {
        "name": None,
        "age_years": None,
        "gender": None,
        "ref_doctor": None,
        "service_ref_no": None
    }
    
    # Extract patient name
    name_match = re.search(r'PATIENT NAME:\s*(.+?)(?:\n|REF)', raw_text, re.IGNORECASE)
    if name_match:
        patient["name"] = name_match.group(1).strip()
    
    # Extract age and gender
    # Pattern: "62 Y/O M/O D" or "62 Y/O M" etc.
    age_match = re.search(r'AGE\s+(\d+)\s*Y/?O?\s*([MF])', raw_text, re.IGNORECASE)
    if age_match:
        patient["age_years"] = int(age_match.group(1))
        gender_code = age_match.group(2).upper()
        patient["gender"] = "Male" if gender_code == "M" else "Female"
    
    # Extract referring doctor
    doctor_match = re.search(r'REF\.DOCTOR\s*:\s*(.+?)(?:\n|AGE)', raw_text, re.IGNORECASE)
    if doctor_match:
        doctor_name = doctor_match.group(1).strip()
        if doctor_name and doctor_name.upper() != "":
            patient["ref_doctor"] = doctor_name
    
    # Extract service reference number
    service_match = re.search(r'SERVICE REF\.NO\s*:\s*(.+?)(?:\n|$)', raw_text, re.IGNORECASE)
    if service_match:
        patient["service_ref_no"] = service_match.group(1).strip()
    
    return patient


def _extract_report_metadata(raw_text: str) -> Dict[str, Optional[str]]:
    """Extract report metadata including dates and report type."""
    metadata = {
        "type": "Full Blood Count",
        "sample_collected_at": None,
        "printed_at": None
    }
    
    # Extract sample collection date/time
    # Pattern: "SAMPLE COLLECTED : 03/06/2025 09:10 AM"
    sample_match = re.search(
        r'SAMPLE COLLECTED\s*:\s*(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}\s*[AP]M)',
        raw_text,
        re.IGNORECASE
    )
    if sample_match:
        date_str = sample_match.group(1)
        time_str = sample_match.group(2)
        metadata["sample_collected_at"] = _parse_datetime(date_str, time_str)
    
    # Extract printed date/time
    # Pattern: "PRINTED DATE : 03/06/2025 06:43 PM" or just "03/06/2025 06:43 PM"
    printed_match = re.search(
        r'PRINTED DATE\s*:?\s*(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}\s*[AP]M)',
        raw_text,
        re.IGNORECASE
    )
    if not printed_match:
        # Try alternate pattern
        printed_match = re.search(
            r'(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}\s*[AP]M)',
            raw_text
        )
    
    if printed_match:
        date_str = printed_match.group(1)
        time_str = printed_match.group(2)
        metadata["printed_at"] = _parse_datetime(date_str, time_str)
    
    return metadata


def _parse_datetime(date_str: str, time_str: str) -> str:
    """
    Parse date and time strings into ISO-8601 format.
    
    Args:
        date_str: Date in format DD/MM/YYYY
        time_str: Time in format HH:MM AM/PM
        
    Returns:
        ISO-8601 formatted datetime string
    """
    try:
        # Combine date and time
        datetime_str = f"{date_str} {time_str}"
        # Parse the datetime
        dt = datetime.strptime(datetime_str, "%d/%m/%Y %I:%M %p")
        # Return ISO-8601 format
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None


def _normalize_fbc_biomarkers(tables: List[List[List[str]]]) -> List[Dict[str, Any]]:
    """
    Extract and normalize FBC biomarkers from OCR tables.
    
    Args:
        tables: List of tables, each table is a list of rows, each row is a list of cells
        
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
            absolute_str = row[3].strip() if len(row) > 3 and row[3] else ""
            ref_range_str = row[4].strip() if len(row) > 4 and row[4] else ""
            
            # Skip header rows and non-test rows
            if not test_name or test_name.upper() in ["TEST NAME", "WHITE BLOOD CELLS", "RED BLOOD CELLS"]:
                continue
            
            # Check if test name matches a known biomarker
            standard_name = _get_standard_biomarker_name(test_name)
            if not standard_name:
                continue
            
            # Clean and parse the value
            clean_value = _clean_numeric_value(value_str)
            if clean_value is None:
                continue
            
            # Normalize unit
            normalized_unit = _normalize_unit(unit_str)
            
            # Infer percentage for differential count if unit is missing/noise
            if not normalized_unit and standard_name in ["Neutrophils", "Lymphocytes", "Eosinophils", "Monocytes", "Basophils", "PCV"]:
                normalized_unit = "%"

            
            # Parse absolute count if present
            absolute_count = _clean_numeric_value(absolute_str) if absolute_str else None
            
            # Parse reference range
            ref_range = _parse_reference_range(ref_range_str)
            
            # Create biomarker entry
            biomarker = {
                "name": standard_name,
                "value": clean_value,
                "unit": normalized_unit,
                "absolute": absolute_count,
                "ref_range": ref_range
            }
            
            biomarkers.append(biomarker)
    
    return biomarkers


def _get_standard_biomarker_name(test_name: str) -> Optional[str]:
    """
    Map lab test name to standard biomarker name.
    
    Args:
        test_name: Raw test name from OCR
        
    Returns:
        Standardized biomarker name or None if not found
    """
    # Clean the test name
    clean_name = test_name.strip().upper()
    
    # Try exact match
    if clean_name in BIOMARKER_NAME_MAPPING:
        return BIOMARKER_NAME_MAPPING[clean_name]
    
    # Try case-insensitive match
    for key, value in BIOMARKER_NAME_MAPPING.items():
        if key.upper() == clean_name:
            return value
    
    # Try partial match (for merged cells)
    for key, value in BIOMARKER_NAME_MAPPING.items():
        if key.upper() in clean_name or clean_name in key.upper():
            return value
    
    return None


def _normalize_unit(unit_str: str) -> str:
    """
    Normalize unit string.
    
    Args:
        unit_str: Raw unit string from OCR
        
    Returns:
        Normalized unit string
    """
    if not unit_str:
        return ""
    
    # Remove OCR noise
    cleaned = unit_str
    for noise in OCR_NOISE_PATTERNS:
        cleaned = cleaned.replace(noise, "")
    
    cleaned = cleaned.strip()
    
    # Check mapping
    if cleaned in UNIT_MAPPING:
        return UNIT_MAPPING[cleaned]
    
    # Try case-insensitive match
    for key, value in UNIT_MAPPING.items():
        if key.lower() == cleaned.lower():
            return value
    
    # Return cleaned version if no mapping found
    return cleaned


def _clean_numeric_value(value_str: str) -> Optional[float]:
    """
    Clean OCR noise from numeric values and convert to float.
    
    Args:
        value_str: Raw value string from OCR
        
    Returns:
        Cleaned numeric value or None if not parseable
    """
    if not value_str:
        return None
    
    # Remove OCR noise patterns
    cleaned = value_str
    for noise in OCR_NOISE_PATTERNS:
        cleaned = cleaned.replace(noise, "")
    
    # Remove whitespace
    cleaned = cleaned.strip()
    
    # Handle cases like "02" - remove leading zeros but keep the number
    # Extract only numeric characters and decimal point
    numeric_str = re.sub(r'[^0-9.]', '', cleaned)
    
    if not numeric_str:
        return None
    
    try:
        # Convert to float
        value = float(numeric_str)
        return value
    except ValueError:
        return None


def _parse_reference_range(range_str: str) -> Optional[List[float]]:
    """
    Parse reference range string into [min, max] array.
    
    Args:
        range_str: Raw reference range string (e.g., "4000 - 11000" or "11.0\n16.5")
        
    Returns:
        [min, max] array or None if not parseable
    """
    if not range_str:
        return None
    
    # Remove OCR noise
    cleaned = range_str
    for noise in OCR_NOISE_PATTERNS:
        cleaned = cleaned.replace(noise, "")
    
    # Try to extract two numbers
    # Pattern: number - number or number \n number
    numbers = re.findall(r'[\d.]+', cleaned)
    
    if len(numbers) >= 2:
        try:
            min_val = float(numbers[0])
            max_val = float(numbers[1])
            return [min_val, max_val]
        except ValueError:
            return None
    
    return None
