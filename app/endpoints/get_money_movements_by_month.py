import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/months/{month}/money_movements",
    method="GET",
    response_model=MoneyMovementsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Money Movements'],
    summary="Get money movements for a plan month",
    description="Returns all money movements for a specific month",
    status_code=200
)
class GetMoneyMovementsByMonth:
    @override
    def __call__(self, plan_id: str, month: dt.date | str) -> MoneyMovementsResponse:
        return MoneyMovementsResponse(data=MoneyMovementsResponseData(money_movements=state.get_money_movements(plan_id), server_knowledge=100))
