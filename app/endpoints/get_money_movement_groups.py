import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/money_movement_groups",
    method="GET",
    response_model=MoneyMovementGroupsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Money Movements'],
    summary="Get all money movement groups",
    description="Returns all money movement groups",
    status_code=200
)
class GetMoneyMovementGroups:
    @override
    def __call__(self, plan_id: str) -> MoneyMovementGroupsResponse:
        return MoneyMovementGroupsResponse(data=MoneyMovementGroupsResponseData(money_movement_groups=[], server_knowledge=100))
