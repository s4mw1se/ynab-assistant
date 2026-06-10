with open("scratch/generator.py") as f:
    content = f.read()

# 1. Replace the state imports block
start_imp = content.find('state_content = """import uuid')
end_imp = content.find('class MockState:')
if start_imp == -1 or end_imp == -1:
    print("Error: Import markers not found!")
    exit(1)

new_imp_block = """state_content = \"\"\"import uuid
from datetime import date, datetime
from app.schemas import *

"""
content = content[:start_imp] + new_imp_block + content[end_imp:]

# 2. Replace the get_plan_detail method
start_gpd = content.find("    def get_plan_detail(self, plan_id: str) -> PlanDetail:")
end_gpd = content.find("    def get_plan_settings(self, plan_id: str) -> PlanSettings:")
if start_gpd == -1 or end_gpd == -1:
    print("Error: get_plan_detail markers not found!")
    exit(1)

new_gpd_block = """    def get_plan_detail(self, plan_id: str) -> PlanDetail:
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

"""

content = content[:start_gpd] + new_gpd_block + content[end_gpd:]

with open("scratch/generator.py", "w") as f:
    f.write(content)

print("Generator updated successfully (pass 2)!")
