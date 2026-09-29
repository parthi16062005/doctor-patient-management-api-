from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Doctor Patient Management API is working!"
    }


def test_invalid_doctor():

    response = client.get(
        "/doctors/99999"
    )

    assert response.status_code in [401, 403, 404]


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_login():

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_login():

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "wrong_password"
        }
    )

    assert response.status_code == 401


def test_protected_endpoint_without_token():

    response = client.get(
        "/api/v1/doctors/"
    )

    assert response.status_code == 401


def test_admin_can_access_doctors():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/doctors/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_doctor_cannot_create_doctor():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "kumar@example.com",
            "password": "doctor123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/doctors/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Doctor",
            "specialization": "Testing",
            "email": "test.doctor@example.com"
        }
    )

    assert response.status_code == 403


def test_admin_can_create_patient():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/patients/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Patient",
            "age": 30,
            "phone": "9876543210",
            "doctor_id": 8
        }
    )

    assert response.status_code == 201


def test_admin_can_create_appointment():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/appointments/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "doctor_id": 8,
            "patient_id": 4,
            "appointment_date": "2030-06-20T10:00:00",
            "status": "completed"
        }
    )

    assert response.status_code == 201


def test_invalid_appointment_status():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/appointments/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "doctor_id": 8,
            "patient_id": 4,
            "appointment_date": "2030-07-15T10:00:00",
            "status": "invalid"
        }
    )

    assert response.status_code == 400


def test_doctor_cannot_create_appointment():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "kumar@example.com",
            "password": "doctor123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/appointments/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "doctor_id": 8,
            "patient_id": 4,
            "appointment_date": "2030-08-20T10:00:00",
            "status": "scheduled"
        }
    )

    assert response.status_code == 403


def test_get_appointment():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    list_response = client.get(
        "/api/v1/appointments/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert list_response.status_code == 200

    appointments = list_response.json()

    assert len(appointments) > 0

    appointment_id = appointments[0]["id"]

    response = client.get(
        f"/api/v1/appointments/{appointment_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == appointment_id


def test_get_all_appointments():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/appointments/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_invalid_patient():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/patients/99999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_duplicate_doctor_email():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    doctors_response = client.get(
        "/api/v1/doctors/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert doctors_response.status_code == 200

    doctors = doctors_response.json()["data"]

    assert len(doctors) > 0

    existing_email = doctors[0]["email"]

    response = client.post(
        "/api/v1/doctors/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Duplicate Test Doctor",
            "specialization": "Testing",
            "email": existing_email
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == "Doctor email already exists"


def test_invalid_pagination():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/doctors/?page=0",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"] == "Validation error"


def test_invalid_limit():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/doctors/?limit=101",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"] == "Validation error"


def test_invalid_patient_age():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/patients/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Invalid Age Patient",
            "age": 0,
            "phone": "9876543210",
            "doctor_id": 8
        }
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"] == "Validation error"


def test_invalid_appointment_doctor():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/appointments/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "doctor_id": 99999,
            "patient_id": 4,
            "appointment_date": "2030-09-20T10:00:00",
            "status": "scheduled"
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Doctor not found"


def test_invalid_appointment_patient():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/appointments/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "doctor_id": 8,
            "patient_id": 99999,
            "appointment_date": "2030-10-20T10:00:00",
            "status": "scheduled"
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Patient not found"


def test_doctor_cannot_delete_patient():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "kumar@example.com",
            "password": "doctor123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.delete(
        "/api/v1/patients/4",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_doctor_cannot_delete_doctor():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "kumar@example.com",
            "password": "doctor123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.delete(
        "/api/v1/doctors/2",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_admin_can_get_patient():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/patients/4",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_admin_can_get_doctor():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/doctors/2",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_invalid_token():

    response = client.get(
        "/api/v1/doctors/",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401


def test_doctor_can_login():

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "kumar@example.com",
            "password": "doctor123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_appointment_not_found():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/appointments/99999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_patient_appointments_invalid_patient():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/appointments/patients/99999/appointments",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_doctor_appointments_invalid_doctor():

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin1",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/appointments/doctors/99999/appointments",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404