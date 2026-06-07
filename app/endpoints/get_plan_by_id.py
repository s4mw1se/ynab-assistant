import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}",
    method="GET",
    response_model=PlanDetailResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Plans'],
    summary="Get a plan",
    description="Returns a single plan with all related entities.  This resource is effectively a full plan export.",
    status_code=200
)
class GetPlanById:
    @override
    def __call__(self, plan_id: str, last_knowledge_of_server: int | None = None) -> PlanDetailResponse:
        try:
            return PlanDetailResponse(data=PlanDetailResponseData(plan=state.get_plan_detail(plan_id), server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Plan not found")
