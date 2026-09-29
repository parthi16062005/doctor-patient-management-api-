
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

from app.logging_config import setup_logging


setup_logging()

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Doctor Patient Management API",
    description="Backend API for managing Doctors, Patients and Appointments",
    version="1.0.0"
)


# ==================================================
# CORS
# ==================================================

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
  
  
# ==================================================  
# RESPONSE TIME MIDDLEWARE  
# ==================================================  
  
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
    
  
  
# ==================================================  
# VALIDATION ERROR HANDLER  
# ==================================================  
  
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
  
  
# ==================================================  
# GLOBAL EXCEPTION HANDLER  
# ==================================================  
  
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


  
# ==================================================  
# ROUTERS  
# ==================================================  
  
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
  
  
# ==================================================  
# HOME  
# ==================================================  
  
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
  
# ==================================================  
# CUSTOM OPENAPI  
# ==================================================  
  
def custom_openapi():  
  
    if app.openapi_schema:  
        return app.openapi_schema  
  
    openapi_schema = get_openapi(  
        title=app.title,  
        version=app.version,  
        description=app.description,  
        routes=app.routes  
    )  
  
    appointment_order = [  
        "/api/v1/appointments/",  
        "/api/v1/appointments/{appointment_id}",  
        "/api/v1/appointments/doctors/{doctor_id}/appointments",  
        "/api/v1/appointments/patients/{patient_id}/appointments"  
    ]  
  
    method_order = {  
        "post": 1,  
        "get": 2,  
        "put": 3,  
        "delete": 4  
    }  
  
    ordered_paths = {}  
  
    for path, path_data in openapi_schema["paths"].items():  
  
        if path.startswith(  
            "/api/v1/appointments"  
        ):  
  
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
  
            ordered_paths[path] = dict(  
                methods  
            )  
  
        else:  
  
            ordered_paths[path] = path_data  
  
    openapi_schema["paths"] = ordered_paths  
  
    app.openapi_schema = openapi_schema  
  
    return app.openapi_schema  
  
  
app.openapi = custom_openapi  
