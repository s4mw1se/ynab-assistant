import json
import os
import re
from typing import Dict, Any, List

# Load OpenAPI spec
with open("ynab-api-spec.json") as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})
paths = spec.get("paths", {})

# Setup output directories
os.makedirs("app", exist_ok=True)
os.makedirs("app/core", exist_ok=True)
os.makedirs("app/endpoints", exist_ok=True)
os.makedirs("tests", exist_ok=True)

# Helper function to convert camelCase to snake_case
def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# Helper function to escape descriptions
def escape_desc(desc: str) -> str:
    if not desc:
        return ""
    return desc.replace('"', '\\"').replace('\n', ' ')

# Helper to map OpenAPI schema type to Python/Pydantic type
def map_type(schema: Dict[str, Any], parent_name: str = "") -> str:
    if not schema:
        return "Any"
    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        return ref_name
    
    t = schema.get("type")
    if isinstance(t, list):
        non_null = [x for x in t if x != "null"]
        t = non_null[0] if non_null else "string"
        
    if t == "string":
        if "enum" in schema:
            items = [f"'{x}'" if x is not None else "None" for x in schema["enum"]]
            return f"Literal[{', '.join(items)}]"
        fmt = schema.get("format")
        if fmt == "date":
            return "dt.date"
        if fmt == "date-time":
            return "dt.datetime"
        return "str"
    elif t == "integer":
        return "int"
    elif t == "number":
        return "float"
    elif t == "boolean":
        return "bool"
    elif t == "array":
        items = schema.get("items", {})
        return f"list[{map_type(items, parent_name)}]"
    elif t == "object":
        if "properties" in schema:
            # Inline object. We'll generate a sub-model name for it
            return f"{parent_name}Data" if parent_name else "dict[str, Any]"
        return "dict[str, Any]"
    
    return "Any"

def generate_inline_models(class_name: str, properties: Dict[str, Any], required: List[str], schema_content: List[str]):
    for p_name, p_val in properties.items():
        p_type = p_val.get("type")
        if isinstance(p_type, list):
            non_null = [x for x in p_type if x != "null"]
            p_type = non_null[0] if non_null else "string"
            
        if p_type == "object" and "properties" in p_val:
            sub_class_name = f"{class_name}Data"
            sub_props = p_val.get("properties", {})
            sub_req = p_val.get("required", [])
            
            # Generate nested inline models recursively first
            generate_inline_models(sub_class_name, sub_props, sub_req, schema_content)
            
            # Write this inline class
            schema_content.append(f"class {sub_class_name}(BaseModel):")
            sub_desc = p_val.get("description", "")
            if sub_desc:
                schema_content.append(f'    """{sub_desc}"""')
            if not sub_props:
                schema_content.append("    pass")
            else:
                for sp_name, sp_val in sub_props.items():
                    sp_type = map_type(sp_val, sub_class_name)
                    sp_desc = sp_val.get("description", "")
                    sp_desc_arg = f', description="{escape_desc(sp_desc)}"' if sp_desc else ""
                    if sp_name in sub_req:
                        schema_content.append(f"    {sp_name}: {sp_type} = Field(...{sp_desc_arg})")
                    else:
                        schema_content.append(f"    {sp_name}: {sp_type} | None = Field(default=None{sp_desc_arg})")
            schema_content.append("\n")

# --- GENERATE SCHEMAS (app/schemas.py) ---
# We will do topological sort of schemas to define dependencies first.
deps = {}
for name, val in schemas.items():
    refs = set()
    def find_refs(s):
        if isinstance(s, dict):
            if "$ref" in s:
                refs.add(s["$ref"].split("/")[-1])
            for k, v in s.items():
                find_refs(v)
        elif isinstance(s, list):
            for item in s:
                find_refs(item)
    find_refs(val)
    deps[name] = refs

visited = {}
order = []

def visit(node):
    if node in visited:
        return
    visited[node] = 1
    for dep in deps.get(node, []):
        if dep in schemas:
            visit(dep)
    order.append(node)

for name in schemas:
    visit(name)

# Write app/schemas.py
schema_content = []
schema_content.append("""from __future__ import annotations
import datetime as dt
from enum import Enum
from typing import Literal, Any, Optional
from pydantic import BaseModel, Field, RootModel

# Base class for all schemas
class BaseSchema(BaseModel):
    pass
""")

for name in order:
    val = schemas[name]
    desc = val.get("description", "")
    desc_str = f'    """{desc}"""\n' if desc else ""
    
    # Check if enum
    if "enum" in val:
        schema_content.append(f"class {name}(str, Enum):")
        if desc:
            schema_content.append(f'    """{desc}"""')
        for enum_val in val["enum"]:
            if enum_val is None:
                continue
            if enum_val == "":
                schema_content.append(f'    EMPTY = ""')
            else:
                # convert name to valid uppercase python identifier
                key = enum_val.upper().replace("-", "_").replace(" ", "_")
                schema_content.append(f'    {key} = "{enum_val}"')
        schema_content.append("\n")
        continue
        
    # Parse allOf/properties/parents
    parents = []
    properties = {}
    required = []
    val_type = val.get("type")
    
    if "allOf" in val:
        for sub in val["allOf"]:
            if "$ref" in sub:
                parents.append(sub["$ref"].split("/")[-1])
            else:
                properties.update(sub.get("properties", {}))
                required.extend(sub.get("required", []))
        val_type = "object"
    else:
        if isinstance(val_type, list):
            non_null = [x for x in val_type if x != "null"]
            val_type = non_null[0] if non_null else "object"
        properties = val.get("properties", {})
        required = val.get("required", [])
    
    # Check if additionalProperties without properties
    if "additionalProperties" in val and not properties:
        add_prop = val["additionalProperties"]
        add_type = map_type(add_prop, name)
        schema_content.append(f"class {name}(RootModel[dict[str, {add_type}]]):")
        if desc:
            schema_content.append(f'    """{desc}"""')
        schema_content.append("    pass\n")
        continue
        
    # Check if primitive type alias (like string with no properties)
    if val_type in ["string", "integer", "number", "boolean"] and not properties:
        p_type = map_type(val, name)
        schema_content.append(f"class {name}(RootModel[{p_type}]):")
        if desc:
            schema_content.append(f'    """{desc}"""')
        schema_content.append("    pass\n")
        continue

    # Check if object
    if val_type == "object" or properties:
        # Generate inline models recursively
        generate_inline_models(name, properties, required, schema_content)
            
        # Generate the main class
        parent_str = ", ".join(parents) if parents else "BaseModel"
        schema_content.append(f"class {name}({parent_str}):")
        if desc:
            schema_content.append(f'    """{desc}"""')
            
        if not properties:
            schema_content.append("    pass")
        else:
            for p_name, p_val in properties.items():
                p_type = map_type(p_val, name)
                p_desc = p_val.get("description", "")
                p_desc_arg = f', description="{escape_desc(p_desc)}"' if p_desc else ""
                
                if p_name in required:
                    schema_content.append(f"    {p_name}: {p_type} = Field(...{p_desc_arg})")
                else:
                    schema_content.append(f"    {p_name}: {p_type} | None = Field(default=None{p_desc_arg})")
        schema_content.append("\n")

# Rebuild all models to resolve forward references
schema_content.append("# Rebuild all models to resolve forward references")
for name in order:
    if name not in schemas:
        continue
    val = schemas[name]
    schema_content.append(f"try:")
    
    # We should get properties of the schema, including allOf properties!
    properties = {}
    if "allOf" in val:
        for sub in val["allOf"]:
            if "$ref" not in sub:
                properties.update(sub.get("properties", {}))
    else:
        properties = val.get("properties", {})
        
    # Rebuild nested inline models recursively if any
    def add_rebuilds(class_name, props):
        for p_name, p_val in props.items():
            p_type = p_val.get("type")
            if isinstance(p_type, list):
                non_null = [x for x in p_type if x != "null"]
                p_type = non_null[0] if non_null else "string"
            if p_type == "object" and "properties" in p_val:
                sub_class_name = f"{class_name}Data"
                add_rebuilds(sub_class_name, p_val.get("properties", {}))
                schema_content.append(f"    {sub_class_name}.model_rebuild()")
                
    add_rebuilds(name, properties)
    schema_content.append(f"    {name}.model_rebuild()")
    schema_content.append(f"except AttributeError:")
    schema_content.append(f"    pass")

with open("app/schemas.py", "w") as f:
    f.write("\n".join(schema_content))

print("Generated app/schemas.py")

# --- GENERATE CORE DECORATORS (app/core/decorators.py) ---
decorators_content = """from typing import Type, Any, List, Dict, Optional
from fastapi import APIRouter

class EndpointRegistry:
    def __init__(self):
        self.endpoints = []

    def register(
        self,
        path: str,
        method: str,
        response_model: Any = None,
        responses: Optional[Dict[int, Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status_code: int = 200,
    ):
        def decorator(cls: Type):
            self.endpoints.append({
                "cls": cls,
                "path": path,
                "method": method.upper(),
                "response_model": response_model,
                "responses": responses,
                "tags": tags,
                "summary": summary,
                "description": description,
                "status_code": status_code,
            })
            return cls
        return decorator

registry = EndpointRegistry()
endpoint = registry.register
"""
with open("app/core/decorators.py", "w") as f:
    f.write(decorators_content)

print("Generated app/core/decorators.py")

# --- GENERATE MOCK STATE (app/core/state.py) ---
state_content = """import uuid
from datetime import date, datetime
from app.schemas import *

class MockState:
    def __init__(self):
        self.reset()

    def reset(self):
        # Initial user
        self.user = User(id="user_12345")
        
        # Initial plans
        self.plans = [
            PlanSummary(
                id="plan_default",
                name="My Personal Plan",
                last_modified_on=datetime.now(),
                first_month=date(2026, 1, 1),
                last_month=date(2026, 12, 1),
                currency_format=CurrencyFormat(
                    iso_code="USD",
                    example_format="$1,000.00",
                    decimal_digits=2,
                    decimal_separator=".",
                    symbol_first=True,
                    group_separator=",",
                    currency_symbol="$",
                    display_symbol=True
                ),
                date_format=DateFormat(format="YYYY-MM-DD")
            )
        ]
        
        # Accounts map: plan_id -> list of Account
        self.accounts = {
            "plan_default": [
                Account(
                    id="account_1",
                    name="Checking Account",
                    type="checking",
                    on_budget=True,
                    closed=False,
                    note="Primary checking",
                    balance=5000000, # 5000 in milliunits
                    cleared_balance=5000000,
                    uncleared_balance=0,
                    transfer_payee_id="payee_transfer_1",
                    deleted=False
                )
            ]
        }
        
        # Categories map: plan_id -> list of Category
        self.categories = {
            "plan_default": [
                Category(
                    id="category_1",
                    category_group_id="group_1",
                    category_group_name="Immediate Obligations",
                    name="Rent",
                    hidden=False,
                    internal=False,
                    original_category_group_id=None,
                    note="Monthly rent payment",
                    budgeted=1000000,
                    activity=-1000000,
                    balance=0,
                    goal_type=None,
                    goal_needs_whole_amount=None,
                    goal_day=None,
                    goal_months_to_accumulate=None,
                    goal_target=None,
                    goal_target_month=None,
                    goal_percentage_complete=None,
                    goal_under_funded_amount=None,
                    goal_overall_left=None,
                    goal_overall_funded_amount=None,
                    goal_cadence=None,
                    goal_cadence_frequency=None,
                    deleted=False
                )
            ]
        }
        
        # Category Groups map: plan_id -> list of CategoryGroupWithCategories
        self.category_groups = {
            "plan_default": [
                CategoryGroupWithCategories(
                    id="group_1",
                    name="Immediate Obligations",
                    hidden=False,
                    internal=False,
                    deleted=False,
                    categories=self.categories["plan_default"]
                )
            ]
        }
        
        # Payees map: plan_id -> list of Payee
        self.payees = {
            "plan_default": [
                Payee(
                    id="payee_1",
                    name="Landlord",
                    transfer_account_id=None,
                    deleted=False
                )
            ]
        }
        
        # Payee Locations map: plan_id -> list of PayeeLocation
        self.payee_locations = {
            "plan_default": [
                PayeeLocation(
                    id="loc_1",
                    payee_id="payee_1",
                    latitude="40.7128",
                    longitude="-74.0060",
                    deleted=False
                )
            ]
        }
        
        # Months map: plan_id -> list of MonthDetail
        self.months = {
            "plan_default": [
                MonthDetail(
                    month=date(2026, 6, 1),
                    note="June 2026",
                    income=6000000,
                    budgeted=5000000,
                    activity=-4000000,
                    to_be_budgeted=1000000,
                    age_of_money=15,
                    deleted=False,
                    categories=self.categories["plan_default"]
                )
            ]
        }
        
        # Money movements map: plan_id -> list of MoneyMovement
        self.money_movements = {
            "plan_default": [
                MoneyMovement(
                    id="movement_1",
                    created_at=datetime.now(),
                    amount=50000,
                    deleted=False,
                    source_category_id="category_1",
                    destination_category_id="category_1"
                )
            ]
        }
        
        # Money movement groups map: plan_id -> list of MoneyMovementGroup
        self.money_movement_groups = {
            "plan_default": []
        }
        
        # Transactions map: plan_id -> list of TransactionDetail
        self.transactions = {
            "plan_default": [
                TransactionDetail(
                    id="tx_1",
                    date=date(2026, 6, 1),
                    amount=-1000000,
                    memo="Rent Payment",
                    cleared="cleared",
                    approved=True,
                    flag_color=None,
                    account_id="account_1",
                    account_name="Checking Account",
                    payee_id="payee_1",
                    payee_name="Landlord",
                    category_id="category_1",
                    category_name="Rent",
                    transfer_account_id=None,
                    transfer_transaction_id=None,
                    matched_transaction_id=None,
                    import_id=None,
                    deleted=False,
                    subtransactions=[],
                    debt_transaction_type=None
                )
            ]
        }
        
        # Scheduled Transactions map: plan_id -> list of ScheduledTransactionDetail
        self.scheduled_transactions = {
            "plan_default": [
                ScheduledTransactionDetail(
                    id="sch_1",
                    date_next=date(2026, 7, 1),
                    date_first=date(2026, 6, 1),
                    frequency="monthly",
                    amount=-1000000,
                    memo="Next Rent Payment",
                    flag_color=None,
                    account_id="account_1",
                    account_name="Checking Account",
                    payee_id="payee_1",
                    payee_name="Landlord",
                    category_id="category_1",
                    category_name="Rent",
                    transfer_account_id=None,
                    deleted=False,
                    subtransactions=[]
                )
            ]
        }

    # Helper accessors
    def get_plan_detail(self, plan_id: str) -> PlanDetail:
        for plan in self.plans:
            if plan.id == plan_id or plan_id in ("default", "last-used"):
                pid = plan.id
                
                # Convert Account to AccountBase
                accounts_base = [AccountBase(**acc.model_dump()) for acc in self.accounts.get(pid, [])]
                
                # Convert CategoryGroupWithCategories to CategoryGroup
                groups_base = [CategoryGroup(
                    id=g.id,
                    name=g.name,
                    hidden=g.hidden,
                    internal=g.internal,
                    deleted=g.deleted
                ) for g in self.category_groups.get(pid, [])]
                
                # Convert Category to CategoryBase
                cats_base = [CategoryBase(**cat.model_dump()) for cat in self.categories.get(pid, [])]
                
                # Convert MonthDetail to MonthDetailBase
                months_base = [MonthDetailBase(
                    month=m.month,
                    note=m.note,
                    income=m.income,
                    budgeted=m.budgeted,
                    activity=m.activity,
                    to_be_budgeted=m.to_be_budgeted,
                    age_of_money=m.age_of_money,
                    deleted=m.deleted,
                    categories=[CategoryBase(**c.model_dump()) for c in m.categories]
                ) for m in self.months.get(pid, [])]
                
                # Convert TransactionDetail to TransactionSummaryBase
                txs_base = [TransactionSummaryBase(**tx.model_dump()) for tx in self.transactions.get(pid, [])]
                
                # Convert ScheduledTransactionDetail to ScheduledTransactionSummaryBase
                stxs_base = [ScheduledTransactionSummaryBase(
                    id=s.id,
                    date_first=s.date_first,
                    date_next=s.date_next,
                    frequency=s.frequency,
                    amount=s.amount,
                    memo=s.memo,
                    flag_color=s.flag_color,
                    account_id=s.account_id,
                    payee_id=s.payee_id,
                    category_id=s.category_id,
                    transfer_account_id=s.transfer_account_id,
                    deleted=s.deleted
                ) for s in self.scheduled_transactions.get(pid, [])]
                
                return PlanDetail(
                    id=plan.id,
                    name=plan.name,
                    last_modified_on=plan.last_modified_on,
                    first_month=plan.first_month,
                    last_month=plan.last_month,
                    currency_format=plan.currency_format,
                    date_format=plan.date_format,
                    accounts=accounts_base,
                    payees=self.payees.get(pid, []),
                    payee_locations=self.payee_locations.get(pid, []),
                    category_groups=groups_base,
                    categories=cats_base,
                    months=months_base,
                    transactions=txs_base,
                    subtransactions=[],
                    scheduled_transactions=stxs_base,
                    scheduled_subtransactions=[]
                )
        raise KeyError("Plan not found")

    def get_plan_settings(self, plan_id: str) -> PlanSettings:
        for plan in self.plans:
            if plan.id == plan_id or plan_id in ("default", "last-used"):
                return PlanSettings(
                    currency_format=plan.currency_format,
                    date_format=plan.date_format
                )
        raise KeyError("Plan not found")

    def get_accounts(self, plan_id: str) -> list[Account]:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        return self.accounts.get(pid, [])

    def get_account(self, plan_id: str, account_id: str) -> Account:
        for acc in self.get_accounts(plan_id):
            if acc.id == account_id:
                return acc
        raise KeyError("Account not found")

    def create_account(self, plan_id: str, account: Account) -> Account:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        if pid not in self.accounts:
            self.accounts[pid] = []
        self.accounts[pid].append(account)
        return account

    def get_category_groups(self, plan_id: str) -> list[CategoryGroupWithCategories]:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        return self.category_groups.get(pid, [])

    def get_category(self, plan_id: str, category_id: str) -> Category:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        for cat in self.categories.get(pid, []):
            if cat.id == category_id:
                return cat
        raise KeyError("Category not found")

    def create_category(self, plan_id: str, category: Category) -> Category:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        if pid not in self.categories:
            self.categories[pid] = []
        self.categories[pid].append(category)
        return category

    def update_category(self, plan_id: str, category_id: str, updates: dict) -> Category:
        cat = self.get_category(plan_id, category_id)
        for k, v in updates.items():
            if hasattr(cat, k):
                setattr(cat, k, v)
        return cat

    def get_payees(self, plan_id: str) -> list[Payee]:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        return self.payees.get(pid, [])

    def get_payee(self, plan_id: str, payee_id: str) -> Payee:
        for payee in self.get_payees(plan_id):
            if payee.id == payee_id:
                return payee
        raise KeyError("Payee not found")

    def create_payee(self, plan_id: str, payee: Payee) -> Payee:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        if pid not in self.payees:
            self.payees[pid] = []
        self.payees[pid].append(payee)
        return payee

    def update_payee(self, plan_id: str, payee_id: str, updates: dict) -> Payee:
        payee = self.get_payee(plan_id, payee_id)
        for k, v in updates.items():
            if hasattr(payee, k):
                setattr(payee, k, v)
        return payee

    def get_payee_locations(self, plan_id: str) -> list[PayeeLocation]:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        return self.payee_locations.get(pid, [])

    def get_payee_location(self, plan_id: str, loc_id: str) -> PayeeLocation:
        for loc in self.get_payee_locations(plan_id):
            if loc.id == loc_id:
                return loc
        raise KeyError("Payee Location not found")

    def get_months(self, plan_id: str) -> list[MonthSummary]:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        return [MonthSummary(
            month=m.month,
            note=m.note,
            income=m.income,
            budgeted=m.budgeted,
            activity=m.activity,
            to_be_budgeted=m.to_be_budgeted,
            age_of_money=m.age_of_money,
            deleted=m.deleted
        ) for m in self.months.get(pid, [])]

    def get_month(self, plan_id: str, month: date) -> MonthDetail:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        for m in self.months.get(pid, []):
            if m.month == month or m.month.strftime("%Y-%m-%d") == str(month):
                return m
        raise KeyError("Month not found")

    def get_money_movements(self, plan_id: str) -> list[MoneyMovement]:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        return self.money_movements.get(pid, [])

    def get_transactions(self, plan_id: str) -> list[TransactionDetail]:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        return self.transactions.get(pid, [])

    def get_transaction(self, plan_id: str, tx_id: str) -> TransactionDetail:
        for tx in self.get_transactions(plan_id):
            if tx.id == tx_id:
                return tx
        raise KeyError("Transaction not found")

    def create_transaction(self, plan_id: str, tx: TransactionDetail) -> TransactionDetail:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        if pid not in self.transactions:
            self.transactions[pid] = []
        self.transactions[pid].append(tx)
        return tx

    def delete_transaction(self, plan_id: str, tx_id: str) -> TransactionDetail:
        tx = self.get_transaction(plan_id, tx_id)
        tx.deleted = True
        return tx

    def get_scheduled_transactions(self, plan_id: str) -> list[ScheduledTransactionDetail]:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        return self.scheduled_transactions.get(pid, [])

    def get_scheduled_transaction(self, plan_id: str, stx_id: str) -> ScheduledTransactionDetail:
        for stx in self.get_scheduled_transactions(plan_id):
            if stx.id == stx_id:
                return stx
        raise KeyError("Scheduled transaction not found")

    def create_scheduled_transaction(self, plan_id: str, stx: ScheduledTransactionDetail) -> ScheduledTransactionDetail:
        pid = "plan_default" if plan_id in ("default", "last-used") else plan_id
        if pid not in self.scheduled_transactions:
            self.scheduled_transactions[pid] = []
        self.scheduled_transactions[pid].append(stx)
        return stx

    def delete_scheduled_transaction(self, plan_id: str, stx_id: str) -> ScheduledTransactionDetail:
        stx = self.get_scheduled_transaction(plan_id, stx_id)
        stx.deleted = True
        return stx

state = MockState()
"""
with open("app/core/state.py", "w") as f:
    f.write(state_content)

print("Generated app/core/state.py")

# --- GENERATE ENDPOINTS & TESTS ---
endpoint_modules = []
test_cases = []

test_cases.append("""import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.state import state

@pytest.fixture(autouse=True)
def run_around_tests():
    state.reset()
    yield

client = TestClient(app)
""")

for path_str, path_item in paths.items():
    for method_str, op_val in path_item.items():
        if method_str not in ["get", "post", "put", "delete", "patch"]:
            continue
            
        op_id = op_val.get("operationId")
        if not op_id:
            continue
            
        filename = camel_to_snake(op_id)
        classname = op_id[0].upper() + op_id[1:]
        endpoint_modules.append(filename)
        
        # Determine Success Response Schema
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
            mock_body = """try:
            return PlanDetailResponse(data=PlanDetailResponseData(plan=state.get_plan_detail(plan_id), server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Plan not found")"""
        elif resp_schema_name == "PlanSettingsResponse":
            mock_body = """try:
            return PlanSettingsResponse(data=PlanSettingsResponseData(settings=state.get_plan_settings(plan_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Plan not found")"""
        elif resp_schema_name == "AccountsResponse":
            mock_body = "return AccountsResponse(data=AccountsResponseData(accounts=state.get_accounts(plan_id), server_knowledge=100))"
        elif resp_schema_name == "AccountResponse":
            if method_str == "post":
                # Create Account
                mock_body = """import uuid
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
            transfer_payee_id=f"payee_transfer_{uuid.uuid4().hex[:6]}",
            deleted=False
        )
        state.create_account(plan_id, acc)
        return AccountResponse(data=AccountResponseData(account=acc))"""
            else:
                # Get Account
                mock_body = """try:
            return AccountResponse(data=AccountResponseData(account=state.get_account(plan_id, account_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Account not found")"""
        elif resp_schema_name == "CategoriesResponse":
            mock_body = "return CategoriesResponse(data=CategoriesResponseData(category_groups=state.get_category_groups(plan_id), server_knowledge=100))"
        elif resp_schema_name == "CategoryResponse":
            if method_str == "post":
                mock_body = """import uuid
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
        return CategoryResponse(data=CategoryResponseData(category=cat))"""
            else:
                # Get Category
                mock_body = """try:
            return CategoryResponse(data=CategoryResponseData(category=state.get_category(plan_id, category_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Category not found")"""
        elif resp_schema_name == "SaveCategoryResponse":
            if method_str == "post":
                # Create category (POST /plans/{plan_id}/categories) returns SaveCategoryResponse
                mock_body = """import uuid
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
        return SaveCategoryResponse(data=SaveCategoryResponseData(category=cat, server_knowledge=100))"""
            else:
                # Update Category or Update Month Category
                mock_body = """try:
            updates = body.category.model_dump()
            cat = state.update_category(plan_id, category_id, updates)
            return SaveCategoryResponse(data=SaveCategoryResponseData(category=cat, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Category not found")"""
        elif resp_schema_name == "SaveCategoryGroupResponse":
            if method_str == "post":
                # Create category group
                mock_body = """import uuid
        group = CategoryGroupWithCategories(
            id=f"group_{uuid.uuid4().hex[:6]}",
            name=body.category_group.name,
            hidden=False,
            internal=False,
            deleted=False,
            categories=[]
        )
        state.category_groups.setdefault(plan_id, []).append(group)
        return SaveCategoryGroupResponse(data=SaveCategoryGroupResponseData(category_group=group, server_knowledge=100))"""
            else:
                # Update Category Group
                mock_body = """groups = state.get_category_groups(plan_id)
        for g in groups:
            if g.id == category_group_id:
                if body.category_group.name:
                    g.name = body.category_group.name
                return SaveCategoryGroupResponse(data=SaveCategoryGroupResponseData(category_group=g, server_knowledge=100))
        raise HTTPException(status_code=404, detail="Category group not found")"""
        elif resp_schema_name == "PayeesResponse":
            mock_body = "return PayeesResponse(data=PayeesResponseData(payees=state.get_payees(plan_id), server_knowledge=100))"
        elif resp_schema_name == "PayeeResponse":
            if method_str == "post":
                mock_body = """import uuid
        payee = Payee(
            id=f"payee_{uuid.uuid4().hex[:6]}",
            name=body.payee.name,
            transfer_account_id=None,
            deleted=False
        )
        state.create_payee(plan_id, payee)
        return PayeeResponse(data=PayeeResponseData(payee=payee))"""
            else:
                mock_body = """try:
            return PayeeResponse(data=PayeeResponseData(payee=state.get_payee(plan_id, payee_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Payee not found")"""
        elif resp_schema_name == "SavePayeeResponse":
            if method_str == "post":
                # Create payee
                mock_body = """import uuid
        payee = Payee(
            id=f"payee_{uuid.uuid4().hex[:6]}",
            name=body.payee.name,
            transfer_account_id=None,
            deleted=False
        )
        state.create_payee(plan_id, payee)
        return SavePayeeResponse(data=SavePayeeResponseData(payee=payee, server_knowledge=100))"""
            else:
                # Update payee
                mock_body = """try:
            updates = body.payee.model_dump()
            payee = state.update_payee(plan_id, payee_id, updates)
            return SavePayeeResponse(data=SavePayeeResponseData(payee=payee, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Payee not found")"""
        elif resp_schema_name == "PayeeLocationsResponse":
            mock_body = "return PayeeLocationsResponse(data=PayeeLocationsResponseData(payee_locations=state.get_payee_locations(plan_id), server_knowledge=100))"
        elif resp_schema_name == "PayeeLocationResponse":
            mock_body = """try:
            return PayeeLocationResponse(data=PayeeLocationResponseData(payee_location=state.get_payee_location(plan_id, payee_location_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Payee Location not found")"""
        elif resp_schema_name == "MonthSummariesResponse":
            mock_body = "return MonthSummariesResponse(data=MonthSummariesResponseData(months=state.get_months(plan_id), server_knowledge=100))"
        elif resp_schema_name == "MonthDetailResponse":
            mock_body = """try:
            # Parse month date
            from datetime import datetime
            parsed_month = datetime.strptime(str(month), "%Y-%m-%d").date()
            return MonthDetailResponse(data=MonthDetailResponseData(month=state.get_month(plan_id, parsed_month), server_knowledge=100))
        except Exception:
            raise HTTPException(status_code=404, detail="Month not found")"""
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
                mock_body = """try:
            tx = state.get_transaction(plan_id, transaction_id)
            for k, v in body.transaction.model_dump().items():
                if hasattr(tx, k) and v is not None:
                    setattr(tx, k, v)
            return TransactionResponse(data=TransactionResponseData(transaction=tx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Transaction not found")"""
            elif method_str == "delete":
                # Delete Transaction
                mock_body = """try:
            tx = state.delete_transaction(plan_id, transaction_id)
            return TransactionResponse(data=TransactionResponseData(transaction=tx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Transaction not found")"""
            else:
                # Get Transaction
                mock_body = """try:
            return TransactionResponse(data=TransactionResponseData(transaction=state.get_transaction(plan_id, transaction_id), server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Transaction not found")"""
        elif resp_schema_name == "SaveTransactionsResponse":
            if method_str == "patch":
                mock_body = """import uuid
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
        )"""
            else:
                # Create transactions (Bulk/Multi)
                mock_body = """import uuid
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
        )"""
        elif resp_schema_name == "TransactionsImportResponse":
            mock_body = "return TransactionsImportResponse(data=TransactionsImportResponseData(transaction_ids=[]))"
        elif resp_schema_name == "BulkResponse":
            mock_body = "return BulkResponse(data=BulkResponseData(bulk=BulkTransactions(transaction_ids=[], duplicate_import_ids=[])))"
        elif resp_schema_name == "ScheduledTransactionsResponse":
            mock_body = "return ScheduledTransactionsResponse(data=ScheduledTransactionsResponseData(scheduled_transactions=state.get_scheduled_transactions(plan_id), server_knowledge=100))"
        elif resp_schema_name == "ScheduledTransactionResponse":
            if method_str == "put":
                # Update scheduled tx
                mock_body = """try:
            stx = state.get_scheduled_transaction(plan_id, scheduled_transaction_id)
            for k, v in body.scheduled_transaction.model_dump().items():
                if hasattr(stx, k) and v is not None:
                    setattr(stx, k, v)
            return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=stx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Scheduled Transaction not found")"""
            elif method_str == "delete":
                # Delete scheduled tx
                mock_body = """try:
            stx = state.delete_scheduled_transaction(plan_id, scheduled_transaction_id)
            return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=stx, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Scheduled Transaction not found")"""
            elif method_str == "post":
                # Create scheduled tx
                mock_body = """import uuid
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
        return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=stx, server_knowledge=100))"""
            else:
                # Get scheduled tx
                mock_body = """try:
            return ScheduledTransactionResponse(data=ScheduledTransactionResponseData(scheduled_transaction=state.get_scheduled_transaction(plan_id, scheduled_transaction_id), server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Scheduled Transaction not found")"""
        else:
            mock_body = "return {}"
            
        endpoint_file_content = f"""import datetime as dt
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
    summary="{escape_desc(summary)}",
    description="{escape_desc(description)}",
    status_code={success_code}
)
class {classname}:
    @override
    def __call__({sig_str}) -> {resp_schema_name}:
        {mock_body}
"""
        with open(f"app/endpoints/{filename}.py", "w") as f_ep:
            f_ep.write(endpoint_file_content)
            
        # Create Test Case for this endpoint
        test_path = path_str.replace("{plan_id}", "plan_default")                             .replace("{account_id}", "account_1")                             .replace("{category_id}", "category_1")                             .replace("{category_group_id}", "group_1")                             .replace("{payee_id}", "payee_1")                             .replace("{payee_location_id}", "loc_1")                             .replace("{month}", "2026-06-01")                             .replace("{transaction_id}", "tx_1")                             .replace("{scheduled_transaction_id}", "sch_1")
                            
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
                
        test_case_code = f"""
def test_{filename}():
    {test_setup.strip()}
    response = client.{method_str}("/v1{test_path}"{req_kwargs})
    assert response.status_code == {success_code}
    data = response.json()
    assert "data" in data
"""
        test_cases.append(test_case_code)
# Write app/endpoints/__init__.py
with open("app/endpoints/__init__.py", "w") as f:
    for filename in sorted(endpoint_modules):
        f.write(f"from app.endpoints import {filename}\n")

# Write tests/test_endpoints.py
with open("tests/test_endpoints.py", "w") as f:
    f.write("\n".join(test_cases))

print("Generated app/endpoints/__init__.py and tests/test_endpoints.py")

# --- GENERATE app/main.py ---
main_content = """from fastapi import FastAPI
from app.core.decorators import registry
import app.endpoints  # Load all endpoints to register them

app = FastAPI(
    title="YNAB API Mock Server",
    description="A complete mock implementation of the YNAB API spec",
    version="1.85.0"
)

# Register all routes from decorator registry
for ep in registry.endpoints:
    cls = ep["cls"]
    # Instantiate class to use as route callable
    handler = cls()
    app.add_api_route(
        path=f"/v1{ep['path']}",
        endpoint=handler,
        methods=[ep["method"]],
        response_model=ep["response_model"],
        responses=ep["responses"],
        tags=ep["tags"],
        summary=ep["summary"],
        description=ep["description"],
        status_code=ep["status_code"]
    )
"""
with open("app/main.py", "w") as f:
    f.write(main_content)

print("Generated app/main.py")
