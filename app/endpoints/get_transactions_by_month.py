import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/months/{month}/transactions",
    method="GET",
    response_model=TransactionsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Transactions'],
    summary="Get plan month transactions",
    description="Returns all transactions for a specified month, excluding any pending transactions",
    status_code=200
)
class GetTransactionsByMonth:
    @override
    def __call__(self, plan_id: str, month: str, since_date: dt.date | str | None = None, until_date: dt.date | str | None = None, type: Literal['uncategorized', 'unapproved'] | None = None, last_knowledge_of_server: int | None = None) -> TransactionsResponse:
        return TransactionsResponse(data=TransactionsResponseData(transactions=state.get_transactions(plan_id), server_knowledge=100))
