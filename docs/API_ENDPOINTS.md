# API Endpoints Documentation

## Base URL
```
http://localhost:8080/api/v1/ocr
```

## Endpoints

### 1. Upload Medical Report

Upload a PDF medical report for OCR processing and normalization.

**Endpoint:** `POST /upload`

**Parameters:**
- `nic` (form-data, string): Patient's National Identity Card number
- `file` (form-data, file): PDF file of the medical report

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8080/api/v1/ocr/upload" \
  -F "nic=123456789V" \
  -F "file=@/path/to/report.pdf"
```

**Example Request (JavaScript):**
```javascript
const formData = new FormData();
formData.append('nic', '123456789V');
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8080/api/v1/ocr/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
```

**Response (200 OK):**
```json
{
  "status": "uploaded",
  "message": "Report uploaded and processing started",
  "file_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 2. Get Normalized Report

Retrieve the normalized medical report JSON.

**Endpoint:** `GET /report/{nic}/{file_id}/normalized`

**Path Parameters:**
- `nic` (string): Patient's National Identity Card number
- `file_id` (string): File identifier returned from upload

**Example Request (cURL):**
```bash
curl -X GET "http://localhost:8080/api/v1/ocr/report/123456789V/a1b2c3d4-e5f6-7890-abcd-ef1234567890/normalized"
```

**Example Request (JavaScript):**
```javascript
const nic = '123456789V';
const fileId = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

const response = await fetch(
  `http://localhost:8080/api/v1/ocr/report/${nic}/${fileId}/normalized`
);

const result = await response.json();
console.log(result.data);
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
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
      }
      // ... more biomarkers
    ]
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Normalized report not found. It may still be processing."
}
```

---

### 3. Get Raw OCR Data

Retrieve the raw OCR data (for debugging purposes).

**Endpoint:** `GET /report/{nic}/{file_id}/raw`

**Path Parameters:**
- `nic` (string): Patient's National Identity Card number
- `file_id` (string): File identifier returned from upload

**Example Request (cURL):**
```bash
curl -X GET "http://localhost:8080/api/v1/ocr/report/123456789V/a1b2c3d4-e5f6-7890-abcd-ef1234567890/raw"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "raw_text": "Full unstructured OCR text...",
    "tables": [
      [
        ["W.B.C.", "7970", "Per Cumm", "", "4000\n-\n11000"]
      ]
    ],
    "entities": [...],
    "page_count": 1
  }
}
```

---

### 4. List All Reports

List all processed reports for a patient.

**Endpoint:** `GET /reports/{nic}`

**Path Parameters:**
- `nic` (string): Patient's National Identity Card number

**Example Request (cURL):**
```bash
curl -X GET "http://localhost:8080/api/v1/ocr/reports/123456789V"
```

**Example Request (JavaScript):**
```javascript
const nic = '123456789V';

const response = await fetch(
  `http://localhost:8080/api/v1/ocr/reports/${nic}`
);

const result = await response.json();
console.log(result.reports);
```

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 2,
  "reports": [
    {
      "file_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "type": "normalized",
      "created": "2025-06-03T09:15:00.000000Z",
      "size_bytes": 2381
    },
    {
      "file_id": "b2c3d4e5-f6g7-8901-bcde-fg2345678901",
      "type": "normalized",
      "created": "2025-06-02T14:30:00.000000Z",
      "size_bytes": 2156
    }
  ]
}
```

---

## Complete Workflow Example

### Step 1: Upload a Report
```javascript
// Upload PDF
const formData = new FormData();
formData.append('nic', '123456789V');
formData.append('file', pdfFile);

const uploadResponse = await fetch('http://localhost:8080/api/v1/ocr/upload', {
  method: 'POST',
  body: formData
});

const { file_id } = await uploadResponse.json();
console.log('File uploaded:', file_id);
```

### Step 2: Wait for Processing
```javascript
// Wait a few seconds for background processing
await new Promise(resolve => setTimeout(resolve, 5000));
```

### Step 3: Retrieve Normalized Data
```javascript
// Get normalized report
const reportResponse = await fetch(
  `http://localhost:8080/api/v1/ocr/report/123456789V/${file_id}/normalized`
);

const { data } = await reportResponse.json();

// Access the normalized data
console.log('Patient:', data.patient);
console.log('Biomarkers:', data.biomarkers);
```

### Step 4: Use the Data
```javascript
// Example: Display patient info
const patientInfo = {
  name: data.patient.name,
  age: data.patient.age_years,
  gender: data.patient.gender
};

// Example: Process biomarkers
data.biomarkers.forEach(biomarker => {
  console.log(`${biomarker.name}: ${biomarker.value} ${biomarker.unit}`);
  
  // Check if value is within reference range
  if (biomarker.ref_range) {
    const [min, max] = biomarker.ref_range;
    const isNormal = biomarker.value >= min && biomarker.value <= max;
    console.log(`  Normal: ${isNormal}`);
  }
});
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- **200 OK**: Request successful
- **404 Not Found**: Report not found or not yet processed
- **422 Unprocessable Entity**: Invalid request parameters
- **500 Internal Server Error**: Server error

Always check the `status_code` and handle errors appropriately:

```javascript
try {
  const response = await fetch(url);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }
  
  const data = await response.json();
  // Process data
} catch (error) {
  console.error('Error:', error.message);
}
```

---

## Testing with Swagger UI

FastAPI automatically generates interactive API documentation:

**Swagger UI:** http://localhost:8080/docs

You can test all endpoints directly from the browser using the Swagger interface.

---

## Production Considerations

1. **CORS**: Update `allow_origins` in `main.py` to specify allowed frontend domains
2. **Authentication**: Add authentication middleware for production
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **File Size Limits**: Configure maximum file upload size
5. **Error Logging**: Set up proper error logging and monitoring
