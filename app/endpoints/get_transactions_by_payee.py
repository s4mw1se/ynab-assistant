import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/payees/{payee_id}/transactions",
    method="GET",
    response_model=HybridTransactionsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Transactions'],
    summary="Get payee transactions",
    description="Returns all transactions for a specified payee, excluding any pending transactions",
    status_code=200
)
class GetTransactionsByPayee:
    @override
    def __call__(self, plan_id: str, payee_id: str, since_date: dt.date | str | None = None, until_date: dt.date | str | None = None, type: Literal['uncategorized', 'unapproved'] | None = None, last_knowledge_of_server: int | None = None) -> HybridTransactionsResponse:
        return HybridTransactionsResponse(data=HybridTransactionsResponseData(transactions=[], server_knowledge=100))
