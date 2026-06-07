import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/transactions/{transaction_id}",
    method="PUT",
    response_model=TransactionResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Transactions'],
    summary="Update a transaction",
    description="Updates a single transaction",
    status_code=200
)
class UpdateTransaction:
    @override
    def __call__(self, plan_id: str, transaction_id: str, body: PutTransactionWrapper) -> TransactionResponse:
        try:
            tx = state.get_transaction(plan_id, transaction_id)
            for k, v in body.transaction.model_dump().items():
                if hasattr(tx, k) and v is not None:
                    setattr(tx, k, v)
            return TransactionResponse(data=TransactionResponseData(transaction=tx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Transaction not found")
