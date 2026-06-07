import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/accounts",
    method="POST",
    response_model=AccountResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Accounts'],
    summary="Create an account",
    description="Creates a new account",
    status_code=201
)
class CreateAccount:
    @override
    def __call__(self, plan_id: str, body: PostAccountWrapper) -> AccountResponse:
        import uuid
        acc = Account(
            id=f"account_{uuid.uuid4().hex[:6]}",
            name=body.account.name,
            type=body.account.type,
            balance=body.account.balance,
            on_budget=True,
            closed=False,
            note=None,
            cleared_balance=body.account.balance,
            uncleared_balance=0,
            transfer_payee_id=f"payee_transfer_{uuid.uuid4().hex[:6]}",
            deleted=False
        )
        state.create_account(plan_id, acc)
        return AccountResponse(data=AccountResponseData(account=acc))
