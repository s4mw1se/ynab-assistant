import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/accounts/{account_id}",
    method="GET",
    response_model=AccountResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Accounts'],
    summary="Get an account",
    description="Returns a single account",
    status_code=200
)
class GetAccountById:
    @override
    def __call__(self, plan_id: str, account_id: str) -> AccountResponse:
        try:
            return AccountResponse(data=AccountResponseData(account=state.get_account(plan_id, account_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Account not found")
