from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import admin_required
from app.models.billing import Billing
from app.models.doctor import Doctor
from app.models.user import User


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get(
    "/revenue",
    summary="Get revenue reports",
    description="""
Retrieve revenue reports from paid billing records.

Only billing records with payment_status = paid
are included in revenue calculations.

Optional filters:
- doctor_id
- from
- to

The response contains:
- total revenue
- revenue per doctor
- revenue per day

Only administrators can access revenue reports.
""",
    responses={
        200: {
            "description": "Revenue report generated successfully"
        },
        400: {
            "description": "Invalid date range"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def get_revenue_report(
    doctor_id: int | None = Query(
        default=None,
        ge=1,
        description="Filter revenue by doctor ID"
    ),
    from_date: datetime | None = Query(
        default=None,
        alias="from",
        description="Start date"
    ),
    to_date: datetime | None = Query(
        default=None,
        alias="to",
        description="End date"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    if (
        from_date is not None
        and to_date is not None
        and from_date > to_date
    ):
        raise HTTPException(
            status_code=400,
            detail="from cannot be greater than to"
        )

    # --------------------------------------------------------
    # Base query
    # --------------------------------------------------------

    query = (
        db.query(Billing)
        .filter(
            Billing.is_active == True,
            Billing.payment_status == "paid"
        )
    )

    # --------------------------------------------------------
    # Doctor filter
    # --------------------------------------------------------

    if doctor_id is not None:

        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == doctor_id)
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found"
            )

        query = query.filter(
            Billing.doctor_id == doctor_id
        )

    # --------------------------------------------------------
    # Date filters
    # --------------------------------------------------------

    if from_date is not None:
        query = query.filter(
            Billing.created_at >= from_date
        )

    if to_date is not None:
        query = query.filter(
            Billing.created_at <= to_date
        )

    billings = query.order_by(
        Billing.created_at
    ).all()

    # --------------------------------------------------------
    # Total revenue
    # --------------------------------------------------------

    total_revenue = sum(
        billing.total_amount
        for billing in billings
    )

    # --------------------------------------------------------
    # Revenue per doctor
    # --------------------------------------------------------

    doctor_revenue = {}

    for billing in billings:

        doctor_id_key = billing.doctor_id

        if doctor_id_key not in doctor_revenue:
            doctor_revenue[doctor_id_key] = 0

        doctor_revenue[doctor_id_key] += billing.total_amount

    doctor_revenue_result = []

    for doctor_id_key, amount in doctor_revenue.items():

        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == doctor_id_key)
            .first()
        )

        doctor_revenue_result.append({
            "doctor_id": doctor_id_key,
            "doctor_name": doctor.name if doctor else None,
            "revenue": amount
        })

    # --------------------------------------------------------
    # Revenue per day
    # --------------------------------------------------------

    daily_revenue = {}

    for billing in billings:

        date_key = billing.created_at.date().isoformat()

        if date_key not in daily_revenue:
            daily_revenue[date_key] = 0

        daily_revenue[date_key] += billing.total_amount

    daily_revenue_result = []

    for date_key, amount in sorted(
        daily_revenue.items()
    ):
        daily_revenue_result.append({
            "date": date_key,
            "revenue": amount
        })

    return {
        "total_revenue": total_revenue,
        "doctor_revenue": doctor_revenue_result,
        "daily_revenue": daily_revenue_result
    }