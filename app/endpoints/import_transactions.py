import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/transactions/import",
    method="POST",
    response_model=TransactionsImportResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Transactions'],
    summary="Import transactions",
    description="Imports available transactions on all linked accounts for the given plan.  Linked accounts allow transactions to be imported directly from a specified financial institution and this endpoint initiates that import.  Sending a request to this endpoint is the equivalent of clicking \"Import\" on each account in the web application or tapping the \"New Transactions\" banner in the mobile applications.  The response for this endpoint contains the transaction ids that have been imported.",
    status_code=200
)
class ImportTransactions:
    @override
    def __call__(self, plan_id: str) -> TransactionsImportResponse:
        return TransactionsImportResponse(data=TransactionsImportResponseData(transaction_ids=[]))
