# Biomarker Reference Range Fix

## 🐛 Issue Identified

The reference ranges (ref_min, ref_max) were not being stored correctly in the database.

### Root Cause

The normalization service (`normalization_service.py`) creates biomarkers with **`ref_range` as an array**:

```python
biomarker = {
    "name": "Hemoglobin",
    "value": 14.5,
    "unit": "g/dL",
    "ref_range": [12.0, 16.0]  # ← Array format [min, max]
}
```

But the database storage code was expecting **separate fields**:

```python
{
    "ref_min": 12.0,
    "ref_max": 16.0
}
```

## ✅ Solution

Updated `reportService.py` to handle **both formats**:

```python
# Handle ref_range array format from normalization service
if "ref_range" in bm and bm["ref_range"] is not None:
    # Normalization service returns [min, max]
    ref_range = bm["ref_range"]
    if isinstance(ref_range, list) and len(ref_range) >= 2:
        ref_min = safe_float(ref_range[0])
        ref_max = safe_float(ref_range[1])
else:
    # Handle separate ref_min/ref_max fields
    ref_min = safe_float(bm.get("ref_min"))
    ref_max = safe_float(bm.get("ref_max"))
```

### What It Does

1. **Checks for `ref_range` array** - If present, extracts min/max from array
2. **Validates array format** - Ensures it's a list with at least 2 elements
3. **Falls back to separate fields** - If `ref_range` not present, uses `ref_min`/`ref_max`
4. **Safe type conversion** - Uses `safe_float()` to handle invalid values gracefully

### Added Error Handling

The `safe_float()` function now handles:
- `None` values
- Empty strings (`""`)
- Invalid numeric formats
- Type errors

```python
def safe_float(value):
    """Safely convert value to float, return None if invalid"""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
```

## 🧪 Testing

Upload a new report and check the database:

```sql
-- Check biomarkers table
SELECT name, value, unit, ref_min, ref_max, flag
FROM biomarkers
ORDER BY created_at DESC
LIMIT 10;
```

You should now see:
- ✅ `ref_min` populated correctly
- ✅ `ref_max` populated correctly
- ✅ No errors during biomarker storage

## 📝 Example Data Flow

### 1. Normalization Service Output
```json
{
  "biomarkers": [
    {
      "name": "Hemoglobin",
      "value": 14.5,
      "unit": "g/dL",
      "ref_range": [12.0, 16.0]  ← Array
    }
  ]
}
```

### 2. After Parsing (reportService.py)
```python
BiomarkerCreate(
    name="Hemoglobin",
    value=14.5,
    unit="g/dL",
    ref_min=12.0,   ← Extracted from ref_range[0]
    ref_max=16.0    ← Extracted from ref_range[1]
)
```

### 3. Stored in Database
| name | value | unit | ref_min | ref_max |
|------|-------|------|---------|---------|
| Hemoglobin | 14.5 | g/dL | 12.0 | 16.0 |

## 🎯 Test Cases Handled

✅ **Array format**: `ref_range: [12.0, 16.0]`
✅ **String numbers in array**: `ref_range: ["12.0", "16.0"]`
✅ **Separate fields**: `ref_min: 12.0, ref_max: 16.0`
✅ **Missing values**: `ref_range: null` or `ref_min: null`
✅ **Empty strings**: `ref_range: ["", ""]`
✅ **Invalid formats**: Non-numeric values are converted to `None`

## 🔄 Next Steps

1. **Upload a new report** - Test with a fresh PDF
2. **Verify in Supabase** - Check biomarkers table
3. **API Testing** - Use `/report/id/{report_id}/complete` to see biomarkers

The fix is backward compatible, so it works with both old and new report formats! 🎉
