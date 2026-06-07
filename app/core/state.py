import uuid
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
