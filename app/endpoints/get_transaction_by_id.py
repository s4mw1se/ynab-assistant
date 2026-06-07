import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/transactions/{transaction_id}",
    method="GET",
    response_model=TransactionResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Transactions'],
    summary="Get a transaction",
    description="Returns a single transaction",
    status_code=200
)
class GetTransactionById:
    @override
    def __call__(self, plan_id: str, transaction_id: str) -> TransactionResponse:
        try:
            return TransactionResponse(data=TransactionResponseData(transaction=state.get_transaction(plan_id, transaction_id), server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Transaction not found")
