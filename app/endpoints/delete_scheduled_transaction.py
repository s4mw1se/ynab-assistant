import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/scheduled_transactions/{scheduled_transaction_id}",
    method="DELETE",
    response_model=ScheduledTransactionResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Scheduled Transactions'],
    summary="Delete a scheduled transaction",
    description="Deletes a scheduled transaction",
    status_code=200
)
class DeleteScheduledTransaction:
    @override
    def __call__(self, plan_id: str, scheduled_transaction_id: str) -> ScheduledTransactionResponse:
        try:
            stx = state.delete_scheduled_transaction(plan_id, scheduled_transaction_id)
            return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=stx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Scheduled Transaction not found")
