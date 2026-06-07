import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/payees",
    method="POST",
    response_model=SavePayeeResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Payees'],
    summary="Create a payee",
    description="Creates a new payee",
    status_code=201
)
class CreatePayee:
    @override
    def __call__(self, plan_id: str, body: PostPayeeWrapper) -> SavePayeeResponse:
        import uuid
        payee = Payee(
            id=f"payee_{uuid.uuid4().hex[:6]}",
            name=body.payee.name,
            transfer_account_id=None,
            deleted=False
        )
        state.create_payee(plan_id, payee)
        return SavePayeeResponse(data=SavePayeeResponseData(payee=payee, server_knowledge=100))
