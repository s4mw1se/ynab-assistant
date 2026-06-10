with open("scratch/generator.py") as f:
    content = f.read()

start_marker = '        elif resp_schema_name == "SaveTransactionsResponse":'
end_marker = '        elif resp_schema_name == "TransactionsImportResponse":'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Error: SaveTransactionsResponse markers not found!")
    exit(1)

new_block = """        elif resp_schema_name == "SaveTransactionsResponse":
            if method_str == "patch":
                mock_body = \"\"\"import uuid
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
        )\"\"\"
            else:
                # Create transactions (Bulk/Multi)
                mock_body = \"\"\"import uuid
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
        )\"\"\"
"""

content = content[:start_idx] + new_block + content[end_idx:]

with open("scratch/generator.py", "w") as f:
    f.write(content)

print("Generator updated successfully (pass 3)!")
