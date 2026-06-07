import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/payees/{payee_id}",
    method="GET",
    response_model=PayeeResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Payees'],
    summary="Get a payee",
    description="Returns a single payee",
    status_code=200
)
class GetPayeeById:
    @override
    def __call__(self, plan_id: str, payee_id: str) -> PayeeResponse:
        try:
            return PayeeResponse(data=PayeeResponseData(payee=state.get_payee(plan_id, payee_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Payee not found")
