import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/accounts",
    method="GET",
    response_model=AccountsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Accounts'],
    summary="Get all accounts",
    description="Returns all accounts",
    status_code=200
)
class GetAccounts:
    @override
    def __call__(self, plan_id: str, last_knowledge_of_server: int | None = None) -> AccountsResponse:
        return AccountsResponse(data=AccountsResponseData(accounts=state.get_accounts(plan_id), server_knowledge=100))
