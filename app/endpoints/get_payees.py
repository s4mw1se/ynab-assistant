import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/payees",
    method="GET",
    response_model=PayeesResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Payees'],
    summary="Get all payees",
    description="Returns all payees",
    status_code=200
)
class GetPayees:
    @override
    def __call__(self, plan_id: str, last_knowledge_of_server: int | None = None) -> PayeesResponse:
        return PayeesResponse(data=PayeesResponseData(payees=state.get_payees(plan_id), server_knowledge=100))
