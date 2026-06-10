with open("scratch/generator.py") as f:
    content = f.read()

# Define the boundaries
start_marker = "        # Determine Success Response Schema"
end_marker = "# Write app/endpoints/__init__.py"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print(f"Error: Markers not found! Start: {start_idx}, End: {end_idx}")
    exit(1)

# Define the replacement text
replacement_text = """        # Determine Success Response Schema
        resp_val = None
        success_code = 200
        for code in ["200", "201", "209", "202", "204"]:
            if code in op_val.get("responses", {}):
                resp_val = op_val["responses"][code]
                success_code = int(code)
                break
                
        resp_schema_name = "Any"
        if resp_val and "content" in resp_val:
            content_val = resp_val["content"].get("application/json", {})
            if "schema" in content_val:
                schema_ref = content_val["schema"].get("$ref", "")
                if schema_ref:
                    resp_schema_name = schema_ref.split("/")[-1]
        
        # Determine error responses
        responses_dict = {}
        for code, r_val in op_val.get("responses", {}).items():
            if code in ["200", "201", "209", "202", "204"]:
                continue
            if "content" in r_val:
                c_val = r_val["content"].get("application/json", {})
                if "schema" in c_val:
                    ref = c_val["schema"].get("$ref", "")
                    if ref:
                        responses_dict[int(code)] = {"model": ref.split("/")[-1]}
        
        # Extract inputs (Parameters and RequestBody)
        params = op_val.get("parameters", [])
        # Also include path parameters defined on the path item level
        params += path_item.get("parameters", [])
        
        path_params = []
        query_params = []
        
        for param in params:
            p_name = param["name"]
            p_in = param["in"]
            p_req = param.get("required", False)
            p_schema = param.get("schema", {})
            p_type = map_type(p_schema)
            
            # ensure standard date type representation is handled correctly
            if p_type == "dt.date":
                p_type = "dt.date | str"
                
            if p_in == "path":
                path_params.append((p_name, p_type, p_req))
            elif p_in == "query":
                query_params.append((p_name, p_type, p_req))
        
        body_param = None
        if "requestBody" in op_val:
            body_content = op_val["requestBody"].get("content", {}).get("application/json", {})
            if "schema" in body_content:
                body_ref = body_content["schema"].get("$ref", "")
                if body_ref:
                    body_param = body_ref.split("/")[-1]
        
        # Formulate Python __call__ signature
        sig_args = ["self"]
        for p_name, p_type, _ in path_params:
            sig_args.append(f"{p_name}: {p_type}")
        if body_param:
            sig_args.append(f"body: {body_param}")
        for p_name, p_type, p_req in query_params:
            if p_req:
                sig_args.append(f"{p_name}: {p_type}")
            else:
                sig_args.append(f"{p_name}: {p_type} | None = None")
                
        sig_str = ", ".join(sig_args)
        
        # Write individual endpoint file
        tags_list = op_val.get("tags", [])
        summary = op_val.get("summary", "")
        description = op_val.get("description", "")
        
        # Create standard mock implementations
        mock_body = ""
        # Let's map typical response values based on the response schema name
        if resp_schema_name == "UserResponse":
            mock_body = "return UserResponse(data=UserResponseData(user=state.user))"
        elif resp_schema_name == "PlanSummaryResponse":
            mock_body = "return PlanSummaryResponse(data=PlanSummaryResponseData(plans=state.plans, server_knowledge=100))"
        elif resp_schema_name == "PlanDetailResponse":
            mock_body = \"\"\"try:
            return PlanDetailResponse(data=PlanDetailResponseData(plan=state.get_plan_detail(plan_id), server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Plan not found")\"\"\"
        elif resp_schema_name == "PlanSettingsResponse":
            mock_body = \"\"\"try:
            return PlanSettingsResponse(data=PlanSettingsResponseData(settings=state.get_plan_settings(plan_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Plan not found")\"\"\"
        elif resp_schema_name == "AccountsResponse":
            mock_body = "return AccountsResponse(data=AccountsResponseData(accounts=state.get_accounts(plan_id), server_knowledge=100))"
        elif resp_schema_name == "AccountResponse":
            if method_str == "post":
                # Create Account
                mock_body = \"\"\"import uuid
        acc = Account(
            id=f"account_{uuid.uuid4().hex[:6]}",
            name=body.account.name,
            type=body.account.type,
            balance=body.account.balance,
            on_budget=True,
            closed=False,
            note=None,
            cleared_balance=body.account.balance,
            uncleared_balance=0,
            transfer_payee_id=None,
            deleted=False
        )
        state.create_account(plan_id, acc)
        return AccountResponse(data=AccountResponseData(account=acc))\"\"\"
            else:
                # Get Account
                mock_body = \"\"\"try:
            return AccountResponse(data=AccountResponseData(account=state.get_account(plan_id, account_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Account not found")\"\"\"
        elif resp_schema_name == "CategoriesResponse":
            mock_body = "return CategoriesResponse(data=CategoriesResponseData(category_groups=state.get_category_groups(plan_id), server_knowledge=100))"
        elif resp_schema_name == "CategoryResponse":
            if method_str == "post":
                mock_body = \"\"\"import uuid
        cat = Category(
            id=f"cat_{uuid.uuid4().hex[:6]}",
            category_group_id=body.category.category_group_id or "group_1",
            category_group_name="Immediate Obligations",
            name=body.category.name,
            hidden=False,
            internal=False,
            original_category_group_id=None,
            note=None,
            budgeted=0,
            activity=0,
            balance=0,
            deleted=False
        )
        state.create_category(plan_id, cat)
        return CategoryResponse(data=CategoryResponseData(category=cat))\"\"\"
            else:
                # Get Category
                mock_body = \"\"\"try:
            return CategoryResponse(data=CategoryResponseData(category=state.get_category(plan_id, category_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Category not found")\"\"\"
        elif resp_schema_name == "SaveCategoryResponse":
            if method_str == "post":
                # Create category (POST /plans/{plan_id}/categories) returns SaveCategoryResponse
                mock_body = \"\"\"import uuid
        cat = Category(
            id=f"cat_{uuid.uuid4().hex[:6]}",
            category_group_id="group_1",
            category_group_name="Immediate Obligations",
            name=body.category.name,
            hidden=False,
            internal=False,
            original_category_group_id=None,
            note=None,
            budgeted=0,
            activity=0,
            balance=0,
            deleted=False
        )
        state.create_category(plan_id, cat)
        return SaveCategoryResponse(data=SaveCategoryResponseData(category=cat, server_knowledge=100))\"\"\"
            else:
                # Update Category or Update Month Category
                mock_body = \"\"\"try:
            updates = body.category.model_dump()
            cat = state.update_category(plan_id, category_id, updates)
            return SaveCategoryResponse(data=SaveCategoryResponseData(category=cat, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Category not found")\"\"\"
        elif resp_schema_name == "SaveCategoryGroupResponse":
            if method_str == "post":
                # Create category group
                mock_body = \"\"\"import uuid
        group = CategoryGroupWithCategories(
            id=f"group_{uuid.uuid4().hex[:6]}",
            name=body.category_group.name,
            hidden=False,
            internal=False,
            deleted=False,
            categories=[]
        )
        state.category_groups.setdefault(plan_id, []).append(group)
        return SaveCategoryGroupResponse(data=SaveCategoryGroupResponseData(category_group=group, server_knowledge=100))\"\"\"
            else:
                # Update Category Group
                mock_body = \"\"\"groups = state.get_category_groups(plan_id)
        for g in groups:
            if g.id == category_group_id:
                if body.category_group.name:
                    g.name = body.category_group.name
                return SaveCategoryGroupResponse(data=SaveCategoryGroupResponseData(category_group=g, server_knowledge=100))
        raise HTTPException(status_code=404, detail="Category group not found")\"\"\"
        elif resp_schema_name == "PayeesResponse":
            mock_body = "return PayeesResponse(data=PayeesResponseData(payees=state.get_payees(plan_id), server_knowledge=100))"
        elif resp_schema_name == "PayeeResponse":
            if method_str == "post":
                mock_body = \"\"\"import uuid
        payee = Payee(
            id=f"payee_{uuid.uuid4().hex[:6]}",
            name=body.payee.name,
            transfer_account_id=None,
            deleted=False
        )
        state.create_payee(plan_id, payee)
        return PayeeResponse(data=PayeeResponseData(payee=payee))\"\"\"
            else:
                mock_body = \"\"\"try:
            return PayeeResponse(data=PayeeResponseData(payee=state.get_payee(plan_id, payee_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Payee not found")\"\"\"
        elif resp_schema_name == "SavePayeeResponse":
            if method_str == "post":
                # Create payee
                mock_body = \"\"\"import uuid
        payee = Payee(
            id=f"payee_{uuid.uuid4().hex[:6]}",
            name=body.payee.name,
            transfer_account_id=None,
            deleted=False
        )
        state.create_payee(plan_id, payee)
        return SavePayeeResponse(data=SavePayeeResponseData(payee=payee, server_knowledge=100))\"\"\"
            else:
                # Update payee
                mock_body = \"\"\"try:
            updates = body.payee.model_dump()
            payee = state.update_payee(plan_id, payee_id, updates)
            return SavePayeeResponse(data=SavePayeeResponseData(payee=payee, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Payee not found")\"\"\"
        elif resp_schema_name == "PayeeLocationsResponse":
            mock_body = "return PayeeLocationsResponse(data=PayeeLocationsResponseData(payee_locations=state.get_payee_locations(plan_id), server_knowledge=100))"
        elif resp_schema_name == "PayeeLocationResponse":
            mock_body = \"\"\"try:
            return PayeeLocationResponse(data=PayeeLocationResponseData(payee_location=state.get_payee_location(plan_id, payee_location_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Payee Location not found")\"\"\"
        elif resp_schema_name == "MonthSummariesResponse":
            mock_body = "return MonthSummariesResponse(data=MonthSummariesResponseData(months=state.get_months(plan_id), server_knowledge=100))"
        elif resp_schema_name == "MonthDetailResponse":
            mock_body = \"\"\"try:
            # Parse month date
            from datetime import datetime
            parsed_month = datetime.strptime(str(month), "%Y-%m-%d").date()
            return MonthDetailResponse(data=MonthDetailResponseData(month=state.get_month(plan_id, parsed_month), server_knowledge=100))
        except Exception:
            raise HTTPException(status_code=404, detail="Month not found")\"\"\"
        elif resp_schema_name == "MoneyMovementsResponse":
            mock_body = "return MoneyMovementsResponse(data=MoneyMovementsResponseData(money_movements=state.get_money_movements(plan_id), server_knowledge=100))"
        elif resp_schema_name == "MoneyMovementGroupsResponse":
            mock_body = "return MoneyMovementGroupsResponse(data=MoneyMovementGroupsResponseData(money_movement_groups=[], server_knowledge=100))"
        elif resp_schema_name == "TransactionsResponse":
            mock_body = "return TransactionsResponse(data=TransactionsResponseData(transactions=state.get_transactions(plan_id), server_knowledge=100))"
        elif resp_schema_name == "HybridTransactionsResponse":
            mock_body = "return HybridTransactionsResponse(data=HybridTransactionsResponseData(transactions=[], server_knowledge=100))"
        elif resp_schema_name == "TransactionResponse":
            if method_str == "put":
                # Update individual Transaction
                mock_body = \"\"\"try:
            tx = state.get_transaction(plan_id, transaction_id)
            for k, v in body.transaction.model_dump().items():
                if hasattr(tx, k) and v is not None:
                    setattr(tx, k, v)
            return TransactionResponse(data=TransactionResponseData(transaction=tx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Transaction not found")\"\"\"
            elif method_str == "delete":
                # Delete Transaction
                mock_body = \"\"\"try:
            tx = state.delete_transaction(plan_id, transaction_id)
            return TransactionResponse(data=TransactionResponseData(transaction=tx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Transaction not found")\"\"\"
            else:
                # Get Transaction
                mock_body = \"\"\"try:
            return TransactionResponse(data=TransactionResponseData(transaction=state.get_transaction(plan_id, transaction_id), server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Transaction not found")\"\"\"
        elif resp_schema_name == "SaveTransactionsResponse":
            # Create transactions (Bulk/Multi) or Update multiple transactions
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
        elif resp_schema_name == "TransactionsImportResponse":
            mock_body = "return TransactionsImportResponse(data=TransactionsImportResponseData(transaction_ids=[]))"
        elif resp_schema_name == "BulkResponse":
            mock_body = "return BulkResponse(data=BulkResponseData(bulk=BulkTransactions(transaction_ids=[], duplicate_import_ids=[])))"
        elif resp_schema_name == "ScheduledTransactionsResponse":
            mock_body = "return ScheduledTransactionsResponse(data=ScheduledTransactionsResponseData(scheduled_transactions=state.get_scheduled_transactions(plan_id), server_knowledge=100))"
        elif resp_schema_name == "ScheduledTransactionResponse":
            if method_str == "put":
                # Update scheduled tx
                mock_body = \"\"\"try:
            stx = state.get_scheduled_transaction(plan_id, scheduled_transaction_id)
            for k, v in body.scheduled_transaction.model_dump().items():
                if hasattr(stx, k) and v is not None:
                    setattr(stx, k, v)
            return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=stx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Scheduled Transaction not found")\"\"\"
            elif method_str == "delete":
                # Delete scheduled tx
                mock_body = \"\"\"try:
            stx = state.delete_scheduled_transaction(plan_id, scheduled_transaction_id)
            return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=stx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Scheduled Transaction not found")\"\"\"
            elif method_str == "post":
                # Create scheduled tx
                mock_body = \"\"\"import uuid
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
        return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=stx, server_knowledge=100))\"\"\"
            else:
                # Get scheduled tx
                mock_body = \"\"\"try:
            return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=state.get_scheduled_transaction(plan_id, scheduled_transaction_id), server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Scheduled Transaction not found")\"\"\"
        else:
            mock_body = "return {}"
            
        endpoint_file_content = f\"\"\"import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="{path_str}",
    method="{method_str.upper()}",
    response_model={resp_schema_name},
    responses={responses_dict},
    tags={tags_list},
    summary=\"{escape_desc(summary)}\",
    description=\"{escape_desc(description)}\",
    status_code={success_code}
)
class {classname}:
    @override
    def __call__({sig_str}) -> {resp_schema_name}:
        {mock_body}
\"\"\"
        with open(f"app/endpoints/{filename}.py", "w") as f_ep:
            f_ep.write(endpoint_file_content)
            
        # Create Test Case for this endpoint
        test_path = path_str.replace("{plan_id}", "plan_default") \
                            .replace("{account_id}", "account_1") \
                            .replace("{category_id}", "category_1") \
                            .replace("{category_group_id}", "group_1") \
                            .replace("{payee_id}", "payee_1") \
                            .replace("{payee_location_id}", "loc_1") \
                            .replace("{month}", "2026-06-01") \
                            .replace("{transaction_id}", "tx_1") \
                            .replace("{scheduled_transaction_id}", "sch_1")
                            
        # Formulate request arguments/body for post/put/patch
        req_kwargs = ""
        test_setup = ""
        
        if method_str in ["post", "put", "patch"] and body_param:
            # We construct a mock payload based on body_param name
            if body_param == "PostAccountWrapper":
                test_setup = ""
                req_kwargs = ', json={"account": {"name": "New Savings", "type": "savings", "balance": 1000000}}'
            elif body_param == "PostTransactionsWrapper":
                req_kwargs = ', json={"transaction": {"account_id": "account_1", "date": "2026-06-01", "amount": -50000, "payee_id": "payee_1", "category_id": "category_1", "memo": "Coffee"}}'
            elif body_param == "PatchTransactionsWrapper":
                req_kwargs = ', json={"transactions": [{"id": "tx_1", "memo": "Updated Rent memo"}]}'
            elif body_param == "PutTransactionWrapper":
                req_kwargs = ', json={"transaction": {"account_id": "account_1", "date": "2026-06-01", "amount": -1000000, "payee_id": "payee_1", "category_id": "category_1", "memo": "Updated Rent Payment"}}'
            elif body_param == "PostPayeeWrapper":
                req_kwargs = ', json={"payee": {"name": "New Payee"}}'
            elif body_param == "PatchPayeeWrapper":
                req_kwargs = ', json={"payee": {"name": "Updated Payee Name"}}'
            elif body_param == "PostCategoryWrapper":
                req_kwargs = ', json={"category": {"name": "Subcategory"}}'
            elif body_param == "PatchCategoryWrapper":
                req_kwargs = ', json={"category": {"name": "Renamed Rent", "note": "Updated note"}}'
            elif body_param == "PatchMonthCategoryWrapper":
                req_kwargs = ', json={"category": {"budgeted": 1200000}}'
            elif body_param == "PostCategoryGroupWrapper":
                req_kwargs = ', json={"category_group": {"name": "New Group"}}'
            elif body_param == "PatchCategoryGroupWrapper":
                req_kwargs = ', json={"category_group": {"name": "Updated Group Name"}}'
            elif body_param == "PostScheduledTransactionWrapper":
                req_kwargs = ', json={"scheduled_transaction": {"account_id": "account_1", "date": "2026-08-01", "frequency": "monthly", "amount": -50000, "payee_id": "payee_1", "category_id": "category_1", "memo": "Monthly Sub"}}'
            elif body_param == "PutScheduledTransactionWrapper":
                req_kwargs = ', json={"scheduled_transaction": {"account_id": "account_1", "date": "2026-08-01", "frequency": "monthly", "amount": -60000, "memo": "Updated Sub"}}'
            else:
                req_kwargs = ', json={}'
                
        test_case_code = f\"\"\"
def test_{filename}():
    {test_setup.strip()}
    response = client.{method_str}("/v1{test_path}"{req_kwargs})
    assert response.status_code == {success_code}
    data = response.json()
    assert "data" in data
\"\"\"
        test_cases.append(test_case_code)
"""

new_content = content[:start_idx] + replacement_text + content[end_idx:]

with open("scratch/generator.py", "w") as f:
    f.write(new_content)

print("Generator updated successfully!")
