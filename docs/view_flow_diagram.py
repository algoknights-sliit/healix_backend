"""
Quick Reference - Patient CRUD Files and Their Roles
"""

print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    PATIENT CRUD - FILE STRUCTURE & FLOW                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  1. CLIENT REQUEST                                                             ║
║     POST http://localhost:8000/api/v1/patients/                                ║
║     Body: {"nic": "...", "name": "...", "age_years": 29, "gender": "..."}     ║
║                                    ↓                                           ║
║  ────────────────────────────────────────────────────────────────────────────  ║
║                                                                                ║
║  2. app/main.py                                   [ENTRY POINT]                ║
║     • Creates FastAPI app                                                      ║
║     • Registers patient router with prefix "/api/v1"                           ║
║     • Key Line: app.include_router(patient.router, prefix="/api/v1")          ║
║                                    ↓                                           ║
║  ────────────────────────────────────────────────────────────────────────────  ║
║                                                                                ║
║  3. app/api/v1/endpoints/patient.py               [API ENDPOINT]               ║
║     • Defines routes (@router.post("/"))                                       ║
║     • Handles HTTP requests/responses                                          ║
║     • Calls service layer functions                                            ║
║     • Returns HTTP status codes (201, 400, 404)                                ║
║                                    ↓                                           ║
║  ────────────────────────────────────────────────────────────────────────────  ║
║                                                                                ║
║  4. app/schemas/patient.py                        [DATA VALIDATION]            ║
║     • PatientCreate: Validates incoming data                                   ║
║       - nic: str (required)                                                    ║
║       - name: str (required)                                                   ║
║       - age_years: int (0-150)                                                 ║
║       - gender: str (required)                                                 ║
║     • PatientOut: Formats response data                                        ║
║     • Returns 422 if validation fails                                          ║
║                                    ↓                                           ║
║  ────────────────────────────────────────────────────────────────────────────  ║
║                                                                                ║
║  5. app/services/patientService.py                [BUSINESS LOGIC]             ║
║     • create_patient(patient) - Insert new record                              ║
║     • get_patient_by_id(id) - Fetch by UUID                                    ║
║     • get_patient_by_nic(nic) - Fetch by NIC                                   ║
║     • list_patients(skip, limit) - Fetch all with pagination                   ║
║     • update_patient(id, updates) - Update record                              ║
║     • delete_patient(id) - Delete record                                       ║
║     • Returns: {"success": bool, "data": {...}, "error": "..."}               ║
║                                    ↓                                           ║
║  ────────────────────────────────────────────────────────────────────────────  ║
║                                                                                ║
║  6. app/db/supabase.py                            [DATABASE CONNECTION]        ║
║     • Loads .env credentials                                                   ║
║     • Creates Supabase client                                                  ║
║     • Exports: supabase (Client instance)                                      ║
║                                    ↓                                           ║
║  ────────────────────────────────────────────────────────────────────────────  ║
║                                                                                ║
║  7. SUPABASE DATABASE (Cloud)                     [DATA STORAGE]               ║
║     • PostgreSQL database                                                      ║
║     • Table: patients                                                          ║
║     • Auto-generates: id (UUID), created_at (timestamp)                        ║
║     • Enforces: NIC uniqueness constraint                                      ║
║                                    ↓                                           ║
║  ────────────────────────────────────────────────────────────────────────────  ║
║                                                                                ║
║  8. RESPONSE                                                                   ║
║     Status: 201 Created                                                        ║
║     Body: {                                                                    ║
║       "success": true,                                                         ║
║       "data": {                                                                ║
║         "id": "uuid-here",                                                     ║
║         "nic": "199512345678",                                                 ║
║         "name": "John Doe",                                                    ║
║         "age_years": 29,                                                       ║
║         "gender": "Male",                                                      ║
║         "created_at": "2026-02-07T..."                                         ║
║       }                                                                        ║
║     }                                                                          ║
║                                                                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                         ALL CRUD ENDPOINTS                                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  POST   /api/v1/patients/              Create new patient                     ║
║  GET    /api/v1/patients/              List all patients (paginated)          ║
║  GET    /api/v1/patients/nic/{nic}     Get patient by NIC                     ║
║  GET    /api/v1/patients/{id}          Get patient by UUID                    ║
║  PATCH  /api/v1/patients/{id}          Update patient (partial)               ║
║  DELETE /api/v1/patients/{id}          Delete patient                         ║
║                                                                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                         CONFIGURATION FILES                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  .env                                   Environment variables                  ║
║    • SUPABASE_URL=https://hbrqbkgaznqcnkkrxiqd.supabase.co                    ║
║    • SUPABASE_SERVICE_ROLE_KEY=eyJhbG...                                      ║
║                                                                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                         KEY CONCEPTS                                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  LAYERED ARCHITECTURE:                                                         ║
║    ┌─────────────┐                                                             ║
║    │  API Layer  │  (endpoints/) - HTTP requests/responses                    ║
║    └──────┬──────┘                                                             ║
║           ↓                                                                    ║
║    ┌─────────────┐                                                             ║
║    │ Schema Layer│  (schemas/) - Data validation                               ║
║    └──────┬──────┘                                                             ║
║           ↓                                                                    ║
║    ┌─────────────┐                                                             ║
║    │Service Layer│  (services/) - Business logic                               ║
║    └──────┬──────┘                                                             ║
║           ↓                                                                    ║
║    ┌─────────────┐                                                             ║
║    │  DB Layer   │  (db/) - Database connection                                ║
║    └──────┬──────┘                                                             ║
║           ↓                                                                    ║
║    ┌─────────────┐                                                             ║
║    │  Supabase   │  PostgreSQL database (Cloud)                                ║
║    └─────────────┘                                                             ║
║                                                                                ║
║  AUTO-GENERATED FIELDS:                                                        ║
║    • id: UUID (generated by Supabase)                                          ║
║    • created_at: timestamp (set by Supabase)                                   ║
║    → You only need to send: nic, name, age_years, gender                      ║
║                                                                                ║
║  ERROR HANDLING:                                                               ║
║    • 422 Unprocessable Entity - Validation failed (missing/invalid fields)     ║
║    • 400 Bad Request - Database error (e.g., duplicate NIC)                   ║
║    • 404 Not Found - Patient doesn't exist                                     ║
║    • 500 Internal Server Error - Unexpected error                              ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Full detailed documentation: DATABASE_UPDATE_FLOW.md
""")
