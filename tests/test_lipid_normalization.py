"""
Test script for Serum Lipid Profile normalization.
Tests the normalization service with the provided lipid profile sample.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.normalization_service import normalize_report


# Sample lipid profile data
LIPID_PROFILE_SAMPLE = {
    "raw_text": """www.asirihealth.com
LAB/FOR-07
CONFIDENTIAL LABORATORY REPORT
Member of Clinical and Laboratory Standards Institute, U.S.A.
ASIRI
Sri Lanka
NATIONAL
Member of
Member of
hin
Asiri Laboratories
5322
CLINICAL AND
LABORATORY
STANDARDS
INSTITUTE
AACC
QUALITY
4
LABORATORIES
YEARS OF
150 14001
ROYALCERT
UKAS
MANAGEMENT
American Association for Cc Chemistry
On
SGS
LIVE
MORE
005
QUALITY
MERIT 2019
Member ID #383029
Member Number: 4790
A Softlogic Group Company
Accuracy, Reliability Trust
Asiri Hospital Holdings PLC, 181, Kirula Road, Narahenpita, Colombo 05
T. +94 11 452 3355-7 F. +94 11 452 3358 prlab@asiri.lk
CLINICAL CHEMISTRY
**
OPD/KELANIYA/ALS **
Page 2 of 2
UHID
310225949
(nitf 667692237v)
:
REFERENCE No.
:
SAMPLE DATE & TIME
43 0003 12/06/25
12/06/2025 06:50
12/06/2025 17:04
:
AGE
: 58 Y/F 25/09/1966
REPORT DATE & TIME
AHH2006215 / AHH2011800
:
PATIENT
:
MRS. S N MANEL
REFERRED BY
:
SAMPLE TYPE
: Serum
TEST/PROFILE
:
SERUM LIPID PROFILE
TEST
RESULT
FLAG
REFERENCE VALUE
SERUM CHOLESTEROL
-
TOTAL
204.2
mg/dL
140.0
-
239.0
SERUM TRIGLYCERIDES
219.1
mg/dL
H
10.0
-
200.0
CHOLESTEROL-H.D.L.
48.9
mg/dL
35.0
-
85.0
CHOLESTEROL
-
NON
-
H.D.L
155.3
mg/dL
55.0
-
189.0
CHOLESTEROL L.D.L
111.5
mg/dL
50.0
- 159.0
CHOLESTEROL
-
VLDL
43.8
mg/dL
H
10.0
41.0
-
CHOL/HDL
4.1
2.0
- 5.0
LDL/HDL
2.28
0.01
3.30
Comment
:-
""",
    "tables": [
        [
            ["SERUM CHOLESTEROL\n-\nTOTAL", "204.2", "mg/dL", "140.0\n-\n239.0"],
            ["SERUM TRIGLYCERIDES", "219.1", "mg/dL", "H\n10.0\n-\n200.0"],
            ["CHOLESTEROL-H.D.L.", "48.9", "mg/dL", "35.0\n-\n85.0"],
            ["CHOLESTEROL\n-\nNON\n-\nH.D.L", "155.3", "mg/dL", "55.0\n-\n189.0"],
            ["CHOLESTEROL L.D.L", "111.5", "mg/dL", "50.0\n- 159.0"],
            ["CHOLESTEROL\n-\nVLDL", "43.8", "mg/dL", "H\n10.0\n41.0\n-"],
            ["CHOL/HDL", "4.1", "", "2.0\n- 5.0"],
            ["LDL/HDL", "2.28", "", "0.01\n3.30"],
            ["Comment\n:-", "", "", ""]
        ]
    ],
    "entities": [],
    "page_count": 1
}


def test_lipid_normalization():
    """Test lipid profile normalization."""
    print("=" * 80)
    print("SERUM LIPID PROFILE NORMALIZATION TEST")
    print("=" * 80)
    print()
    
    print("INPUT DATA:")
    print("-" * 80)
    print(f"Number of tables: {len(LIPID_PROFILE_SAMPLE['tables'])}")
    print(f"Number of rows in first table: {len(LIPID_PROFILE_SAMPLE['tables'][0])}")
    print()
    
    # Run normalization
    print("RUNNING NORMALIZATION...")
    print("-" * 80)
    try:
        result = normalize_report(LIPID_PROFILE_SAMPLE)
        print("✓ Normalization completed successfully")
        print()
        
        # Display results
        print("NORMALIZED OUTPUT:")
        print("-" * 80)
        output = json.dumps(result, indent=2)
        print(output)
        print()
        
        # Validation checks
        print("VALIDATION CHECKS:")
        print("-" * 80)
        
        # Check report type
        report = result.get("report", {})
        print(f"✓ Report type: {report.get('type')}")
        assert report.get('type') == "Serum Lipid Profile", "Wrong report type!"
        
        # Check patient info
        patient = result.get("patient", {})
        print(f"✓ Patient name: {patient.get('name')}")
        print(f"✓ Patient age: {patient.get('age_years')} years")
        print(f"✓ Patient gender: {patient.get('gender')}")
        print(f"✓ UHID: {patient.get('uhid')}")
        print(f"✓ Reference No: {patient.get('reference_no')}")
        
        assert patient.get('name') == "MRS. S N MANEL", "Wrong patient name!"
        assert patient.get('age_years') == 58, "Wrong age!"
        assert patient.get('gender') == "Female", "Wrong gender!"
        assert patient.get('uhid') == "310225949", "Wrong UHID!"
        
        # Check report metadata
        print(f"✓ Sample type: {report.get('sample_type')}")
        print(f"✓ Sample collected: {report.get('sample_collected_at')}")
        print(f"✓ Reported at: {report.get('reported_at')}")
        
        assert report.get('sample_type') == "Serum", "Wrong sample type!"
        
        # Check biomarkers
        biomarkers = result.get("biomarkers", [])
        print(f"✓ Number of biomarkers: {len(biomarkers)}")
        
        assert len(biomarkers) == 8, f"Expected 8 biomarkers, got {len(biomarkers)}!"
        
        print()
        print("BIOMARKERS EXTRACTED:")
        print("-" * 80)
        
        expected_flags = {
            "Triglycerides": "High",
            "VLDL Cholesterol": "High"
        }
        
        for bio in biomarkers:
            name = bio.get('name')
            value = bio.get('value')
            unit = bio.get('unit')
            flag = bio.get('flag')
            ref_range = bio.get('ref_range')
            
            flag_str = f", Flag: {flag}" if flag else ""
            unit_str = f" {unit}" if unit else ""
            ref_str = f", Ref: {ref_range}" if ref_range else ""
            
            print(f"  • {name}: {value}{unit_str}{flag_str}{ref_str}")
            
            # Validate flags
            if name in expected_flags:
                assert flag == expected_flags[name], f"{name} should have flag {expected_flags[name]}, got {flag}!"
            
            # Validate ratios have no unit
            if "Ratio" in name:
                assert unit is None, f"{name} should have no unit, got {unit}!"
        
        # Save output
        with open("tests/lipid_normalized_output.json", "w") as f:
            f.write(output)
        
        print()
        print("=" * 80)
        print("TEST COMPLETED SUCCESSFULLY ✓")
        print("Output saved to tests/lipid_normalized_output.json")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"✗ ERROR during normalization: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_lipid_normalization()
