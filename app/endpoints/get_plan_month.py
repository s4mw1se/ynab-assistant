import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/months/{month}",
    method="GET",
    response_model=MonthDetailResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Months'],
    summary="Get a plan month",
    description="Returns a single plan month",
    status_code=200
)
class GetPlanMonth:
    @override
    def __call__(self, plan_id: str, month: dt.date | str) -> MonthDetailResponse:
        try:
            # Parse month date
            from datetime import datetime
            parsed_month = datetime.strptime(str(month), "%Y-%m-%d").date()
            return MonthDetailResponse(data=MonthDetailResponseData(month=state.get_month(plan_id, parsed_month), server_knowledge=100))
        except Exception:
            raise HTTPException(status_code=404, detail="Month not found")
