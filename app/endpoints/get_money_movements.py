import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/money_movements",
    method="GET",
    response_model=MoneyMovementsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Money Movements'],
    summary="Get all money movements",
    description="Returns all money movements",
    status_code=200
)
class GetMoneyMovements:
    @override
    def __call__(self, plan_id: str) -> MoneyMovementsResponse:
        return MoneyMovementsResponse(data=MoneyMovementsResponseData(money_movements=state.get_money_movements(plan_id), server_knowledge=100))
