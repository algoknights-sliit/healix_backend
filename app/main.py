
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import reports as ocr
from app.api.v1.endpoints import patient
from app.api.v1.endpoints import care_circle
from app.api.v1.endpoints import medication

app = FastAPI(
    title="Healix Backend API",
    description="AI-powered medical record system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(patient.router, prefix="/api/v1", tags=["Patients"])
app.include_router(care_circle.router, prefix="/api/v1", tags=["Care Circle"])
app.include_router(medication.router, prefix="/api/v1", tags=["Medications"])


