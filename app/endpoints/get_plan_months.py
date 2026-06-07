import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/months",
    method="GET",
    response_model=MonthSummariesResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Months'],
    summary="Get all plan months",
    description="Returns all plan months",
    status_code=200
)
class GetPlanMonths:
    @override
    def __call__(self, plan_id: str, last_knowledge_of_server: int | None = None) -> MonthSummariesResponse:
        return MonthSummariesResponse(data=MonthSummariesResponseData(months=state.get_months(plan_id), server_knowledge=100))
