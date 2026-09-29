# Doctor Patient Management API

A production-style backend application built using FastAPI for managing Doctors, Patients, and Appointments.

The project includes authentication, role-based authorization, database persistence, validation, audit tracking, API security, performance optimization, automated testing, and Swagger documentation.

## Features

* User registration and login
* JWT authentication
* Role-based authorization
* Admin and Doctor roles
* Doctor management
* Patient management
* Doctor-Patient assignment
* Appointment management
* SQLite database
* SQLAlchemy ORM
* Data validation
* Database constraints
* Pagination
* Query optimization
* Database indexes
* Audit fields
* Request ID tracking
* Request processing time tracking
* CORS configuration
* Security response headers
* Global exception handling
* Validation error handling
* Automated API testing
* Swagger/OpenAPI documentation
* Alembic database migrations

## Tech Stack

* Python 3.14
* FastAPI
* Pydantic
* SQLAlchemy
* SQLite
* JWT
* Passlib
* bcrypt
* Alembic
* Pytest
* Uvicorn

## Project Structure

```text
doctor_patient_api/
│
├── alembic/
│   └── versions/
│       ├── 7f8aa5f14746_initial_migration.py
│       └── add_audit_fields.py
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   └── doctor_patient_router.py
│   │
│   ├── routes/
│   │   ├── doctors.py
│   │   ├── patients.py
│   │   └── appointments.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── appointment.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── appointment.py
│   │
│   ├── services/
│   │   ├── doctor_service.py
│   │   ├── patient_service.py
│   │   └── appointment_service.py
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

## Authentication

The API uses JWT-based authentication.

### Register

```text
POST /api/v1/auth/register
```

Creates a new user account.

Supported roles:

```text
admin
doctor
```

### Login

```text
POST /api/v1/auth/login
```

Returns a JWT access token.

The token can be used in Swagger through the `Authorize` button.

## Authorization

The application provides role-based access control.

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
* Assign patients to doctors
* Create appointments
* View appointments
* Update appointments
* Delete appointments

### Doctor

Doctor users can:

* Login
* View their assigned patients
* View appointments related to their work

Doctors cannot perform admin-only operations such as deleting doctors or patients.

Unauthorized operations return appropriate HTTP status codes.

## Doctor API

Base path:

```text
/api/v1/doctors
```

Main operations:

```text
POST   /api/v1/doctors/
GET    /api/v1/doctors/
GET    /api/v1/doctors/{doctor_id}
PUT    /api/v1/doctors/{doctor_id}
DELETE /api/v1/doctors/{doctor_id}
```

## Patient API

Base path:

```text
/api/v1/patients
```

Main operations:

```text
POST   /api/v1/patients/
GET    /api/v1/patients/
GET    /api/v1/patients/{patient_id}
PUT    /api/v1/patients/{patient_id}
DELETE /api/v1/patients/{patient_id}
```

## Doctor-Patient API

The Doctor-Patient module manages the relationship between doctors and patients.

Example:

```text
GET  /api/v1/doctor-patient/{doctor_id}/patients
POST /api/v1/doctor-patient/{patient_id}/assign/{doctor_id}
```

This allows administrators to assign patients to doctors and allows doctors to access their assigned patients according to authorization rules.

## Appointment API

Base path:

```text
/api/v1/appointments
```

Main operations:

```text
POST   /api/v1/appointments/
GET    /api/v1/appointments/
GET    /api/v1/appointments/{appointment_id}
PUT    /api/v1/appointments/{appointment_id}
DELETE /api/v1/appointments/{appointment_id}
```

Appointments can also be retrieved by doctor or patient.

```text
GET /api/v1/appointments/doctors/{doctor_id}/appointments

GET /api/v1/appointments/patients/{patient_id}/appointments
```

## Database

The project uses SQLite with SQLAlchemy ORM.

Database file:

```text
doctor_patient.db
```

Main tables:

```text
users
doctors
patients
appointments
```

Foreign-key relationships are used between appointments, doctors, and patients.

Doctor email addresses are unique.

Database indexes are used on frequently queried fields.

## Audit Tracking

Doctors, Patients, and Appointments contain audit information such as:

```text
created_at
updated_at
created_by
updated_by
```

This provides basic tracking of when records were created or modified and which user performed the operation.

## Pagination

List APIs support pagination.

Example:

```text
GET /api/v1/doctors/?page=1&limit=10
```

Pagination validation prevents invalid page and limit values.

## Performance Optimization

The project includes:

* Database indexes
* Pagination
* Efficient SQLAlchemy queries
* Avoidance of unnecessary repeated database queries
* Response processing-time tracking

The API returns an `X-Process-Time` response header.

## API Security

The application includes:

* JWT authentication
* Role-based authorization
* Password hashing
* CORS configuration
* Request validation
* Global exception handling
* Security response headers
* Request ID tracking
* Protected endpoints

Security-related response headers include:

```text
X-Content-Type-Options
X-Frame-Options
Referrer-Policy
```

## Request Tracking

Each request receives a unique request ID.

Response header:

```text
X-Request-ID
```

The request ID is also included in logs and internal error responses.

## Health Check

The application provides a health-check endpoint:

```text
GET /health
```

Example response:

```json
{
    "status": "healthy"
}
```

## Swagger Documentation

FastAPI automatically provides interactive API documentation.

After starting the application, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger documentation includes:

* Endpoint summaries
* Endpoint descriptions
* Request parameters
* Response descriptions
* Request/response examples
* Authentication documentation

## Running the Project

### 1. Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run database migrations

```powershell
alembic upgrade head
```

### 4. Start the FastAPI application

```powershell
uvicorn app.main:app --reload
```

The application will run at:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Testing

The project uses Pytest for automated API testing.

Run:

```powershell
pytest
```

Current test result:

```text
30 passed
```

The test suite covers:

* Home endpoint
* Health endpoint
* Login
* Invalid login
* Authentication
* Authorization
* Doctor APIs
* Patient APIs
* Appointment APIs
* Validation
* Pagination
* Duplicate data
* Invalid IDs
* Role restrictions
* Error handling

## Database Migrations

Alembic is used for database migrations.

Check the current migration:

```powershell
alembic current
```

Apply migrations:

```powershell
alembic upgrade head
```

Create a new migration:

```powershell
alembic revision --autogenerate -m "migration message"
```

## Environment Variables

Sensitive configuration should be stored in a `.env` file and should not be committed to GitHub.

The `.env` file is excluded through `.gitignore`.

## API Base URL

```text
http://127.0.0.1:8000/api/v1
```

## Project Status

```text
Levels 11 - 18: Completed
Automated Tests: 30 passed
Swagger Documentation: Completed
Authentication: Completed
Authorization: Completed
Appointments: Completed
Audit Tracking: Completed
API Hardening: Completed
Performance Optimization: Completed


