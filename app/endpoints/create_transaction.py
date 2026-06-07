import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/transactions",
    method="POST",
    response_model=SaveTransactionsResponse,
    responses={400: {'model': 'ErrorResponse'}, 409: {'model': 'ErrorResponse'}},
    tags=['Transactions'],
    summary="Create a single transaction or multiple transactions",
    description="Creates a single transaction or multiple transactions.  If you provide a body containing a `transaction` object, a single transaction will be created and if you provide a body containing a `transactions` array, multiple transactions will be created.  Scheduled transactions (transactions with a future date) cannot be created on this endpoint.",
    status_code=201
)
class CreateTransaction:
    @override
    def __call__(self, plan_id: str, body: PostTransactionsWrapper) -> SaveTransactionsResponse:
        import uuid
        created_txs = []
        if hasattr(body, 'transaction') and body.transaction:
            t_data = body.transaction
            tx = TransactionDetail(
                id=f"tx_{uuid.uuid4().hex[:6]}",
                date=t_data.date,
                amount=t_data.amount,
                memo=t_data.memo,
                cleared=t_data.cleared or "uncleared",
                approved=t_data.approved or False,
                flag_color=t_data.flag_color,
                account_id=t_data.account_id,
                account_name="Checking Account",
                payee_id=t_data.payee_id,
                payee_name=t_data.payee_name,
                category_id=t_data.category_id,
                category_name="Rent",
                transfer_account_id=None,
                transfer_transaction_id=None,
                matched_transaction_id=None,
                import_id=t_data.import_id,
                deleted=False,
                subtransactions=[],
                debt_transaction_type=None
            )
            state.create_transaction(plan_id, tx)
            created_txs.append(tx)
        elif hasattr(body, 'transactions') and body.transactions:
            for t_data in body.transactions:
                tx = TransactionDetail(
                    id=f"tx_{uuid.uuid4().hex[:6]}",
                    date=t_data.date,
                    amount=t_data.amount,
                    memo=t_data.memo,
                    cleared=t_data.cleared or "uncleared",
                    approved=t_data.approved or False,
                    flag_color=t_data.flag_color,
                    account_id=t_data.account_id,
                    account_name="Checking Account",
                    payee_id=t_data.payee_id,
                    payee_name=t_data.payee_name,
                    category_id=t_data.category_id,
                    category_name="Rent",
                    transfer_account_id=None,
                    transfer_transaction_id=None,
                    matched_transaction_id=None,
                    import_id=t_data.import_id,
                    deleted=False,
                    subtransactions=[],
                    debt_transaction_type=None
                )
                state.create_transaction(plan_id, tx)
                created_txs.append(tx)
        
        return SaveTransactionsResponse(
            data=SaveTransactionsResponseData(
                transaction_ids=[x.id for x in created_txs],
                transactions=created_txs,
                server_knowledge=101
            )
        )
