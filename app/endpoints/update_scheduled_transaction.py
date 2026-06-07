import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/scheduled_transactions/{scheduled_transaction_id}",
    method="PUT",
    response_model=ScheduledTransactionResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Scheduled Transactions'],
    summary="Update a scheduled transaction",
    description="Updates a single scheduled transaction",
    status_code=200
)
class UpdateScheduledTransaction:
    @override
    def __call__(self, plan_id: str, scheduled_transaction_id: str, body: PutScheduledTransactionWrapper) -> ScheduledTransactionResponse:
        try:
            stx = state.get_scheduled_transaction(plan_id, scheduled_transaction_id)
            for k, v in body.scheduled_transaction.model_dump().items():
                if hasattr(stx, k) and v is not None:
                    setattr(stx, k, v)
            return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=stx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Scheduled Transaction not found")
