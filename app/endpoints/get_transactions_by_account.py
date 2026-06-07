import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/accounts/{account_id}/transactions",
    method="GET",
    response_model=TransactionsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Transactions'],
    summary="Get account transactions",
    description="Returns all transactions for a specified account, excluding any pending transactions",
    status_code=200
)
class GetTransactionsByAccount:
    @override
    def __call__(self, plan_id: str, account_id: str, since_date: dt.date | str | None = None, until_date: dt.date | str | None = None, type: Literal['uncategorized', 'unapproved'] | None = None, last_knowledge_of_server: int | None = None) -> TransactionsResponse:
        return TransactionsResponse(data=TransactionsResponseData(transactions=state.get_transactions(plan_id), server_knowledge=100))
