# Hospital Management API

A production-style Hospital Management Backend API built using **FastAPI, Python, SQLAlchemy, and SQLite**.

The application manages Doctors, Patients, Appointments, Billing, Payments, Authentication, Authorization, and Revenue Reports.

---

## 🚀 Features

* JWT Authentication
* Role-Based Authorization
* Admin and Doctor roles
* Doctor management
* Patient management
* Doctor-Patient assignment
* Appointment management
* Billing and Payment management
* Billing filters and pagination
* Revenue reports
* Transaction handling
* Database constraints
* Input validation
* Error handling
* Request ID tracking
* Response-time tracking
* Security headers
* CORS configuration
* Audit fields
* API documentation with Swagger
* Automated testing with Pytest
* Database migrations with Alembic

---

## 🛠️ Tech Stack

* **Python 3.9+**
* **FastAPI**
* **Pydantic**
* **SQLAlchemy**
* **SQLite**
* **JWT**
* **Passlib**
* **bcrypt**
* **Alembic**
* **Pytest**
* **Uvicorn**

---

## 📁 Project Structure

```text
doctor_patient_api/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   └── doctor_patient_router.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   └── billing.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   └── billing.py
│   │
│   ├── routes/
│   │   ├── doctors.py
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── billings.py
│   │   └── reports.py
│   │
│   ├── services/
│   │   ├── doctor_service.py
│   │   ├── patient_service.py
│   │   ├── appointment_service.py
│   │   └── billing_service.py
│   │
│   ├── auth.py
│   ├── database.py
│   ├── dependencies.py
│   ├── logging_config.py
│   └── main.py
│
├── tests/
│   └── test_api.py
│
├── create_admin.py
├── Dockerfile
├── alembic.ini
├── pytest.ini
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 🔐 Authentication

The API uses **JWT authentication**.

### Register

```text
POST /api/v1/auth/register
```

### Login

```text
POST /api/v1/auth/login
```

The login endpoint returns an access token.

Example:

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

The token can be used through Swagger's **Authorize** button.

---

# 👥 Authorization

The application supports two roles:

* `admin`
* `doctor`

### Admin

Admin users can:

* Create doctors
* View doctors
* Update doctors
* Delete doctors
* Create patients
* View patients
* Update patients
* Delete patients
* Manage doctor-patient assignments
* Manage appointments
* Manage billing
* View revenue reports

### Doctor

Doctors can:

* Login
* View their assigned patients
* View related appointments
* View billing records related to their patients

Doctors cannot:

* Delete doctors
* Delete patients
* Delete billing records
* Access admin-only operations

Unauthorized operations return:

```text
403 Forbidden
```

---

# 👨‍⚕️ Doctors

Doctor APIs include:

```text
POST   /api/v1/doctors/
GET    /api/v1/doctors/
GET    /api/v1/doctors/{doctor_id}
PUT    /api/v1/doctors/{doctor_id}
DELETE /api/v1/doctors/{doctor_id}
```

Doctor email is unique.

Inactive doctors cannot be used for new billing operations.

---

# 🧑‍🤝‍🧑 Patients

Patient APIs include:

```text
POST   /api/v1/patients/
GET    /api/v1/patients/
GET    /api/v1/patients/{patient_id}
PUT    /api/v1/patients/{patient_id}
DELETE /api/v1/patients/{patient_id}
```

Patients can be assigned to doctors.

---

# 🔗 Doctor-Patient Relationship

Doctors and patients can be connected using the doctor-patient APIs.

Example:

```text
GET /api/v1/doctor-patient/{doctor_id}/patients
```

Doctors can only access patients assigned to them.

---

# 📅 Appointments

Appointment APIs include:

```text
POST   /api/v1/appointments/
GET    /api/v1/appointments/
GET    /api/v1/appointments/{appointment_id}
PUT    /api/v1/appointments/{appointment_id}
DELETE /api/v1/appointments/{appointment_id}
```

An appointment contains:

* Doctor
* Patient
* Appointment date
* Status
* Audit information

Example appointment:

```json
{
  "doctor_id": 2,
  "patient_id": 1,
  "appointment_date": "2026-10-05T10:00:00",
  "status": "scheduled"
}
```

---

# 💰 Billing & Payments

The Billing module manages patient billing and payments.

## Billing Fields

* `id`
* `patient_id`
* `doctor_id`
* `appointment_id`
* `consultation_fee`
* `additional_charges`
* `total_amount`
* `payment_status`
* `payment_mode`
* `is_active`
* `created_at`
* `updated_at`

### Payment Status

Supported values:

```text
pending
paid
cancelled
```

### Payment Mode

Supported values:

```text
cash
card
upi
```

---

## Billing Flow

The billing process follows these rules:

```text
Patient
   ↓
Doctor
   ↓
Appointment (optional)
   ↓
Validate Doctor
   ↓
Validate Patient
   ↓
Validate Appointment
   ↓
Calculate Total Amount
   ↓
Create Billing
   ↓
Update Appointment Status
   ↓
Commit Transaction
```

The total amount is calculated automatically:

```text
total_amount = consultation_fee + additional_charges
```

Example:

```text
Consultation Fee = 800
Additional Charges = 100

Total Amount = 900
```

---

## Billing APIs

```text
POST   /api/v1/billings/
GET    /api/v1/billings/
GET    /api/v1/billings/{billing_id}
PUT    /api/v1/billings/{billing_id}
PATCH  /api/v1/billings/{billing_id}
DELETE /api/v1/billings/{billing_id}
```

Additional APIs:

```text
GET /api/v1/billings/patients/{patient_id}/billings
GET /api/v1/billings/doctors/{doctor_id}/billings
```

---

## Billing Validation

The API validates:

* Patient must exist
* Doctor must exist
* Doctor must be active
* Appointment must exist if provided
* Appointment must belong to the same doctor
* Appointment must belong to the same patient
* Cancelled appointments cannot be billed
* Duplicate billing for the same appointment is prevented
* Payment status must be valid
* Payment mode must be valid
* Fees cannot be negative

---

## Soft Delete

Billing records use soft delete.

Instead of permanently deleting a billing record:

```text
is_active = false
```

Inactive billing records are excluded from normal billing list results.

---

# 📊 Billing Filters & Pagination

Billing records support filtering by:

```text
payment_status
doctor_id
patient_id
from_date
to_date
```

Pagination is supported using:

```text
page
limit
```

Example:

```text
GET /api/v1/billings/?doctor_id=2&page=1&limit=10
```

Example date filter:

```text
GET /api/v1/billings/?from_date=2026-09-30T00:00:00&to_date=2026-09-30T23:59:59
```

---

# 📈 Revenue Reports

Revenue reports include only:

```text
payment_status = paid
```

Revenue can be filtered by:

* Doctor
* Start date
* End date

Endpoint:

```text
GET /api/v1/reports/revenue
```

Example:

```text
GET /api/v1/reports/revenue?doctor_id=2&from=2026-09-01&to=2026-09-30
```

The response provides:

* Total revenue
* Revenue per doctor
* Revenue per day

Example:

```json
{
  "total_revenue": 1800,
  "doctor_revenue": [
    {
      "doctor_id": 2,
      "doctor_name": "Dr. Kumar",
      "revenue": 1800
    }
  ],
  "daily_revenue": [
    {
      "date": "2026-09-30",
      "revenue": 1800
    }
  ]
}
```

Revenue reports are available to administrators.

---

# 🔄 Transactions & Consistency

Billing creation uses a database transaction.

When a billing is created for an appointment:

```text
Create Billing
      +
Update Appointment Status
      ↓
Single Database Commit
```

If an error occurs:

```text
Database Rollback
```

This prevents partial updates.

For example, when an invalid doctor is supplied, the billing is rejected and the appointment is not incorrectly changed.

---

# 🗄️ Database Constraints

The Billing table contains database-level constraints.

### Fee constraints

```text
consultation_fee >= 0
additional_charges >= 0
total_amount >= 0
```

### Payment constraints

```text
payment_status:
pending / paid / cancelled

payment_mode:
cash / card / upi
```

### Unique constraint

Only one billing can exist for an appointment.

```text
appointment_id → UNIQUE
```

### Foreign keys

```text
patient_id → patients.id
doctor_id → doctors.id
appointment_id → appointments.id
```

---

# 📝 Audit & Tracking

Doctors, Patients, and Appointments contain audit fields:

```text
created_at
updated_at
created_by
updated_by
```

These fields help track when records were created or updated.

---

# 🔍 Validation & Error Handling

The API provides validation and error handling for:

* Invalid IDs
* Missing records
* Invalid data types
* Invalid pagination
* Invalid payment status
* Invalid payment mode
* Duplicate records
* Invalid appointment relationships
* Unauthorized access

Validation errors return:

```text
422 Unprocessable Entity
```

Unauthorized requests return:

```text
401 Unauthorized
```

Forbidden operations return:

```text
403 Forbidden
```

Not-found resources return:

```text
404 Not Found
```

---

# 🔒 Security

The application includes:

* JWT authentication
* Password hashing
* Role-based authorization
* CORS configuration
* Security response headers
* Request ID tracking
* Input validation
* Global exception handling

Response headers include security headers such as:

```text
X-Content-Type-Options
X-Frame-Options
Referrer-Policy
X-Request-ID
X-Process-Time
```

---

# 🆔 Request Tracking

Every request receives a unique request ID.

Example:

```text
X-Request-ID: <unique-request-id>
```

The ID is also available through the request state for logging and debugging.

---

# ❤️ Health Check

Health endpoint:

```text
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

---

# 📚 Swagger Documentation

After starting the application, open:

```text
http://127.0.0.1:8000/docs
```

Swagger provides interactive documentation for all API endpoints.

The API groups are organized as:

```text
Authentication
Doctors
Patients
Doctor-Patient
Appointments
Billings
Reports
default
```

---

# ⚙️ Installation

Clone the repository and open the project folder.

Create a virtual environment:

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# ▶️ Running the Application

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

Application:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

# 🗃️ Database Migrations

The project uses Alembic for database migrations.

Check the current migration:

```powershell
alembic current
```

Upgrade database:

```powershell
alembic upgrade head
```

Create a new migration:

```powershell
alembic revision --autogenerate -m "migration message"
```

---

# 🧪 Testing

The project uses Pytest.

Run:

```powershell
pytest -v
```

Current test result:

```text
30 passed
```

The tests cover authentication, authorization, validation, doctors, patients, appointments, billing-related behavior, and error handling.

---

# 📦 Requirements

Dependencies are listed in:

```text
requirements.txt
```

Install them using:

```powershell
pip install -r requirements.txt
```

---

# 📸 API Testing

Swagger/Postman can be used to test:

* Authentication
* Doctors
* Patients
* Doctor-Patient relationships
* Appointments
* Billing
* Billing filters
* Billing pagination
* Revenue reports

Screenshots of important API tests can be included with the project submission.

---

# 🔑 Environment Variables

Sensitive configuration should be stored in `.env`.

The `.env` file should **not** be uploaded to GitHub.

Example:

```text
SECRET_KEY=your-secret-key
```

Use `.gitignore` to exclude sensitive and local files.

---




# 📌 API Base URL

```text
http://127.0.0.1:8000/api/v1
```

---

# 📊 Project Status

The Hospital Management API includes:

```text
Authentication          ✅
Authorization           ✅
Doctors                 ✅
Patients                ✅
Doctor-Patient          ✅
Appointments            ✅
Audit & Tracking        ✅
Security & Reliability  ✅
Testing                 ✅
Documentation           ✅
Billing                 ✅
Payments                ✅
Billing Filters         ✅
Pagination              ✅
Revenue Reports         ✅
Transactions             ✅
Database Constraints    ✅
```

---

# 👨‍💻 Author

**Parthiban V.**

BE Computer Science and Engineering

Hospital Management Backend API using FastAPI
