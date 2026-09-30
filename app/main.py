import time
import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.database import Base, engine

from app.api.auth import router as auth_router
from app.api.doctor_patient_router import router as doctor_patient_router

from app.routes.doctors import router as doctor_router
from app.routes.patients import router as patient_router
from app.routes.appointments import router as appointment_router
from app.routes.billings import router as billing_router
from app.routes.reports import router as reports_router

from app.logging_config import setup_logging


setup_logging()

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Doctor Patient Management API",
    description="Backend API for managing Doctors, Patients, Appointments and Billings",
    version="1.0.0"
)


allowed_origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def add_process_time_header(
    request: Request,
    call_next
):
    start_time = time.perf_counter()

    request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = str(
        round(process_time, 6)
    )

    response.headers["X-Request-ID"] = request_id

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["Referrer-Policy"] = "no-referrer"

    logger.info(
        "%s %s - %s - %.6f seconds - Request ID: %s",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
        request_id
    )

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []

    for error in exc.errors():

        errors.append({
            "field": ".".join(
                str(item)
                for item in error["loc"]
            ),
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    request_id = getattr(
        request.state,
        "request_id",
        "unknown"
    )

    logger.exception(
        "Unhandled exception - Request ID: %s",
        request_id
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id
        }
    )


app.include_router(
    auth_router,
    prefix="/api/v1"
)

app.include_router(
    doctor_router,
    prefix="/api/v1"
)

app.include_router(
    patient_router,
    prefix="/api/v1"
)

app.include_router(
    doctor_patient_router,
    prefix="/api/v1"
)

app.include_router(
    appointment_router,
    prefix="/api/v1"
)

app.include_router(
    billing_router,
    prefix="/api/v1"
)

app.include_router(
    reports_router,
    prefix="/api/v1"
)


@app.get("/")
def home():
    return {
        "message": "Doctor Patient Management API is working!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


def custom_openapi():

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )

    method_order = {
        "post": 1,
        "get": 2,
        "put": 3,
        "patch": 4,
        "delete": 5
    }

    appointment_order = [
        "/api/v1/appointments/",
        "/api/v1/appointments/{appointment_id}",
        "/api/v1/appointments/doctors/{doctor_id}/appointments",
        "/api/v1/appointments/patients/{patient_id}/appointments"
    ]

    billing_order = [
        "/api/v1/billings/",
        "/api/v1/billings/{billing_id}",
        "/api/v1/billings/patients/{patient_id}/billings",
        "/api/v1/billings/doctors/{doctor_id}/billings"
    ]

    report_order = [
        "/api/v1/reports/revenue"
    ]

    ordered_paths = {}

    # --------------------------------------------------------
    # Keep all non-special paths in their existing order.
    # Billing, Reports and Appointments are handled separately.
    # --------------------------------------------------------

    for path, path_data in openapi_schema["paths"].items():

        if path.startswith("/api/v1/appointments"):
            continue

        if path.startswith("/api/v1/billings"):
            continue

        if path.startswith("/api/v1/reports"):
            continue

        ordered_paths[path] = path_data


    # --------------------------------------------------------
    # Appointment paths
    # --------------------------------------------------------

    appointment_paths = {}

    for path in appointment_order:

        if path in openapi_schema["paths"]:

            path_data = openapi_schema["paths"][path]

            methods = list(
                path_data.items()
            )

            methods.sort(
                key=lambda item:
                method_order.get(
                    item[0],
                    99
                )
            )

            appointment_paths[path] = dict(methods)


    # --------------------------------------------------------
    # Billing paths
    # --------------------------------------------------------

    billing_paths = {}

    for path in billing_order:

        if path in openapi_schema["paths"]:

            path_data = openapi_schema["paths"][path]

            methods = list(
                path_data.items()
            )

            methods.sort(
                key=lambda item:
                method_order.get(
                    item[0],
                    99
                )
            )

            billing_paths[path] = dict(methods)


    # --------------------------------------------------------
    # Report paths
    # --------------------------------------------------------

    report_paths = {}

    for path in report_order:

        if path in openapi_schema["paths"]:

            path_data = openapi_schema["paths"][path]

            methods = list(
                path_data.items()
            )

            methods.sort(
                key=lambda item:
                method_order.get(
                    item[0],
                    99
                )
            )

            report_paths[path] = dict(methods)


    # --------------------------------------------------------
    # Build final path order
    #
    # Authentication
    # Doctors
    # Patients
    # Doctor-Patient
    # Appointments
    # Billings
    # Reports
    # default
    # --------------------------------------------------------

    final_paths = {}

    # Authentication
    for path, path_data in ordered_paths.items():

        if path.startswith("/api/v1/auth"):
            final_paths[path] = path_data


    # Doctors
    for path, path_data in ordered_paths.items():

        if path.startswith("/api/v1/doctors"):
            final_paths[path] = path_data


    # Patients
    for path, path_data in ordered_paths.items():

        if path.startswith("/api/v1/patients"):
            final_paths[path] = path_data


    # Doctor-Patient
    for path, path_data in ordered_paths.items():

        if path.startswith("/api/v1/doctor-patient"):
            final_paths[path] = path_data


    # Appointments
    for path, path_data in appointment_paths.items():
        final_paths[path] = path_data


    # Billings
    for path, path_data in billing_paths.items():
        final_paths[path] = path_data


    # Reports
    for path, path_data in report_paths.items():
        final_paths[path] = path_data


    # --------------------------------------------------------
    # Add any remaining API paths
    # --------------------------------------------------------

    already_added = set(final_paths.keys())

    for path, path_data in ordered_paths.items():

        if path not in already_added:
            final_paths[path] = path_data


    openapi_schema["paths"] = final_paths

    # --------------------------------------------------------
    # Swagger tag order
    # --------------------------------------------------------

    openapi_schema["tags"] = [
        {
            "name": "Authentication",
            "description": "Authentication and authorization"
        },
        {
            "name": "Doctors",
            "description": "Doctor management"
        },
        {
            "name": "Patients",
            "description": "Patient management"
        },
        {
            "name": "Doctor-Patient",
            "description": "Doctor and patient relationship management"
        },
        {
            "name": "Appointments",
            "description": "Appointment management"
        },
        {
            "name": "Billings",
            "description": "Billing and payment management"
        },
        {
            "name": "Reports",
            "description": "Billing and revenue reports"
        },
        {
            "name": "default",
            "description": "Default API endpoints"
        }
    ]

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi