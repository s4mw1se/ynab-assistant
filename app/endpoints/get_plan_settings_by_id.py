import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/settings",
    method="GET",
    response_model=PlanSettingsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Plans'],
    summary="Get plan settings",
    description="Returns settings for a plan",
    status_code=200
)
class GetPlanSettingsById:
    @override
    def __call__(self, plan_id: str) -> PlanSettingsResponse:
        try:
            return PlanSettingsResponse(data=PlanSettingsResponseData(settings=state.get_plan_settings(plan_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Plan not found")
