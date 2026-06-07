import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/scheduled_transactions",
    method="POST",
    response_model=ScheduledTransactionResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Scheduled Transactions'],
    summary="Create a scheduled transaction",
    description="Creates a single scheduled transaction (a transaction with a future date).",
    status_code=201
)
class CreateScheduledTransaction:
    @override
    def __call__(self, plan_id: str, body: PostScheduledTransactionWrapper) -> ScheduledTransactionResponse:
        import uuid
        stx = ScheduledTransactionDetail(
            id=f"sch_{uuid.uuid4().hex[:6]}",
            date_next=body.scheduled_transaction.date,
            date_first=dt.date.today(),
            frequency=body.scheduled_transaction.frequency or "never",
            amount=body.scheduled_transaction.amount,
            memo=body.scheduled_transaction.memo,
            flag_color=body.scheduled_transaction.flag_color,
            account_id=body.scheduled_transaction.account_id,
            account_name="Checking Account",
            payee_id=body.scheduled_transaction.payee_id,
            payee_name=None,
            category_id=body.scheduled_transaction.category_id,
            category_name=None,
            transfer_account_id=None,
            deleted=False,
            subtransactions=[]
        )
        state.create_scheduled_transaction(plan_id, stx)
        return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=stx, server_knowledge=100))
