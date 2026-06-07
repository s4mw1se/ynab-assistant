import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/months/{month}/money_movement_groups",
    method="GET",
    response_model=MoneyMovementGroupsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Money Movements'],
    summary="Get money movement groups for a plan month",
    description="Returns all money movement groups for a specific month",
    status_code=200
)
class GetMoneyMovementGroupsByMonth:
    @override
    def __call__(self, plan_id: str, month: dt.date | str) -> MoneyMovementGroupsResponse:
        return MoneyMovementGroupsResponse(data=MoneyMovementGroupsResponseData(money_movement_groups=[], server_knowledge=100))
