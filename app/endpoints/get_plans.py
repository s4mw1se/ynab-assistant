import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans",
    method="GET",
    response_model=PlanSummaryResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Plans'],
    summary="Get all plans",
    description="Returns plans list with summary information",
    status_code=200
)
class GetPlans:
    @override
    def __call__(self, include_accounts: bool | None = None) -> PlanSummaryResponse:
        return PlanSummaryResponse(data=PlanSummaryResponseData(plans=state.plans, server_knowledge=100))
