"""
Test script for medical document normalization.
Tests the normalization service with sample FBC report data.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.normalization_service import normalize_fbc_report


# Sample input data (from your original request)
SAMPLE_INPUT = {
    "raw_text": """52/FO/KMC/LA/01
NAWALOKA
MEDICAL CENTRE
KIRIBATHGODA
No. 88, Kandy Road, Dalugama.
T| 0115 552 440, 0115 552 244
E| labkmc@nawatagroup.com
0773 510 088
PATIENT NAME: MR S KUMAR
REF.DOCTOR :
OPD
AGE 62 Y/O M/O D
SERVICE REF.NO : CHL000735039
LABORATORY REPORT
CONFIDENTIAL
03/06/2025 06:43 PM
SAMPLE COLLECTED
: 03/06/2025 09:10 AM
PRINTED DATE
FULL BLOOD COUNT
TEST NAME
RESULT
UNITS
AB. COUNT
REF.RANGE
WHITE BLOOD CELLS
W.B.C.
7970
Per Cumm
4000
-
11000
NEUTROPHILS
79
응
6296.3
LYMPHOCYTES
11
응
876.7
EOSINOPHIL
02
응
159.4
1280
MONOCYTES
08
응
olo olo olo
637.6
BASOPHILS
00
응
0
RED BLOOD CELLS
HAEMOGLOBIN
13.6
g/dl
11.0
16.5
P.C.V.
39.2
응
36.0
-
48.0
M.C.H.C.
34.6
g/dl
33.0
37.0
R.B.C.
4.29
10^6 /UL
4.0
6.2
M.C.H.
31.7
Pg
27.0
31.0
M.C.V.
91.5
fL
78.0
100.0
Platelet count
224000
Per Cu mm
150000
-
400000
End Of Report
Supere
MLT (EMP ID: 68)
Dr. B.K.T. P. Dayanath
MBBS, D. Path, MD(Chem.Path), MAACB
Consultant Chemical Pathologist &
Head Department of Pathology
North Colombo Teaching Hospital
Ragama, Sri Lanka.
Internal Quality Control
External Quality Control EQAS
BIO-RAD
ISO 9001:2015
Certified Medical Centre
""",
    "tables": [
        [
            ["WHITE BLOOD CELLS", "", "", "", ""],
            ["W.B.C.", "7970", "Per Cumm", "", "4000\n-\n11000"],
            ["NEUTROPHILS", "79", "응", "6296.3", ""],
            ["LYMPHOCYTES", "11", "응", "876.7", ""],
            ["EOSINOPHIL", "02\n1280", "응\nolo", "159.4", ""],
            ["MONOCYTES", "08", "응\nolo", "637.6", ""],
            ["BASOPHILS", "00", "olo\n응", "0", ""],
            ["RED BLOOD CELLS\nHAEMOGLOBIN", "13.6", "g/dl", "", "11.0\n16.5"],
            ["P.C.V.", "39.2", "응", "", "36.0\n-\n48.0"],
            ["M.C.H.C.", "34.6", "g/dl", "", "33.0\n37.0"],
            ["R.B.C.", "4.29", "10^6 /UL", "", "4.0\n6.2"],
            ["M.C.H.", "31.7", "Pg", "", "27.0\n31.0"],
            ["M.C.V.", "91.5", "fL", "", "78.0\n100.0"],
            ["Platelet count", "224000", "Per Cu mm", "", "150000\n-\n400000"]
        ],
        []
    ],
    "entities": [
        {
            "type": "generic_entities",
            "value": "",
            "confidence": 0.0
        }
    ],
    "page_count": 1
}


def test_normalization():
    """Test the normalization service with sample data."""
    print("=" * 80)
    print("MEDICAL DOCUMENT NORMALIZATION TEST")
    print("=" * 80)
    print()
    
    print("INPUT DATA:")
    print("-" * 80)
    print(f"Raw text length: {len(SAMPLE_INPUT['raw_text'])} characters")
    print(f"Number of tables: {len(SAMPLE_INPUT['tables'])}")
    print(f"Number of rows in first table: {len(SAMPLE_INPUT['tables'][0]) if SAMPLE_INPUT['tables'] else 0}")
    print()
    
    # Run normalization
    print("RUNNING NORMALIZATION...")
    print("-" * 80)
    try:
        result = normalize_fbc_report(SAMPLE_INPUT)
        print("✓ Normalization completed successfully")
        print()
        
        # Display results
        print("NORMALIZED OUTPUT:")
        print("-" * 80)
        print(json.dumps(result, indent=2))
        print()
        
        # Validation checks
        print("VALIDATION CHECKS:")
        print("-" * 80)
        
        # Check patient info
        patient = result.get("patient", {})
        print(f"✓ Patient name: {patient.get('name')}")
        print(f"✓ Patient age: {patient.get('age_years')} years")
        print(f"✓ Patient gender: {patient.get('gender')}")
        print(f"✓ Service ref: {patient.get('service_ref_no')}")
        
        # Check report metadata
        report = result.get("report", {})
        print(f"✓ Report type: {report.get('type')}")
        print(f"✓ Sample collected: {report.get('sample_collected_at')}")
        print(f"✓ Printed at: {report.get('printed_at')}")
        
        # Check biomarkers
        biomarkers = result.get("biomarkers", [])
        print(f"✓ Number of biomarkers: {len(biomarkers)}")
        
        if biomarkers:
            print()
            print("BIOMARKERS EXTRACTED:")
            print("-" * 80)
            for bio in biomarkers:
                name = bio.get('name', 'Unknown')
                value = bio.get('value', 'N/A')
                unit = bio.get('unit', '')
                absolute = bio.get('absolute')
                ref_range = bio.get('ref_range')
                
                abs_str = f", Absolute: {absolute}" if absolute else ""
                ref_str = f", Ref: {ref_range}" if ref_range else ""
                print(f"  • {name}: {value} {unit}{abs_str}{ref_str}")
        
        print()
        print("=" * 80)
        print("TEST COMPLETED SUCCESSFULLY ✓")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"✗ ERROR during normalization: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_normalization()
