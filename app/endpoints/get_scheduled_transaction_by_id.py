import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/scheduled_transactions/{scheduled_transaction_id}",
    method="GET",
    response_model=ScheduledTransactionResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Scheduled Transactions'],
    summary="Get a scheduled transaction",
    description="Returns a single scheduled transaction",
    status_code=200
)
class GetScheduledTransactionById:
    @override
    def __call__(self, plan_id: str, scheduled_transaction_id: str) -> ScheduledTransactionResponse:
        try:
            return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=state.get_scheduled_transaction(plan_id, scheduled_transaction_id), server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Scheduled Transaction not found")
