"""
Simple test to verify normalization and save output.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.normalization_service import normalize_fbc_report


# Sample input
sample_input = {
    "raw_text": """PATIENT NAME: MR S KUMAR
REF.DOCTOR : OPD
AGE 62 Y/O M/O D
SERVICE REF.NO : CHL000735039
SAMPLE COLLECTED : 03/06/2025 09:10 AM
PRINTED DATE : 03/06/2025 06:43 PM
FULL BLOOD COUNT""",
    "tables": [
        [
            ["W.B.C.", "7970", "Per Cumm", "", "4000\n-\n11000"],
            ["NEUTROPHILS", "79", "응", "6296.3", ""],
            ["LYMPHOCYTES", "11", "응", "876.7", ""],
            ["EOSINOPHIL", "02", "응", "159.4", ""],
            ["MONOCYTES", "08", "응", "637.6", ""],
            ["BASOPHILS", "00", "응", "0", ""],
            ["HAEMOGLOBIN", "13.6", "g/dl", "", "11.0\n16.5"],
            ["P.C.V.", "39.2", "응", "", "36.0\n-\n48.0"],
            ["M.C.H.C.", "34.6", "g/dl", "", "33.0\n37.0"],
            ["R.B.C.", "4.29", "10^6 /UL", "", "4.0\n6.2"],
            ["M.C.H.", "31.7", "Pg", "", "27.0\n31.0"],
            ["M.C.V.", "91.5", "fL", "", "78.0\n100.0"],
            ["Platelet count", "224000", "Per Cu mm", "", "150000\n-\n400000"]
        ]
    ],
    "entities": [],
    "page_count": 1
}

print("Testing normalization...")
result = normalize_fbc_report(sample_input)

print("\nNormalized JSON Output:")
print("=" * 60)
output = json.dumps(result, indent=2)
print(output)

# Save to file
with open("tests/normalized_output.json", "w") as f:
    f.write(output)

print("\n" + "=" * 60)
print("✓ Test completed! Output saved to tests/normalized_output.json")
