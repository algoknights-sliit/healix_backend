"""
Test script for Fasting Plasma Glucose (FBS) normalization.
Tests the normalization service with the provided FBS sample.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.normalization_service import normalize_report


# Sample FBS data
FBS_SAMPLE = {
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
Page 1 of 2
UHID
:
REFERENCE No.
:
310225949
(nitf 667692237v)
43 0003 12/06/25
12/06/2025 06:50
AGE
12/06/2025 16:37
AHH2009957 / AHH2011800
SAMPLE DATE & TIME
: 58 Y/F 25/09/1966
:
REPORT DATE & TIME
:
PATIENT
:
MRS. S N MANEL
REFERRED BY
:
SAMPLE TYPE
:
Plasma
TEST
RESULT
FLAG
REFERENCE VALUE
FASTING
LASMA GLUCOSE (FBS)
102.9
mg/d
0.
-
99.
Comment
-:
Reference ranges
:
70
-
99
= Normal fasting glucose.
mg/dL ( 3.9 -
125 mg/dL ( 5.6
5.5 mmol/L)
6.9 mmol/L)
100
-
=
Prediabetes
(impaired fasting glucose)
High fasting glucose.
>
126
mg/dL ( >
7.0 mmol/L)
=
CONVERSION FACTOR
:
( mmol/L
=
mg/dL X 0.055 )""",
    "tables": [
        [
            ["125 mg/dL 100\n-", "( 5.6\n6.9 mmol/L)", "=\nPrediabetes"],
            [">\n126\nmg/dL", "( >\n7.0 mmol/L)", "(impaired fasting glucose)\nHigh fasting glucose.\n="]
        ],
        [
            ["FASTING\nLASMA GLUCOSE (FBS)", "102.9\nmg/d\n0.\n-\n99."]
        ],
        [
            ["005\nMember ID #383029", "Member Number: 4790"]
        ],
        [
            ["SAMPLE DATE & TIME", "12/06/2025 06:50\n:", "AGE\n: 58 Y/F 25/09/1966"],
            ["REPORT DATE & TIME\nPATIENT", "12/06/2025 16:37\n:\n:\nMRS. S N MANEL", "AHH2009957 / AHH2011800"],
            ["REFERRED BY\nSAMPLE TYPE", ":\n:\nPlasma", ""],
            ["TEST", "", "RESULT\nFLAG\nREFERENCE VALUE"],
            ["FASTING\nLASMA GLUCOSE", "(FBS)", "102.9\nmg/d\n0.\n-\n99."]
        ]
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


def test_fbs_normalization():
    """Test FBS normalization."""
    print("=" * 80)
    print("FASTING PLASMA GLUCOSE (FBS) NORMALIZATION TEST")
    print("=" * 80)
    print()
    
    print("INPUT DATA:")
    print("-" * 80)
    print(f"Number of tables: {len(FBS_SAMPLE['tables'])}")
    print()
    
    # Run normalization
    print("RUNNING NORMALIZATION...")
    print("-" * 80)
    try:
        result = normalize_report(FBS_SAMPLE)
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
        assert report.get('type') == "Fasting Plasma Glucose", "Wrong report type!"
        
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
        
        assert report.get('sample_type') == "Plasma", "Wrong sample type!"
        
        # Check biomarker
        biomarkers = result.get("biomarkers", [])
        print(f"✓ Number of biomarkers: {len(biomarkers)}")
        
        assert len(biomarkers) == 1, f"Expected 1 biomarker, got {len(biomarkers)}!"
        
        print()
        print("BIOMARKER EXTRACTED:")
        print("-" * 80)
        
        bio = biomarkers[0]
        name = bio.get('name')
        value = bio.get('value')
        unit = bio.get('unit')
        flag = bio.get('flag')
        ref_range = bio.get('ref_range')
        
        flag_str = f", Flag: {flag}" if flag else ""
        ref_str = f", Ref: {ref_range}" if ref_range else ""
        
        print(f"  • {name}: {value} {unit}{flag_str}{ref_str}")
        
        # Validate FBS specific checks
        assert name == "Fasting Plasma Glucose", f"Wrong biomarker name: {name}!"
        assert value == 102.9, f"Wrong value: {value}!"
        assert unit == "mg/dL", f"Wrong unit: {unit}!"
        
        # Value is 102.9, ref range should be [70.0, 99.0], so flag should be "High"
        assert flag == "High", f"Expected flag 'High', got {flag}!"
        assert ref_range == [70.0, 99.0], f"Wrong ref range: {ref_range}!"
        
        print()
        print("FLAG LOGIC VALIDATION:")
        print("-" * 80)
        print(f"  Value: {value} mg/dL")
        print(f"  Reference range: {ref_range[0]} - {ref_range[1]} mg/dL")
        print(f"  {value} > {ref_range[1]} → Flag: '{flag}' ✓")
        print()
        print("  Clinical interpretation:")
        print("    70-99 mg/dL: Normal")
        print("    100-125 mg/dL: Prediabetes (HIGH)")
        print("    ≥126 mg/dL: Diabetes (HIGH)")
        
        # Save output
        with open("tests/fbs_normalized_output.json", "w") as f:
            f.write(output)
        
        print()
        print("=" * 80)
        print("TEST COMPLETED SUCCESSFULLY ✓")
        print("Output saved to tests/fbs_normalized_output.json")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"✗ ERROR during normalization: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_fbs_normalization()
