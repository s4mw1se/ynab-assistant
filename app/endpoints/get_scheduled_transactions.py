import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/scheduled_transactions",
    method="GET",
    response_model=ScheduledTransactionsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Scheduled Transactions'],
    summary="Get all scheduled transactions",
    description="Returns all scheduled transactions",
    status_code=200
)
class GetScheduledTransactions:
    @override
    def __call__(self, plan_id: str, last_knowledge_of_server: int | None = None) -> ScheduledTransactionsResponse:
        return ScheduledTransactionsResponse(data=ScheduledTransactionsResponseData(scheduled_transactions=state.get_scheduled_transactions(plan_id), server_knowledge=100))
