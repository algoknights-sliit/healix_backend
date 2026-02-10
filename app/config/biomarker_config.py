"""
Biomarker configuration for medical document normalization.
Contains standardized biomarker names, unit mappings, and OCR noise patterns.
"""

# ===== FULL BLOOD COUNT (FBC) =====

# Biomarker name mapping: Lab report names → Standardized names
FBC_BIOMARKER_MAPPING = {
    # White Blood Cells
    "W.B.C.": "WBC",
    "WHITE BLOOD CELLS": "WBC",
    "WBC": "WBC",
    
    # Differential Count
    "NEUTROPHILS": "Neutrophils",
    "LYMPHOCYTES": "Lymphocytes",
    "EOSINOPHIL": "Eosinophils",
    "EOSINOPHILS": "Eosinophils",
    "MONOCYTES": "Monocytes",
    "BASOPHILS": "Basophils",
    
    # Red Blood Cells
    "R.B.C.": "RBC",
    "RED BLOOD CELLS": "RBC",
    "RBC": "RBC",
    "HAEMOGLOBIN": "Hemoglobin",
    "HEMOGLOBIN": "Hemoglobin",
    
    # Red Cell Indices
    "M.C.V.": "MCV",
    "MCV": "MCV",
    "M.C.H.": "MCH",
    "MCH": "MCH",
    "M.C.H.C.": "MCHC",
    "MCHC": "MCHC",
    "P.C.V.": "PCV",
    "PCV": "PCV",
    "HCT": "PCV",
    "HEMATOCRIT": "PCV",
    
    # Platelets
    "PLATELET COUNT": "Platelets",
    "PLATELETS": "Platelets",
    "PLT": "Platelets",
}

# Legacy alias for backward compatibility
BIOMARKER_NAME_MAPPING = FBC_BIOMARKER_MAPPING

# ===== SERUM LIPID PROFILE =====

LIPID_PROFILE_BIOMARKER_MAPPING = {
    # Total Cholesterol
    "SERUM CHOLESTEROL - TOTAL": "Total Cholesterol",
    "TOTAL CHOLESTEROL": "Total Cholesterol",
    "CHOLESTEROL - TOTAL": "Total Cholesterol",
    "CHOLESTEROL TOTAL": "Total Cholesterol",
    
    # Triglycerides
    "SERUM TRIGLYCERIDES": "Triglycerides",
    "TRIGLYCERIDES": "Triglycerides",
    
    # HDL Cholesterol
    "CHOLESTEROL-H.D.L.": "HDL Cholesterol",
    "CHOLESTEROL - H.D.L.": "HDL Cholesterol",
    "CHOLESTEROL-HDL": "HDL Cholesterol",
    "HDL CHOLESTEROL": "HDL Cholesterol",
    "HDL": "HDL Cholesterol",
    
    # Non-HDL Cholesterol
    "CHOLESTEROL - NON - H.D.L": "Non-HDL Cholesterol",
    "CHOLESTEROL-NON-HDL": "Non-HDL Cholesterol",
    "NON-HDL CHOLESTEROL": "Non-HDL Cholesterol",
    "NON HDL": "Non-HDL Cholesterol",
    
    # LDL Cholesterol
    "CHOLESTEROL L.D.L": "LDL Cholesterol",
    "CHOLESTEROL - L.D.L": "LDL Cholesterol",
    "CHOLESTEROL-LDL": "LDL Cholesterol",
    "LDL CHOLESTEROL": "LDL Cholesterol",
    "LDL": "LDL Cholesterol",
    
    # VLDL Cholesterol
    "CHOLESTEROL - VLDL": "VLDL Cholesterol",
    "CHOLESTEROL-VLDL": "VLDL Cholesterol",
    "VLDL CHOLESTEROL": "VLDL Cholesterol",
    "VLDL": "VLDL Cholesterol",
    
    # Ratios
    "CHOL/HDL": "Cholesterol/HDL Ratio",
    "CHOLESTEROL/HDL RATIO": "Cholesterol/HDL Ratio",
    "TC/HDL": "Cholesterol/HDL Ratio",
    
    "LDL/HDL": "LDL/HDL Ratio",
    "LDL/HDL RATIO": "LDL/HDL Ratio",
}

# ===== FASTING PLASMA GLUCOSE (FBS) =====

FBS_BIOMARKER_MAPPING = {
    "FASTING PLASMA GLUCOSE": "Fasting Plasma Glucose",
    "FASTING GLUCOSE": "Fasting Plasma Glucose",
    "FBS": "Fasting Plasma Glucose",
    "PLASMA GLUCOSE": "Fasting Plasma Glucose",
    "FASTING PLASMA GLUCOSE (FBS)": "Fasting Plasma Glucose",
    "FASTING\nLASMA GLUCOSE": "Fasting Plasma Glucose",  # OCR noise
    "FASTING\nLASMA GLUCOSE (FBS)": "Fasting Plasma Glucose",
}

# ===== COMMON CONFIGURATION =====

# Unit normalization mapping
UNIT_MAPPING = {
    # Volume units
    "Per Cumm": "per cu mm",
    "Per Cu mm": "per cu mm",
    "per cumm": "per cu mm",
    "per cu mm": "per cu mm",
    "/cumm": "per cu mm",
    "/cu mm": "per cu mm",
    
    # Concentration units
    "g/dl": "g/dL",
    "g/dL": "g/dL",
    "gm/dl": "g/dL",
    "gm/dL": "g/dL",
    
    # Lipid units
    "mg/dl": "mg/dL",
    "mg/dL": "mg/dL",
    "mg/DL": "mg/dL",
    "MG/DL": "mg/dL",
    
    # Mass units
    "Pg": "pg",
    "pg": "pg",
    "PG": "pg",
    
    # Volume units (cells)
    "fL": "fL",
    "fl": "fL",
    "FL": "fL",
    
    # Cell count units
    "10^6 /UL": "10^6/uL",
    "10^6/UL": "10^6/uL",
    "10^6/ul": "10^6/uL",
    "10^6 /ul": "10^6/uL",
    
    # Percentage
    "%": "%",
    "percent": "%",
    "Percent": "%",
}

# Flag mapping for lipid profiles (H/L indicators)
FLAG_MAPPING = {
    "H": "High",
    "L": "Low",
    "HIGH": "High",
    "LOW": "Low",
}

# Report type detection keywords
# Order matters: Check more specific patterns first!
REPORT_TYPE_KEYWORDS = {
    "Fasting Plasma Glucose": ["FASTING PLASMA GLUCOSE", "PLASMA GLUCOSE (FBS)", "LASMA GLUCOSE (FBS)"],
    "Serum Lipid Profile": ["SERUM LIPID PROFILE", "LIPID PROFILE", "LIPID PANEL", "CHOLESTEROL PANEL"],
    "Full Blood Count": ["FULL BLOOD COUNT", "COMPLETE BLOOD COUNT"],
}

# OCR noise patterns (strings to remove or ignore)
OCR_NOISE_PATTERNS = [
    "\uc751",  # Korean character
    "olo",     # OCR artifact
    "O1O",     # OCR artifact (O instead of 0)
    "O",       # When used as zero
]

# Keywords to ignore (non-medical content)
IGNORE_KEYWORDS = [
    "NAWALOKA",
    "ASIRI",
    "MEDICAL CENTRE",
    "ISO 9001",
    "ISO 14001",
    "Certified",
    "Internal Quality Control",
    "External Quality Control",
    "EQAS",
    "BIO-RAD",
    "UKAS",
    "ROYALCERT",
    "SGS",
    "AACC",
    "CLSI",
    "End Of Report",
    "MLT",
    "MBBS",
    "Consultant",
    "Department of Pathology",
    "Member of",
    "Member ID",
    "Member Number",
    "www.",
    ".com",
    ".lk",
]

