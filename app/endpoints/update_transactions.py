import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/transactions",
    method="PATCH",
    response_model=SaveTransactionsResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Transactions'],
    summary="Update multiple transactions",
    description="Updates multiple transactions, by `id` or `import_id`.",
    status_code=209
)
class UpdateTransactions:
    @override
    def __call__(self, plan_id: str, body: PatchTransactionsWrapper) -> SaveTransactionsResponse:
        import uuid
        updated_txs = []
        if hasattr(body, 'transactions') and body.transactions:
            for t_data in body.transactions:
                try:
                    tx = state.get_transaction(plan_id, t_data.id)
                    for k, v in t_data.model_dump().items():
                        if hasattr(tx, k) and v is not None:
                            setattr(tx, k, v)
                    updated_txs.append(tx)
                except KeyError:
                    pass
        return SaveTransactionsResponse(
            data=SaveTransactionsResponseData(
                transaction_ids=[x.id for x in updated_txs],
                transactions=updated_txs,
                server_knowledge=101
            )
        )
