# Patient Schema Update - Authentication & User Management

## 🎯 Overview

The patient model has been updated from a medical records system to a **user authentication and account management system**.

---

## 📊 Database Schema Changes

### Old Schema (Medical Records):
```sql
create table patients (
  id uuid primary key default gen_random_uuid(),
  nic text unique not null,
  name text,
  age_years int,
  gender text,
  created_at timestamptz default now()
);
```

### New Schema (User Authentication):
```sql
create table patients (
  id uuid primary key default gen_random_uuid(),
  full_name text not null,
  email text unique not null,
  phone text unique,
  password_hash text not null,
  nic text unique,
  created_at timestamptz default now()
);
```

---

## 🔧 What Changed

### ❌ Removed Fields:
- `age_years` (int) - Medical demographic data
- `gender` (text) - Medical demographic data
- `name` → Renamed to `full_name`

### ✅ Added Fields:
- `full_name` (text, not null) - User's complete name
- `email` (text, unique, not null) - Primary login identifier
- `phone` (text, unique, optional) - Contact number
- `password_hash` (text, not null) - Encrypted password

### 🔄 Modified Fields:
- `nic` - Now **optional** (was required)

---

## 📁 Updated Files

### 1. **app/schemas/patient.py** ✅

Added new schemas:

#### `PatientCreate` - Registration
```python
class PatientCreate(BaseModel):
    full_name: str          # Required, 1-255 chars
    email: EmailStr         # Required, valid email, unique
    phone: Optional[str]    # Optional, phone format validation
    password: str           # Required, min 8 chars
    nic: Optional[str]      # Optional
```

#### `PatientLogin` - Authentication (NEW)
```python
class PatientLogin(BaseModel):
    email: EmailStr
    password: str
```

#### `PatientPasswordUpdate` - Password changes (NEW)
```python
class PatientPasswordUpdate(BaseModel):
    old_password: str
    new_password: str  # Min 8 chars
```

#### `PatientUpdate` - Profile updates
```python
class PatientUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    nic: Optional[str]
    # Note: password excluded, use PatientPasswordUpdate
```

#### `PatientOut` - Response
```python
class PatientOut(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    nic: Optional[str]
    created_at: datetime
    # Note: password_hash excluded for security
```

---

### 2. **app/services/patientService.py** ✅

#### New Functions:
- `authenticate_patient(login)` - Login with email/password

#### Updated Functions:
- `create_patient(patient)` - Now hashes password, checks email uniqueness
- All read functions - Now exclude `password_hash` from responses
- `update_patient(...)` - Checks email uniqueness on updates

#### Security Features:
- ✅ Passwords are hashed using bcrypt before storage
- ✅ `password_hash` never returned in responses
- ✅ Email uniqueness validated before creation/update
- ✅ Login returns generic error message (security best practice)

---

### 3. **app/utils/auth.py** ✅ NEW FILE

Password security utilities:

```python
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    
def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Check password meets security requirements"""
```

---

### 4. **app/api/v1/endpoints/patient.py** ✅

#### New Endpoints:
```python
POST /api/v1/patients/register    # Create account (was POST /)
POST /api/v1/patients/login       # Authenticate user
GET  /api/v1/patients/email/{email}  # Lookup by email
```

#### Updated Endpoints:
```python
GET  /api/v1/patients/            # List all (excludes passwords)
GET  /api/v1/patients/nic/{nic}   # Get by NIC  
GET  /api/v1/patients/{id}        # Get by ID
PATCH /api/v1/patients/{id}       # Update profile
DELETE /api/v1/patients/{id}      # Delete account
```

---

### 5. **app/models/patient.py** ✅

Converted to dataclass (documentation only):

```python
@dataclass
class Patient:
    id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    password_hash: str
    nic: Optional[str]
    created_at: datetime
```

---

### 6. **requirements.txt** ✅

Added dependencies:
```
bcrypt==4.2.2           # Password hashing
email-validator==2.2.0  # Email validation for Pydantic
```

---

## 🔐 Security Features

### Password Handling:
1. ✅ **Hashing**: Passwords hashed with bcrypt before storage
2. ✅ **Never exposed**: `password_hash` excluded from all API responses
3. ✅ **Validation**: Minimum 8 characters required
4. ✅ **Secure login**: Generic error messages prevent user enumeration

### Email Security:
1. ✅ **Uniqueness enforced**: Database constraint + application check
2. ✅ **Format validation**: Pydantic EmailStr validator
3. ✅ **Used as login ID**: Primary authentication identifier

### Phone Validation:
1. ✅ **Format validation**: Regex pattern for international numbers
2. ✅ **Optional but unique**: If provided, must be unique

---

## 🚀 API Examples

### 1. Register a New Patient
```http
POST /api/v1/patients/register
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "password": "SecurePass123",
  "nic": "199512345678"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "nic": "199512345678",
    "created_at": "2026-02-07T13:20:00Z"
  }
}
```

---

### 2. Login
```http
POST /api/v1/patients/login
Content-Type: application/json

{
  "email": "john.doe@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "nic": "199512345678",
    "created_at": "2026-02-07T13:20:00Z"
  }
}
```

**Failed Login (401):**
```json
{
  "detail": "Invalid email or password"
}
```

---

### 3. Get Patient by Email
```http
GET /api/v1/patients/email/john.doe@example.com
```

---

### 4. Update Profile
```http
PATCH /api/v1/patients/{patient_id}
Content-Type: application/json

{
  "full_name": "John Smith",
  "phone": "+9876543210"
}
```

---

## 📝 Installation Steps

### 1. Install New Dependencies
```bash
pip install bcrypt==4.2.2 email-validator==2.2.0
```

Or install all:
```bash
pip install -r requirements.txt
```

### 2. Update Supabase Schema
Run this in Supabase SQL Editor:
```sql
-- Drop old table (WARNING: This deletes all data!)
DROP TABLE IF EXISTS patients;

-- Create new table
CREATE TABLE patients (
  id uuid primary key default gen_random_uuid(),
  full_name text not null,
  email text unique not null,
  phone text unique,
  password_hash text not null,
  nic text unique,
  created_at timestamptz default now()
);

-- Create indexes for performance
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_patients_phone ON patients(phone);
CREATE INDEX idx_patients_nic ON patients(nic);
```

### 3. Restart Server
The FastAPI server will auto-reload, but to be safe:
```bash
# Stop current server (Ctrl+C)
# Start again
uvicorn app.main:app --reload --port 8000
```

---

## ✅ Testing

### Test Registration:
```bash
curl -X POST "http://localhost:8000/api/v1/patients/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123",
    "phone": "+1234567890"
  }'
```

### Test Login:
```bash
curl -X POST "http://localhost:8000/api/v1/patients/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

---

## 🎯 Key Differences Summary

| Aspect | Old (Medical) | New (Authentication) |
|--------|---------------|---------------------|
| **Purpose** | Medical records | User accounts |
| **Primary ID** | NIC (required) | Email (required) |
| **Authentication** | None | Email + Password |
| **Data Fields** | age, gender | email, phone, password |
| **Security** | None | Bcrypt password hashing |
| **Endpoints** | POST / (create) | POST /register, /login |

---

## 🔒 Security Best Practices Implemented

1. ✅ Passwords hashed with bcrypt (industry standard)
2. ✅ Password min length: 8 characters
3. ✅ Passwords never logged or returned in responses
4. ✅ Generic error messages on failed login
5. ✅ Email uniqueness enforced at DB + app level
6. ✅ Input validation (email format, phone format)
7. ✅ Optional fields handled properly (phone, nic)

---

## 📊 Migration Checklist

- [x] Update database schema in Supabase
- [x] Update Pydantic schemas
- [x] Create password hashing utilities
- [x] Update service layer
- [x] Update API endpoints
- [x] Add new dependencies
- [x] Test registration
- [x] Test login
- [x] Test profile updates

---

## 🆘 Troubleshooting

### Error: "Email already registered"
- Check if email exists in database
- Use different email or delete existing record

### Error: "Invalid email or password"
- Verify email is correct
- Check password (case-sensitive)
- Ensure account exists (register first)

### Error: EmailStr not found
- Install: `pip install email-validator`

### Error: bcrypt not found
- Install: `pip install bcrypt`

---

**Update Date:** 2026-02-07  
**Backend Version:** 1.0.0  
**Supabase Table:** patients (v2 - Authentication)
