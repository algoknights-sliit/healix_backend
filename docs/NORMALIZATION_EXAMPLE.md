# Normalization Example - Before and After

## Input (Raw OCR)

```json
{
  "raw_text": "PATIENT NAME: MR S KUMAR\nREF.DOCTOR : OPD\nAGE 62 Y/O M/O D\nSERVICE REF.NO : CHL000735039\nSAMPLE COLLECTED : 03/06/2025 09:10 AM\nPRINTED DATE : 03/06/2025 06:43 PM\nFULL BLOOD COUNT",
  "tables": [
    [
      ["W.B.C.", "7970", "Per Cumm", "", "4000\n-\n11000"],
      ["NEUTROPHILS", "79", "응", "6296.3", ""],
      ["HAEMOGLOBIN", "13.6", "g/dl", "", "11.0\n16.5"]
    ]
  ]
}
```

## Output (Normalized)

```json
{
  "patient": {
    "name": "MR S KUMAR",
    "age_years": 62,
    "gender": "Male",
    "ref_doctor": "OPD",
    "service_ref_no": "CHL000735039"
  },
  "report": {
    "type": "Full Blood Count",
    "sample_collected_at": "2025-06-03T09:10:00",
    "printed_at": "2025-06-03T18:43:00"
  },
  "biomarkers": [
    {
      "name": "WBC",
      "value": 7970.0,
      "unit": "per cu mm",
      "absolute": null,
      "ref_range": [4000.0, 11000.0]
    },
    {
      "name": "Neutrophils",
      "value": 79.0,
      "unit": "%",
      "absolute": 6296.3,
      "ref_range": null
    },
    {
      "name": "Hemoglobin",
      "value": 13.6,
      "unit": "g/dL",
      "absolute": null,
      "ref_range": [11.0, 16.5]
    }
  ]
}
```

## Key Transformations

| Aspect | Before | After |
|--------|--------|-------|
| **Patient Name** | Unstructured text | Extracted: "MR S KUMAR" |
| **Age** | "62 Y/O M/O D" | Numeric: 62 |
| **Gender** | "M" in text | Standardized: "Male" |
| **Dates** | "03/06/2025 09:10 AM" | ISO-8601: "2025-06-03T09:10:00" |
| **Biomarker Names** | "W.B.C.", "HAEMOGLOBIN" | Standardized: "WBC", "Hemoglobin" |
| **Units** | "Per Cumm", "g/dl", "응" | Normalized: "per cu mm", "g/dL", "%" |
| **Values** | Strings with noise | Clean floats: 7970.0, 79.0, 13.6 |
| **Reference Ranges** | "4000\n-\n11000" | Array: [4000.0, 11000.0] |
| **OCR Noise** | Korean char "응", "olo" | Removed completely |
