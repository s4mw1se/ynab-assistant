import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/payees/{payee_id}",
    method="PATCH",
    response_model=SavePayeeResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Payees'],
    summary="Update a payee",
    description="Update a payee",
    status_code=200
)
class UpdatePayee:
    @override
    def __call__(self, plan_id: str, payee_id: str, body: PatchPayeeWrapper) -> SavePayeeResponse:
        try:
            updates = body.payee.model_dump()
            payee = state.update_payee(plan_id, payee_id, updates)
            return SavePayeeResponse(data=SavePayeeResponseData(payee=payee, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Payee not found")
