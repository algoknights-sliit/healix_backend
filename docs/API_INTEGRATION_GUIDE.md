# API Integration Guide - Getting Normalized JSON Output

## Overview

You now have a complete API to retrieve normalized medical reports! The system automatically processes uploaded PDFs and provides clean, structured JSON data ready for use in your application.

## Quick Start

### 1. Your API is Running ✓

Server: `http://localhost:8080`  
Swagger Docs: `http://localhost:8080/docs`

### 2. Available Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/ocr/upload` | Upload PDF report |
| GET | `/api/v1/ocr/report/{nic}/{file_id}/normalized` | **Get normalized JSON** |
| GET | `/api/v1/ocr/report/{nic}/{file_id}/raw` | Get raw OCR data |
| GET | `/api/v1/ocr/reports/{nic}` | List all reports |

## How to Get Normalized JSON Output

### Step-by-Step Workflow

#### 1. Upload a Medical Report

```javascript
// Frontend example (React/Vue/Angular)
const uploadReport = async (pdfFile, patientNIC) => {
  const formData = new FormData();
  formData.append('nic', patientNIC);
  formData.append('file', pdfFile);

  const response = await fetch('http://localhost:8080/api/v1/ocr/upload', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();
  return result.file_id;  // Save this for later retrieval
};

// Usage
const fileId = await uploadReport(selectedFile, '123456789V');
console.log('Uploaded! File ID:', fileId);
```

#### 2. Wait for Processing (Background Task)

The normalization happens automatically in the background. Typically takes 5-10 seconds.

```javascript
// Optional: Poll for completion
const waitForProcessing = (delay = 5000) => {
  return new Promise(resolve => setTimeout(resolve, delay));
};

await waitForProcessing(5000);  // Wait 5 seconds
```

#### 3. Retrieve the Normalized JSON

```javascript
const getNormalizedReport = async (nic, fileId) => {
  const url = `http://localhost:8080/api/v1/ocr/report/${nic}/${fileId}/normalized`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Report not found or still processing');
    }
    throw new Error('Failed to fetch report');
  }
  
  const result = await response.json();
  return result.data;  // This is your normalized medical data!
};

// Usage
const normalizedData = await getNormalizedReport('123456789V', fileId);
console.log('Patient:', normalizedData.patient);
console.log('Biomarkers:', normalizedData.biomarkers);
```

#### 4. Use the Normalized Data

```javascript
// Example: Display patient information
const displayPatient = (data) => {
  const { patient, report } = data;
  
  console.log('Patient Information:');
  console.log(`  Name: ${patient.name}`);
  console.log(`  Age: ${patient.age_years} years`);
  console.log(`  Gender: ${patient.gender}`);
  console.log(`  Service Ref: ${patient.service_ref_no}`);
  console.log(`  Sample Collected: ${report.sample_collected_at}`);
};

// Example: Process biomarkers
const processBiomarkers = (data) => {
  data.biomarkers.forEach(biomarker => {
    console.log(`${biomarker.name}: ${biomarker.value} ${biomarker.unit}`);
    
    // Check if within reference range
    if (biomarker.ref_range) {
      const [min, max] = biomarker.ref_range;
      const isNormal = biomarker.value >= min && biomarker.value <= max;
      const status = isNormal ? '✓ Normal' : '⚠ Abnormal';
      console.log(`  ${status} (Range: ${min}-${max})`);
    }
  });
};

// Example: Store in database
const saveToDB = async (data) => {
  // Your database logic here
  await db.collection('medical_reports').add({
    patient_id: data.patient.service_ref_no,
    report_type: data.report.type,
    report_date: data.report.sample_collected_at,
    biomarkers: data.biomarkers,
    created_at: new Date()
  });
};
```

## Complete Example Application

```javascript
// Complete workflow
class MedicalReportHandler {
  constructor(apiBaseUrl = 'http://localhost:8080/api/v1/ocr') {
    this.apiBaseUrl = apiBaseUrl;
  }

  async uploadAndProcess(pdfFile, patientNIC) {
    try {
      // Step 1: Upload
      console.log('Uploading report...');
      const fileId = await this.upload(pdfFile, patientNIC);
      console.log('✓ Uploaded! File ID:', fileId);

      // Step 2: Wait for processing
      console.log('⏳ Processing (waiting 8 seconds)...');
      await this.wait(8000);

      // Step 3: Retrieve normalized data
      console.log('Fetching normalized data...');
      const normalizedData = await this.getNormalized(patientNIC, fileId);
      console.log('✓ Received normalized data!');

      // Step 4: Return the data
      return {
        fileId,
        data: normalizedData
      };

    } catch (error) {
      console.error('Error:', error.message);
      throw error;
    }
  }

  async upload(pdfFile, nic) {
    const formData = new FormData();
    formData.append('nic', nic);
    formData.append('file', pdfFile);

    const response = await fetch(`${this.apiBaseUrl}/upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error('Upload failed');
    
    const result = await response.json();
    return result.file_id;
  }

  async getNormalized(nic, fileId) {
    const response = await fetch(
      `${this.apiBaseUrl}/report/${nic}/${fileId}/normalized`
    );

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Report not ready yet, try again in a few seconds');
      }
      throw new Error('Failed to fetch report');
    }

    const result = await response.json();
    return result.data;
  }

  async listReports(nic) {
    const response = await fetch(`${this.apiBaseUrl}/reports/${nic}`);
    if (!response.ok) throw new Error('Failed to list reports');
    
    const result = await response.json();
    return result.reports;
  }

  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Usage
const handler = new MedicalReportHandler();

// In your upload handler
document.getElementById('uploadBtn').addEventListener('click', async () => {
  const fileInput = document.getElementById('pdfFile');
  const nicInput = document.getElementById('patientNIC');

  const result = await handler.uploadAndProcess(
    fileInput.files[0],
    nicInput.value
  );

  console.log('Normalized Data:', result.data);
  
  // Use the data in your app
  displayPatientInfo(result.data.patient);
  renderBiomarkers(result.data.biomarkers);
  saveToLocalStorage(result.fileId, result.data);
});
```

## Response Data Structure

```typescript
interface NormalizedReport {
  patient: {
    name: string | null;
    age_years: number | null;
    gender: "Male" | "Female" | null;
    ref_doctor: string | null;
    service_ref_no: string | null;
  };
  report: {
    type: string;
    sample_collected_at: string | null;  // ISO-8601 format
    printed_at: string | null;           // ISO-8601 format
  };
  biomarkers: Array<{
    name: string;
    value: number;
    unit: string;
    absolute: number | null;
    ref_range: [number, number] | null;
  }>;
}
```

## Error Handling

```javascript
const getReportWithRetry = async (nic, fileId, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const data = await getNormalizedReport(nic, fileId);
      return data;
    } catch (error) {
      if (error.message.includes('not found') && i < maxRetries - 1) {
        console.log(`Retry ${i + 1}/${maxRetries}...`);
        await new Promise(resolve => setTimeout(resolve, 3000));
        continue;
      }
      throw error;
    }
  }
};
```

## Testing with cURL

```bash
# 1. Upload a report
curl -X POST "http://localhost:8080/api/v1/ocr/upload" \
  -F "nic=123456789V" \
  -F "file=@sample_report.pdf"

# Response: { "file_id": "abc-123-def-456", ... }

# 2. Wait ~5 seconds, then get normalized data
curl "http://localhost:8080/api/v1/ocr/report/123456789V/abc-123-def-456/normalized"

# 3. List all reports for patient
curl "http://localhost:8080/api/v1/ocr/reports/123456789V"
```

## Integration with Frontend Frameworks

### React Example

```jsx
import { useState } from 'react';

function ReportUploader() {
  const [fileId, setFileId] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (file, nic) => {
    setLoading(true);
    
    // Upload
    const formData = new FormData();
    formData.append('nic', nic);
    formData.append('file', file);
    
    const uploadRes = await fetch('http://localhost:8080/api/v1/ocr/upload', {
      method: 'POST',
      body: formData
    });
    
    const { file_id } = await uploadRes.json();
    setFileId(file_id);
    
    // Wait and fetch
    await new Promise(r => setTimeout(r, 8000));
    
    const reportRes = await fetch(
      `http://localhost:8080/api/v1/ocr/report/${nic}/${file_id}/normalized`
    );
    
    const { data } = await reportRes.json();
    setReportData(data);
    setLoading(false);
  };

  return (
    <div>
      {loading && <p>Processing...</p>}
      {reportData && (
        <div>
          <h2>{reportData.patient.name}</h2>
          <p>Age: {reportData.patient.age_years}</p>
          {/* Render biomarkers table */}
        </div>
      )}
    </div>
  );
}
```

## What You Get

✅ **Patient Demographics** - Name, age, gender, references  
✅ **Report Metadata** - Type, collection date, print date  
✅ **Biomarkers** - 13 standardized biomarkers with values, units, and ranges  
✅ **Clean Data** - No OCR noise, normalized units, numeric values  
✅ **Database Ready** - ISO-8601 dates, structured JSON  
✅ **Trend Analysis Ready** - Consistent format for time-series analysis  

## Next Steps

1. ✅ **Test the API** - Visit http://localhost:8080/docs
2. ✅ **Integrate with Frontend** - Use the examples above
3. 📊 **Build Dashboard** - Display patient trends over time
4. 💾 **Store in Database** - Save normalized data for analysis
5. 📱 **Mobile App** - Use the same API endpoints

## Support

- 📄 See `docs/API_ENDPOINTS.md` for detailed API documentation
- 📄 See `docs/NORMALIZATION.md` for normalization details
- 🧪 Run `python tests/test_api.py` to verify API is working

Your backend is now complete and ready to serve normalized medical data! 🎉
