from __future__ import annotations
import datetime as dt
from enum import Enum
from typing import Literal, Any, Optional
from pydantic import BaseModel, Field, RootModel

# Base class for all schemas
class BaseSchema(BaseModel):
    pass

class ErrorDetail(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    detail: str = Field(...)


class ErrorResponse(BaseModel):
    error: ErrorDetail = Field(...)


class User(BaseModel):
    id: str = Field(...)


class UserResponseData(BaseModel):
    user: User = Field(...)


class UserResponse(BaseModel):
    data: UserResponseData = Field(...)


class DateFormat(BaseModel):
    """The date format setting for the plan.  In some cases the format will not be available and will be specified as null."""
    format: str = Field(...)


class CurrencyFormat(BaseModel):
    """The currency format setting for the plan.  In some cases the format will not be available and will be specified as null."""
    iso_code: str = Field(...)
    example_format: str = Field(...)
    decimal_digits: int = Field(...)
    decimal_separator: str = Field(...)
    symbol_first: bool = Field(...)
    group_separator: str = Field(...)
    currency_symbol: str = Field(...)
    display_symbol: bool = Field(...)


class AccountType(str, Enum):
    """The type of account"""
    CHECKING = "checking"
    SAVINGS = "savings"
    CASH = "cash"
    CREDITCARD = "creditCard"
    LINEOFCREDIT = "lineOfCredit"
    OTHERASSET = "otherAsset"
    OTHERLIABILITY = "otherLiability"
    MORTGAGE = "mortgage"
    AUTOLOAN = "autoLoan"
    STUDENTLOAN = "studentLoan"
    PERSONALLOAN = "personalLoan"
    MEDICALDEBT = "medicalDebt"
    OTHERDEBT = "otherDebt"


class LoanAccountPeriodicValue(RootModel[dict[str, int]]):
    pass

class AccountBase(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    type: AccountType = Field(...)
    on_budget: bool = Field(..., description="Whether this account is \"on budget\" or not")
    closed: bool = Field(..., description="Whether this account is closed or not")
    note: str | None = Field(default=None)
    balance: int = Field(..., description="The current available balance of the account in milliunits format")
    cleared_balance: int = Field(..., description="The current cleared balance of the account in milliunits format")
    uncleared_balance: int = Field(..., description="The current uncleared balance of the account in milliunits format")
    transfer_payee_id: str = Field(..., description="The payee id which should be used when transferring to this account")
    direct_import_linked: bool | None = Field(default=None, description="Whether or not the account is linked to a financial institution for automatic transaction import.")
    direct_import_in_error: bool | None = Field(default=None, description="If an account linked to a financial institution (direct_import_linked=true) and the linked connection is not in a healthy state, this will be true.")
    last_reconciled_at: dt.datetime | None = Field(default=None, description="A date/time specifying when the account was last reconciled.")
    debt_original_balance: int | None = Field(default=None, description="This field is deprecated and will always be null.")
    debt_interest_rates: LoanAccountPeriodicValue | None = Field(default=None)
    debt_minimum_payments: LoanAccountPeriodicValue | None = Field(default=None)
    debt_escrow_amounts: LoanAccountPeriodicValue | None = Field(default=None)
    deleted: bool = Field(..., description="Whether or not the account has been deleted.  Deleted accounts will only be included in delta requests.")


class Account(AccountBase):
    balance_formatted: str | None = Field(default=None, description="The current available balance of the account formatted in the plan's currency format")
    balance_currency: float | None = Field(default=None, description="The current available balance of the account as a decimal currency amount")
    cleared_balance_formatted: str | None = Field(default=None, description="The current cleared balance of the account formatted in the plan's currency format")
    cleared_balance_currency: float | None = Field(default=None, description="The current cleared balance of the account as a decimal currency amount")
    uncleared_balance_formatted: str | None = Field(default=None, description="The current uncleared balance of the account formatted in the plan's currency format")
    uncleared_balance_currency: float | None = Field(default=None, description="The current uncleared balance of the account as a decimal currency amount")


class PlanSummary(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    last_modified_on: dt.datetime | None = Field(default=None, description="The last time any changes were made to the plan from either a web or mobile client")
    first_month: dt.date | None = Field(default=None, description="The earliest plan month")
    last_month: dt.date | None = Field(default=None, description="The latest plan month")
    date_format: DateFormat | None = Field(default=None)
    currency_format: CurrencyFormat | None = Field(default=None)
    accounts: list[Account] | None = Field(default=None, description="The plan accounts (only included if `include_accounts=true` specified as query parameter)")


class PlanSummaryResponseData(BaseModel):
    plans: list[PlanSummary] = Field(...)
    default_plan: Any | None = Field(default=None)


class PlanSummaryResponse(BaseModel):
    data: PlanSummaryResponseData = Field(...)


class PayeeLocation(BaseModel):
    id: str = Field(...)
    payee_id: str = Field(...)
    latitude: str = Field(...)
    longitude: str = Field(...)
    deleted: bool = Field(..., description="Whether or not the payee location has been deleted.  Deleted payee locations will only be included in delta requests.")


class TransactionFlagName(RootModel[str]):
    """The customized name of a transaction flag"""
    pass

class TransactionFlagColor(str, Enum):
    """The transaction flag"""
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    EMPTY = ""


class ScheduledTransactionSummaryBase(BaseModel):
    id: str = Field(...)
    date_first: dt.date = Field(..., description="The first date for which the Scheduled Transaction was scheduled.")
    date_next: dt.date = Field(..., description="The next date for which the Scheduled Transaction is scheduled.")
    frequency: Literal['never', 'daily', 'weekly', 'everyOtherWeek', 'twiceAMonth', 'every4Weeks', 'monthly', 'everyOtherMonth', 'every3Months', 'every4Months', 'twiceAYear', 'yearly', 'everyOtherYear'] = Field(...)
    amount: int = Field(..., description="The scheduled transaction amount in milliunits format")
    memo: str | None = Field(default=None)
    flag_color: TransactionFlagColor | None = Field(default=None)
    flag_name: TransactionFlagName | None = Field(default=None)
    account_id: str = Field(...)
    payee_id: str | None = Field(default=None)
    category_id: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None, description="If a transfer, the account_id which the scheduled transaction transfers to")
    deleted: bool = Field(..., description="Whether or not the scheduled transaction has been deleted.  Deleted scheduled transactions will only be included in delta requests.")


class CategoryBase(BaseModel):
    id: str = Field(...)
    category_group_id: str = Field(...)
    category_group_name: str | None = Field(default=None)
    name: str = Field(...)
    hidden: bool = Field(..., description="Whether or not the category is hidden")
    internal: bool = Field(..., description="Whether or not the category is internal")
    original_category_group_id: str | None = Field(default=None, description="DEPRECATED: No longer used.  Value will always be null.")
    note: str | None = Field(default=None)
    budgeted: int = Field(..., description="Assigned (budgeted) amount in milliunits format")
    activity: int = Field(..., description="Activity amount in milliunits format")
    balance: int = Field(..., description="Available balance in milliunits format")
    goal_type: Literal['TB', 'TBD', 'MF', 'NEED', 'DEBT', None] | None = Field(default=None, description="The type of goal, if the category has a goal (TB='Target Category Balance', TBD='Target Category Balance by Date', MF='Monthly Funding', NEED='Plan Your Spending')")
    goal_needs_whole_amount: bool | None = Field(default=None, description="Indicates the monthly rollover behavior for \"NEED\"-type goals. When \"true\", the goal will always ask for the target amount in the new month (\"Set Aside\"). When \"false\", previous month category funding is used (\"Refill\"). For other goal types, this field will be null.")
    goal_day: int | None = Field(default=None, description="A day offset modifier for the goal's due date. When goal_cadence is 2 (Weekly), this value specifies which day of the week the goal is due (0 = Sunday, 6 = Saturday). Otherwise, this value specifies which day of the month the goal is due (1 = 1st, 31 = 31st, null = Last day of Month).")
    goal_cadence: int | None = Field(default=None, description="The goal cadence. Value in range 0-14. There are two subsets of these values which behave differently. For values 0, 1, 2, and 13, the goal's due date repeats every goal_cadence * goal_cadence_frequency, where 0 = None, 1 = Monthly, 2 = Weekly, and 13 = Yearly. For example, goal_cadence 1 with goal_cadence_frequency 2 means the goal is due every other month. For values 3-12 and 14, goal_cadence_frequency is ignored and the goal's due date repeats every goal_cadence, where 3 = Every 2 Months, 4 = Every 3 Months, ..., 12 = Every 11 Months, and 14 = Every 2 Years.")
    goal_cadence_frequency: int | None = Field(default=None, description="The goal cadence frequency. When goal_cadence is 0, 1, 2, or 13, a goal's due date repeats every goal_cadence * goal_cadence_frequency. For example, goal_cadence 1 with goal_cadence_frequency 2 means the goal is due every other month.  When goal_cadence is 3-12 or 14, goal_cadence_frequency is ignored.")
    goal_creation_month: dt.date | None = Field(default=None, description="The month a goal was created")
    goal_target: int | None = Field(default=None, description="The goal target amount in milliunits")
    goal_target_month: dt.date | None = Field(default=None, description="DEPRECATED: No longer used.  Use `goal_target_date` instead.")
    goal_target_date: dt.date | None = Field(default=None, description="The target date for the goal to be completed.  Only some goal types specify this date.")
    goal_percentage_complete: int | None = Field(default=None, description="The percentage completion of the goal")
    goal_months_to_budget: int | None = Field(default=None, description="The number of months, including the current month, left in the current goal period.")
    goal_under_funded: int | None = Field(default=None, description="The amount of funding still needed in the current month to stay on track towards completing the goal within the current goal period. This amount will generally correspond to the 'Underfunded' amount in the web and mobile clients except when viewing a category with a Needed for Spending Goal in a future month.  The web and mobile clients will ignore any funding from a prior goal period when viewing category with a Needed for Spending Goal in a future month.")
    goal_overall_funded: int | None = Field(default=None, description="The total amount funded towards the goal within the current goal period.")
    goal_overall_left: int | None = Field(default=None, description="The amount of funding still needed to complete the goal within the current goal period.")
    goal_snoozed_at: dt.datetime | None = Field(default=None, description="The date/time the goal was snoozed.  If the goal is not snoozed, this will be null.")
    deleted: bool = Field(..., description="Whether or not the category has been deleted.  Deleted categories will only be included in delta requests.")


class CategoryGroup(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    hidden: bool = Field(..., description="Whether or not the category group is hidden")
    internal: bool = Field(..., description="Whether or not the category group is internal")
    deleted: bool = Field(..., description="Whether or not the category group has been deleted.  Deleted category groups will only be included in delta requests.")


class Payee(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    transfer_account_id: str | None = Field(default=None, description="If a transfer payee, the `account_id` to which this payee transfers to")
    deleted: bool = Field(..., description="Whether or not the payee has been deleted.  Deleted payees will only be included in delta requests.")


class TransactionClearedStatus(str, Enum):
    """The cleared status of the transaction"""
    CLEARED = "cleared"
    UNCLEARED = "uncleared"
    RECONCILED = "reconciled"


class TransactionSummaryBase(BaseModel):
    id: str = Field(...)
    date: dt.date = Field(..., description="The transaction date in ISO format (e.g. 2016-12-01)")
    amount: int = Field(..., description="The transaction amount in milliunits format")
    memo: str | None = Field(default=None)
    cleared: TransactionClearedStatus = Field(...)
    approved: bool = Field(..., description="Whether or not the transaction is approved")
    flag_color: TransactionFlagColor | None = Field(default=None)
    flag_name: TransactionFlagName | None = Field(default=None)
    account_id: str = Field(...)
    payee_id: str | None = Field(default=None)
    category_id: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None, description="If a transfer transaction, the account to which it transfers")
    transfer_transaction_id: str | None = Field(default=None, description="If a transfer transaction, the id of transaction on the other side of the transfer")
    matched_transaction_id: str | None = Field(default=None, description="If transaction is matched, the id of the matched transaction")
    import_id: str | None = Field(default=None, description="If the transaction was imported, this field is a unique (by account) import identifier.  If this transaction was imported through File Based Import or Direct Import and not through the API, the import_id will have the format: 'YNAB:[milliunit_amount]:[iso_date]:[occurrence]'.  For example, a transaction dated 2015-12-30 in the amount of -$294.23 USD would have an import_id of 'YNAB:-294230:2015-12-30:1'.  If a second transaction on the same account was imported and had the same date and same amount, its import_id would be 'YNAB:-294230:2015-12-30:2'.")
    import_payee_name: str | None = Field(default=None, description="If the transaction was imported, the payee name that was used when importing and before applying any payee rename rules")
    import_payee_name_original: str | None = Field(default=None, description="If the transaction was imported, the original payee name as it appeared on the statement")
    debt_transaction_type: Literal['payment', 'refund', 'fee', 'interest', 'escrow', 'balanceAdjustment', 'credit', 'charge', None] | None = Field(default=None, description="If the transaction is a debt/loan account transaction, the type of transaction")
    deleted: bool = Field(..., description="Whether or not the transaction has been deleted.  Deleted transactions will only be included in delta requests.")


class MonthSummaryBase(BaseModel):
    month: dt.date = Field(...)
    note: str | None = Field(default=None)
    income: int = Field(..., description="The total amount of transactions categorized to 'Inflow: Ready to Assign' in the month")
    budgeted: int = Field(..., description="The total amount assigned (budgeted) in the month")
    activity: int = Field(..., description="The total amount of transactions in the month, excluding those categorized to 'Inflow: Ready to Assign'")
    to_be_budgeted: int = Field(..., description="The available amount for 'Ready to Assign'")
    age_of_money: int | None = Field(default=None, description="The Age of Money as of the month")
    deleted: bool = Field(..., description="Whether or not the month has been deleted.  Deleted months will only be included in delta requests.")


class MonthDetailBase(MonthSummaryBase):
    categories: list[CategoryBase] = Field(..., description="The plan month categories.  Amounts (budgeted, activity, balance, etc.) are specific to the {month} parameter specified.")


class SubTransactionBase(BaseModel):
    id: str = Field(...)
    transaction_id: str = Field(...)
    amount: int = Field(..., description="The subtransaction amount in milliunits format")
    memo: str | None = Field(default=None)
    payee_id: str | None = Field(default=None)
    payee_name: str | None = Field(default=None)
    category_id: str | None = Field(default=None)
    category_name: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None, description="If a transfer, the account_id which the subtransaction transfers to")
    transfer_transaction_id: str | None = Field(default=None, description="If a transfer, the id of transaction on the other side of the transfer")
    deleted: bool = Field(..., description="Whether or not the subtransaction has been deleted.  Deleted subtransactions will only be included in delta requests.")


class ScheduledSubTransactionBase(BaseModel):
    id: str = Field(...)
    scheduled_transaction_id: str = Field(...)
    amount: int = Field(..., description="The scheduled subtransaction amount in milliunits format")
    memo: str | None = Field(default=None)
    payee_id: str | None = Field(default=None)
    payee_name: str | None = Field(default=None)
    category_id: str | None = Field(default=None)
    category_name: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None, description="If a transfer, the account_id which the scheduled subtransaction transfers to")
    deleted: bool = Field(..., description="Whether or not the scheduled subtransaction has been deleted. Deleted scheduled subtransactions will only be included in delta requests.")


class PlanDetail(PlanSummary):
    accounts: list[AccountBase] | None = Field(default=None)
    payees: list[Payee] | None = Field(default=None)
    payee_locations: list[PayeeLocation] | None = Field(default=None)
    category_groups: list[CategoryGroup] | None = Field(default=None)
    categories: list[CategoryBase] | None = Field(default=None)
    months: list[MonthDetailBase] | None = Field(default=None)
    transactions: list[TransactionSummaryBase] | None = Field(default=None)
    subtransactions: list[SubTransactionBase] | None = Field(default=None)
    scheduled_transactions: list[ScheduledTransactionSummaryBase] | None = Field(default=None)
    scheduled_subtransactions: list[ScheduledSubTransactionBase] | None = Field(default=None)


class PlanDetailResponseData(BaseModel):
    plan: PlanDetail = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class PlanDetailResponse(BaseModel):
    data: PlanDetailResponseData = Field(...)


class PlanSettings(BaseModel):
    date_format: DateFormat = Field(...)
    currency_format: CurrencyFormat = Field(...)


class PlanSettingsResponseData(BaseModel):
    settings: PlanSettings = Field(...)


class PlanSettingsResponse(BaseModel):
    data: PlanSettingsResponseData = Field(...)


class AccountsResponseData(BaseModel):
    accounts: list[Account] = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class AccountsResponse(BaseModel):
    data: AccountsResponseData = Field(...)


class AccountResponseData(BaseModel):
    account: Account = Field(...)


class AccountResponse(BaseModel):
    data: AccountResponseData = Field(...)


class SaveAccountType(str, Enum):
    """The type of account to create or update"""
    CHECKING = "checking"
    SAVINGS = "savings"
    CASH = "cash"
    CREDITCARD = "creditCard"
    OTHERASSET = "otherAsset"
    OTHERLIABILITY = "otherLiability"


class SaveAccount(BaseModel):
    name: str = Field(..., description="The name of the account")
    type: SaveAccountType = Field(...)
    balance: int = Field(..., description="The current balance of the account in milliunits format")


class PostAccountWrapper(BaseModel):
    account: SaveAccount = Field(...)


class Category(CategoryBase):
    balance_formatted: str | None = Field(default=None, description="Available balance of the category formatted in the plan's currency format")
    balance_currency: float | None = Field(default=None, description="Available balance of the category as a decimal currency amount")
    activity_formatted: str | None = Field(default=None, description="Activity of the category formatted in the plan's currency format")
    activity_currency: float | None = Field(default=None, description="Activity of the category as a decimal currency amount")
    budgeted_formatted: str | None = Field(default=None, description="Assigned (budgeted) amount of the category formatted in the plan's currency format")
    budgeted_currency: float | None = Field(default=None, description="Assigned (budgeted) amount of the category as a decimal currency amount")
    goal_target_formatted: str | None = Field(default=None, description="The goal target amount formatted in the plan's currency format")
    goal_target_currency: float | None = Field(default=None, description="The goal target amount as a decimal currency amount")
    goal_under_funded_formatted: str | None = Field(default=None, description="The goal underfunded amount formatted in the plan's currency format")
    goal_under_funded_currency: float | None = Field(default=None, description="The goal underfunded amount as a decimal currency amount")
    goal_overall_funded_formatted: str | None = Field(default=None, description="The total amount funded towards the goal formatted in the plan's currency format")
    goal_overall_funded_currency: float | None = Field(default=None, description="The total amount funded towards the goal as a decimal currency amount")
    goal_overall_left_formatted: str | None = Field(default=None, description="The amount of funding still needed to complete the goal formatted in the plan's currency format")
    goal_overall_left_currency: float | None = Field(default=None, description="The amount of funding still needed to complete the goal as a decimal currency amount")


class CategoryGroupWithCategories(CategoryGroup):
    categories: list[Category] = Field(..., description="Category group categories.  Amounts (assigned, activity, available, etc.) are specific to the current plan month (UTC).")


class CategoriesResponseData(BaseModel):
    category_groups: list[CategoryGroupWithCategories] = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class CategoriesResponse(BaseModel):
    data: CategoriesResponseData = Field(...)


class CategoryResponseData(BaseModel):
    category: Category = Field(...)


class CategoryResponse(BaseModel):
    data: CategoryResponseData = Field(...)


class SaveCategoryResponseData(BaseModel):
    category: Category = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class SaveCategoryResponse(BaseModel):
    data: SaveCategoryResponseData = Field(...)


class SaveCategoryGroupResponseData(BaseModel):
    category_group: CategoryGroup = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class SaveCategoryGroupResponse(BaseModel):
    data: SaveCategoryGroupResponseData = Field(...)


class PayeesResponseData(BaseModel):
    payees: list[Payee] = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class PayeesResponse(BaseModel):
    data: PayeesResponseData = Field(...)


class PayeeResponseData(BaseModel):
    payee: Payee = Field(...)


class PayeeResponse(BaseModel):
    data: PayeeResponseData = Field(...)


class SavePayeeResponseData(BaseModel):
    payee: Payee = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class SavePayeeResponse(BaseModel):
    data: SavePayeeResponseData = Field(...)


class PayeeLocationsResponseData(BaseModel):
    payee_locations: list[PayeeLocation] = Field(...)


class PayeeLocationsResponse(BaseModel):
    data: PayeeLocationsResponseData = Field(...)


class PayeeLocationResponseData(BaseModel):
    payee_location: PayeeLocation = Field(...)


class PayeeLocationResponse(BaseModel):
    data: PayeeLocationResponseData = Field(...)


class SubTransaction(SubTransactionBase):
    amount_formatted: str | None = Field(default=None, description="The subtransaction amount formatted in the plan's currency format")
    amount_currency: float | None = Field(default=None, description="The subtransaction amount as a decimal currency amount")


class TransactionSummary(TransactionSummaryBase):
    amount_formatted: str | None = Field(default=None, description="The transaction amount formatted in the plan's currency format")
    amount_currency: float | None = Field(default=None, description="The transaction amount as a decimal currency amount")


class TransactionDetail(TransactionSummary):
    account_name: str = Field(...)
    payee_name: str | None = Field(default=None)
    category_name: str | None = Field(default=None, description="The name of the category.  If a split transaction, this will be 'Split'.")
    subtransactions: list[SubTransaction] = Field(..., description="If a split transaction, the subtransactions.")


class TransactionsResponseData(BaseModel):
    transactions: list[TransactionDetail] = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class TransactionsResponse(BaseModel):
    data: TransactionsResponseData = Field(...)


class HybridTransaction(TransactionSummary):
    type: Literal['transaction', 'subtransaction'] = Field(..., description="Whether the hybrid transaction represents a regular transaction or a subtransaction")
    parent_transaction_id: str | None = Field(default=None, description="For subtransaction types, this is the id of the parent transaction.  For transaction types, this id will be always be null.")
    account_name: str = Field(...)
    payee_name: str | None = Field(default=None)
    category_name: str | None = Field(default=None, description="The name of the category.  If a split transaction, this will be 'Split'.")


class HybridTransactionsResponseData(BaseModel):
    transactions: list[HybridTransaction] = Field(...)
    server_knowledge: int | None = Field(default=None, description="The knowledge of the server")


class HybridTransactionsResponse(BaseModel):
    data: HybridTransactionsResponseData = Field(...)


class SaveSubTransaction(BaseModel):
    amount: int = Field(..., description="The subtransaction amount in milliunits format.")
    payee_id: str | None = Field(default=None, description="The payee for the subtransaction.")
    payee_name: str | None = Field(default=None, description="The payee name.  If a `payee_name` value is provided and `payee_id` has a null value, the `payee_name` value will be used to resolve the payee by either (1) a matching payee rename rule (only if import_id is also specified on parent transaction) or (2) a payee with the same name or (3) creation of a new payee.")
    category_id: str | None = Field(default=None, description="The category for the subtransaction.  Credit Card Payment categories are not permitted and will be ignored if supplied.")
    memo: str | None = Field(default=None)


class SaveTransactionWithOptionalFields(BaseModel):
    account_id: str | None = Field(default=None)
    date: dt.date | None = Field(default=None, description="The transaction date in ISO format (e.g. 2016-12-01).  Future dates (scheduled transactions) are not permitted.  Split transaction dates cannot be changed and if a different date is supplied it will be ignored.")
    amount: int | None = Field(default=None, description="The transaction amount in milliunits format.  Split transaction amounts cannot be changed and if a different amount is supplied it will be ignored.")
    payee_id: str | None = Field(default=None, description="The payee for the transaction.  To create a transfer between two accounts, use the account transfer payee pointing to the target account.  Account transfer payees are specified as `transfer_payee_id` on the account resource.")
    payee_name: str | None = Field(default=None, description="The payee name.  If a `payee_name` value is provided and `payee_id` has a null value, the `payee_name` value will be used to resolve the payee by either (1) a matching payee rename rule (only if `import_id` is also specified) or (2) a payee with the same name or (3) creation of a new payee.")
    category_id: str | None = Field(default=None, description="The category for the transaction.  To configure a split transaction, you can specify null for `category_id` and provide a `subtransactions` array as part of the transaction object.  If an existing transaction is a split, the `category_id` cannot be changed.  Credit Card Payment categories are not permitted and will be ignored if supplied.")
    memo: str | None = Field(default=None)
    cleared: TransactionClearedStatus | None = Field(default=None)
    approved: bool | None = Field(default=None, description="Whether or not the transaction is approved.  If not supplied, transaction will be unapproved by default.")
    flag_color: TransactionFlagColor | None = Field(default=None)
    subtransactions: list[SaveSubTransaction] | None = Field(default=None, description="An array of subtransactions to configure a transaction as a split. Updating `subtransactions` on an existing split transaction is not supported.")


class ExistingTransaction(SaveTransactionWithOptionalFields):
    pass


class PutTransactionWrapper(BaseModel):
    transaction: ExistingTransaction = Field(...)


class NewTransaction(SaveTransactionWithOptionalFields):
    import_id: str | None = Field(default=None, description="If specified, a new transaction will be assigned this `import_id` and considered \"imported\".  We will also attempt to match this imported transaction to an existing \"user-entered\" transaction on the same account, with the same amount, and with a date +/-10 days from the imported transaction date.<br><br>Transactions imported through File Based Import or Direct Import (not through the API) are assigned an import_id in the format: 'YNAB:[milliunit_amount]:[iso_date]:[occurrence]'. For example, a transaction dated 2015-12-30 in the amount of -$294.23 USD would have an import_id of 'YNAB:-294230:2015-12-30:1'.  If a second transaction on the same account was imported and had the same date and same amount, its import_id would be 'YNAB:-294230:2015-12-30:2'.  Using a consistent format will prevent duplicates through Direct Import and File Based Import.<br><br>If import_id is omitted or specified as null, the transaction will be treated as a \"user-entered\" transaction. As such, it will be eligible to be matched against transactions later being imported (via DI, FBI, or API).")


class PostTransactionsWrapper(BaseModel):
    transaction: NewTransaction | None = Field(default=None)
    transactions: list[NewTransaction] | None = Field(default=None)


class SaveTransactionWithIdOrImportId(SaveTransactionWithOptionalFields):
    id: str | None = Field(default=None, description="If specified, this id will be used to lookup a transaction by its `id` for the purpose of updating the transaction itself. If not specified, an `import_id` should be supplied.")
    import_id: str | None = Field(default=None, description="If specified, this id will be used to lookup a transaction by its `import_id` for the purpose of updating the transaction itself. If not specified, an `id` should be supplied.  You may not provide both an `id` and an `import_id` and updating an `import_id` on an existing transaction is not allowed.")


class PatchTransactionsWrapper(BaseModel):
    transactions: list[SaveTransactionWithIdOrImportId] = Field(...)


class SaveTransactionsResponseData(BaseModel):
    transaction_ids: list[str] = Field(..., description="The transaction ids that were saved")
    transaction: TransactionDetail | None = Field(default=None)
    transactions: list[TransactionDetail] | None = Field(default=None, description="If multiple transactions were specified, the transactions that were saved")
    duplicate_import_ids: list[str] | None = Field(default=None, description="If multiple transactions were specified, a list of import_ids that were not created because of an existing `import_id` found on the same account")
    server_knowledge: int = Field(..., description="The knowledge of the server")


class SaveTransactionsResponse(BaseModel):
    data: SaveTransactionsResponseData = Field(...)


class TransactionResponseData(BaseModel):
    transaction: TransactionDetail = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class TransactionResponse(BaseModel):
    data: TransactionResponseData = Field(...)


class PostPayee(BaseModel):
    name: str = Field(..., description="The name of the payee.")


class PostPayeeWrapper(BaseModel):
    payee: PostPayee = Field(...)


class SavePayee(BaseModel):
    name: str | None = Field(default=None, description="The name of the payee.")


class PatchPayeeWrapper(BaseModel):
    payee: SavePayee = Field(...)


class SaveCategoryGroup(BaseModel):
    name: str = Field(..., description="The name of the category group. The name must be a maximum of 50 characters.")


class PostCategoryGroupWrapper(BaseModel):
    category_group: SaveCategoryGroup = Field(...)


class PatchCategoryGroupWrapper(BaseModel):
    category_group: SaveCategoryGroup = Field(...)


class SaveCategory(BaseModel):
    name: str | None = Field(default=None)
    note: str | None = Field(default=None)
    category_group_id: str | None = Field(default=None, description="The id of the category group to which this category belongs.  An internal category group may not be specified.")
    goal_target: int | None = Field(default=None, description="The goal target amount in milliunits format.  If value is specified and goal has not already been configured for category, a monthly goal will be created for the category with this target amount.  If goal_type is not specified, it will default to 'NEED' or 'MF' for Credit Card Payment categories.")
    goal_target_date: dt.date | None = Field(default=None, description="The goal target date in ISO format (e.g. 2016-12-01).")
    goal_needs_whole_amount: bool | None = Field(default=None, description="Whether the goal requires the full target amount each period. Only supported for 'NEED' goals. When true, the goal is configured as 'Set aside another...'. When false, the goal is configured as 'Refill up to...'.")


class NewCategory(SaveCategory):
    pass


class PostCategoryWrapper(BaseModel):
    category: NewCategory = Field(...)


class ExistingCategory(SaveCategory):
    pass


class PatchCategoryWrapper(BaseModel):
    category: ExistingCategory = Field(...)


class SaveMonthCategory(BaseModel):
    budgeted: int = Field(..., description="Assigned (budgeted) amount in milliunits format")


class PatchMonthCategoryWrapper(BaseModel):
    category: SaveMonthCategory = Field(...)


class TransactionsImportResponseData(BaseModel):
    transaction_ids: list[str] = Field(..., description="The list of transaction ids that were imported.")


class TransactionsImportResponse(BaseModel):
    data: TransactionsImportResponseData = Field(...)


class BulkResponseDataData(BaseModel):
    transaction_ids: list[str] = Field(..., description="The list of Transaction ids that were created.")
    duplicate_import_ids: list[str] = Field(..., description="If any Transactions were not created because they had an `import_id` matching a transaction already on the same account, the specified import_id(s) will be included in this list.")


class BulkResponseData(BaseModel):
    bulk: BulkResponseDataData = Field(...)


class BulkResponse(BaseModel):
    data: BulkResponseData = Field(...)


class BulkTransactions(BaseModel):
    transactions: list[SaveTransactionWithOptionalFields] = Field(...)


class ScheduledSubTransaction(ScheduledSubTransactionBase):
    amount_formatted: str | None = Field(default=None, description="The scheduled subtransaction amount formatted in the plan's currency format")
    amount_currency: float | None = Field(default=None, description="The scheduled subtransaction amount as a decimal currency amount")


class ScheduledTransactionSummary(ScheduledTransactionSummaryBase):
    amount_formatted: str | None = Field(default=None, description="The scheduled transaction amount formatted in the plan's currency format")
    amount_currency: float | None = Field(default=None, description="The scheduled transaction amount as a decimal currency amount")


class ScheduledTransactionDetail(ScheduledTransactionSummary):
    account_name: str = Field(...)
    payee_name: str | None = Field(default=None)
    category_name: str | None = Field(default=None, description="The name of the category.  If a split scheduled transaction, this will be 'Split'.")
    subtransactions: list[ScheduledSubTransaction] = Field(..., description="If a split scheduled transaction, the subtransactions.")


class ScheduledTransactionsResponseData(BaseModel):
    scheduled_transactions: list[ScheduledTransactionDetail] = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class ScheduledTransactionsResponse(BaseModel):
    data: ScheduledTransactionsResponseData = Field(...)


class ScheduledTransactionResponseData(BaseModel):
    scheduled_transaction: ScheduledTransactionDetail = Field(...)


class ScheduledTransactionResponse(BaseModel):
    data: ScheduledTransactionResponseData = Field(...)


class ScheduledTransactionFrequency(str, Enum):
    """The scheduled transaction frequency"""
    NEVER = "never"
    DAILY = "daily"
    WEEKLY = "weekly"
    EVERYOTHERWEEK = "everyOtherWeek"
    TWICEAMONTH = "twiceAMonth"
    EVERY4WEEKS = "every4Weeks"
    MONTHLY = "monthly"
    EVERYOTHERMONTH = "everyOtherMonth"
    EVERY3MONTHS = "every3Months"
    EVERY4MONTHS = "every4Months"
    TWICEAYEAR = "twiceAYear"
    YEARLY = "yearly"
    EVERYOTHERYEAR = "everyOtherYear"


class SaveScheduledTransaction(BaseModel):
    account_id: str = Field(...)
    date: dt.date = Field(..., description="The scheduled transaction date in ISO format (e.g. 2016-12-01).  This should be a future date no more than 5 years into the future.")
    amount: int | None = Field(default=None, description="The scheduled transaction amount in milliunits format.")
    payee_id: str | None = Field(default=None, description="The payee for the scheduled transaction.  To create a transfer between two accounts, use the account transfer payee pointing to the target account.  Account transfer payees are specified as `transfer_payee_id` on the account resource.")
    payee_name: str | None = Field(default=None, description="The payee name for the the scheduled transaction.  If a `payee_name` value is provided and `payee_id` has a null value, the `payee_name` value will be used to resolve the payee by either (1) a payee with the same name or (2) creation of a new payee.")
    category_id: str | None = Field(default=None, description="The category for the scheduled transaction. Credit Card Payment categories are not permitted. Creating a split scheduled transaction is not currently supported.")
    memo: str | None = Field(default=None)
    flag_color: TransactionFlagColor | None = Field(default=None)
    frequency: ScheduledTransactionFrequency | None = Field(default=None)


class PutScheduledTransactionWrapper(BaseModel):
    scheduled_transaction: SaveScheduledTransaction = Field(...)


class PostScheduledTransactionWrapper(BaseModel):
    scheduled_transaction: SaveScheduledTransaction = Field(...)


class MonthSummary(MonthSummaryBase):
    income_formatted: str | None = Field(default=None, description="The total income formatted in the plan's currency format")
    income_currency: float | None = Field(default=None, description="The total income as a decimal currency amount")
    budgeted_formatted: str | None = Field(default=None, description="The total amount assigned formatted in the plan's currency format")
    budgeted_currency: float | None = Field(default=None, description="The total amount assigned as a decimal currency amount")
    activity_formatted: str | None = Field(default=None, description="The total activity amount formatted in the plan's currency format")
    activity_currency: float | None = Field(default=None, description="The total activity amount as a decimal currency amount")
    to_be_budgeted_formatted: str | None = Field(default=None, description="The available amount for 'Ready to Assign' formatted in the plan's currency format")
    to_be_budgeted_currency: float | None = Field(default=None, description="The available amount for 'Ready to Assign' as a decimal currency amount")


class MonthSummariesResponseData(BaseModel):
    months: list[MonthSummary] = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class MonthSummariesResponse(BaseModel):
    data: MonthSummariesResponseData = Field(...)


class MonthDetail(MonthSummary):
    categories: list[Category] = Field(..., description="The plan month categories.  Amounts (budgeted, activity, balance, etc.) are specific to the {month} parameter specified.")


class MonthDetailResponseData(BaseModel):
    month: MonthDetail = Field(...)


class MonthDetailResponse(BaseModel):
    data: MonthDetailResponseData = Field(...)


class MoneyMovementBase(BaseModel):
    id: str = Field(...)
    month: dt.date | None = Field(default=None, description="The month of the money movement in ISO format (e.g. 2024-01-01)")
    moved_at: dt.datetime | None = Field(default=None, description="The date/time the money movement was processed on the server in ISO format (e.g. 2024-01-01T12:00:00Z)")
    note: str | None = Field(default=None)
    money_movement_group_id: str | None = Field(default=None, description="The id of the money movement group this movement belongs to")
    performed_by_user_id: str | None = Field(default=None, description="The id of the user who performed the money movement")
    from_category_id: str | None = Field(default=None, description="The id of the category the money was moved from")
    to_category_id: str | None = Field(default=None, description="The id of the category the money was moved to")
    amount: int = Field(..., description="The amount of the money movement in milliunits format")


class MoneyMovement(MoneyMovementBase):
    amount_formatted: str | None = Field(default=None, description="The money movement amount formatted in the plan's currency format")
    amount_currency: float | None = Field(default=None, description="The money movement amount as a decimal currency amount")


class MoneyMovementsResponseData(BaseModel):
    money_movements: list[MoneyMovement] = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class MoneyMovementsResponse(BaseModel):
    data: MoneyMovementsResponseData = Field(...)


class MoneyMovementGroup(BaseModel):
    id: str = Field(...)
    group_created_at: dt.datetime = Field(..., description="When the money movement group was created")
    month: dt.date = Field(..., description="The month of the money movement group in ISO format (e.g. 2024-01-01)")
    note: str | None = Field(default=None)
    performed_by_user_id: str | None = Field(default=None, description="The id of the user who performed the money movement group")


class MoneyMovementGroupsResponseData(BaseModel):
    money_movement_groups: list[MoneyMovementGroup] = Field(...)
    server_knowledge: int = Field(..., description="The knowledge of the server")


class MoneyMovementGroupsResponse(BaseModel):
    data: MoneyMovementGroupsResponseData = Field(...)


# Rebuild all models to resolve forward references
try:
    ErrorDetail.model_rebuild()
except AttributeError:
    pass
try:
    ErrorResponse.model_rebuild()
except AttributeError:
    pass
try:
    User.model_rebuild()
except AttributeError:
    pass
try:
    UserResponseData.model_rebuild()
    UserResponse.model_rebuild()
except AttributeError:
    pass
try:
    DateFormat.model_rebuild()
except AttributeError:
    pass
try:
    CurrencyFormat.model_rebuild()
except AttributeError:
    pass
try:
    AccountType.model_rebuild()
except AttributeError:
    pass
try:
    LoanAccountPeriodicValue.model_rebuild()
except AttributeError:
    pass
try:
    AccountBase.model_rebuild()
except AttributeError:
    pass
try:
    Account.model_rebuild()
except AttributeError:
    pass
try:
    PlanSummary.model_rebuild()
except AttributeError:
    pass
try:
    PlanSummaryResponseData.model_rebuild()
    PlanSummaryResponse.model_rebuild()
except AttributeError:
    pass
try:
    PayeeLocation.model_rebuild()
except AttributeError:
    pass
try:
    TransactionFlagName.model_rebuild()
except AttributeError:
    pass
try:
    TransactionFlagColor.model_rebuild()
except AttributeError:
    pass
try:
    ScheduledTransactionSummaryBase.model_rebuild()
except AttributeError:
    pass
try:
    CategoryBase.model_rebuild()
except AttributeError:
    pass
try:
    CategoryGroup.model_rebuild()
except AttributeError:
    pass
try:
    Payee.model_rebuild()
except AttributeError:
    pass
try:
    TransactionClearedStatus.model_rebuild()
except AttributeError:
    pass
try:
    TransactionSummaryBase.model_rebuild()
except AttributeError:
    pass
try:
    MonthSummaryBase.model_rebuild()
except AttributeError:
    pass
try:
    MonthDetailBase.model_rebuild()
except AttributeError:
    pass
try:
    SubTransactionBase.model_rebuild()
except AttributeError:
    pass
try:
    ScheduledSubTransactionBase.model_rebuild()
except AttributeError:
    pass
try:
    PlanDetail.model_rebuild()
except AttributeError:
    pass
try:
    PlanDetailResponseData.model_rebuild()
    PlanDetailResponse.model_rebuild()
except AttributeError:
    pass
try:
    PlanSettings.model_rebuild()
except AttributeError:
    pass
try:
    PlanSettingsResponseData.model_rebuild()
    PlanSettingsResponse.model_rebuild()
except AttributeError:
    pass
try:
    AccountsResponseData.model_rebuild()
    AccountsResponse.model_rebuild()
except AttributeError:
    pass
try:
    AccountResponseData.model_rebuild()
    AccountResponse.model_rebuild()
except AttributeError:
    pass
try:
    SaveAccountType.model_rebuild()
except AttributeError:
    pass
try:
    SaveAccount.model_rebuild()
except AttributeError:
    pass
try:
    PostAccountWrapper.model_rebuild()
except AttributeError:
    pass
try:
    Category.model_rebuild()
except AttributeError:
    pass
try:
    CategoryGroupWithCategories.model_rebuild()
except AttributeError:
    pass
try:
    CategoriesResponseData.model_rebuild()
    CategoriesResponse.model_rebuild()
except AttributeError:
    pass
try:
    CategoryResponseData.model_rebuild()
    CategoryResponse.model_rebuild()
except AttributeError:
    pass
try:
    SaveCategoryResponseData.model_rebuild()
    SaveCategoryResponse.model_rebuild()
except AttributeError:
    pass
try:
    SaveCategoryGroupResponseData.model_rebuild()
    SaveCategoryGroupResponse.model_rebuild()
except AttributeError:
    pass
try:
    PayeesResponseData.model_rebuild()
    PayeesResponse.model_rebuild()
except AttributeError:
    pass
try:
    PayeeResponseData.model_rebuild()
    PayeeResponse.model_rebuild()
except AttributeError:
    pass
try:
    SavePayeeResponseData.model_rebuild()
    SavePayeeResponse.model_rebuild()
except AttributeError:
    pass
try:
    PayeeLocationsResponseData.model_rebuild()
    PayeeLocationsResponse.model_rebuild()
except AttributeError:
    pass
try:
    PayeeLocationResponseData.model_rebuild()
    PayeeLocationResponse.model_rebuild()
except AttributeError:
    pass
try:
    SubTransaction.model_rebuild()
except AttributeError:
    pass
try:
    TransactionSummary.model_rebuild()
except AttributeError:
    pass
try:
    TransactionDetail.model_rebuild()
except AttributeError:
    pass
try:
    TransactionsResponseData.model_rebuild()
    TransactionsResponse.model_rebuild()
except AttributeError:
    pass
try:
    HybridTransaction.model_rebuild()
except AttributeError:
    pass
try:
    HybridTransactionsResponseData.model_rebuild()
    HybridTransactionsResponse.model_rebuild()
except AttributeError:
    pass
try:
    SaveSubTransaction.model_rebuild()
except AttributeError:
    pass
try:
    SaveTransactionWithOptionalFields.model_rebuild()
except AttributeError:
    pass
try:
    ExistingTransaction.model_rebuild()
except AttributeError:
    pass
try:
    PutTransactionWrapper.model_rebuild()
except AttributeError:
    pass
try:
    NewTransaction.model_rebuild()
except AttributeError:
    pass
try:
    PostTransactionsWrapper.model_rebuild()
except AttributeError:
    pass
try:
    SaveTransactionWithIdOrImportId.model_rebuild()
except AttributeError:
    pass
try:
    PatchTransactionsWrapper.model_rebuild()
except AttributeError:
    pass
try:
    SaveTransactionsResponseData.model_rebuild()
    SaveTransactionsResponse.model_rebuild()
except AttributeError:
    pass
try:
    TransactionResponseData.model_rebuild()
    TransactionResponse.model_rebuild()
except AttributeError:
    pass
try:
    PostPayee.model_rebuild()
except AttributeError:
    pass
try:
    PostPayeeWrapper.model_rebuild()
except AttributeError:
    pass
try:
    SavePayee.model_rebuild()
except AttributeError:
    pass
try:
    PatchPayeeWrapper.model_rebuild()
except AttributeError:
    pass
try:
    SaveCategoryGroup.model_rebuild()
except AttributeError:
    pass
try:
    PostCategoryGroupWrapper.model_rebuild()
except AttributeError:
    pass
try:
    PatchCategoryGroupWrapper.model_rebuild()
except AttributeError:
    pass
try:
    SaveCategory.model_rebuild()
except AttributeError:
    pass
try:
    NewCategory.model_rebuild()
except AttributeError:
    pass
try:
    PostCategoryWrapper.model_rebuild()
except AttributeError:
    pass
try:
    ExistingCategory.model_rebuild()
except AttributeError:
    pass
try:
    PatchCategoryWrapper.model_rebuild()
except AttributeError:
    pass
try:
    SaveMonthCategory.model_rebuild()
except AttributeError:
    pass
try:
    PatchMonthCategoryWrapper.model_rebuild()
except AttributeError:
    pass
try:
    TransactionsImportResponseData.model_rebuild()
    TransactionsImportResponse.model_rebuild()
except AttributeError:
    pass
try:
    BulkResponseDataData.model_rebuild()
    BulkResponseData.model_rebuild()
    BulkResponse.model_rebuild()
except AttributeError:
    pass
try:
    BulkTransactions.model_rebuild()
except AttributeError:
    pass
try:
    ScheduledSubTransaction.model_rebuild()
except AttributeError:
    pass
try:
    ScheduledTransactionSummary.model_rebuild()
except AttributeError:
    pass
try:
    ScheduledTransactionDetail.model_rebuild()
except AttributeError:
    pass
try:
    ScheduledTransactionsResponseData.model_rebuild()
    ScheduledTransactionsResponse.model_rebuild()
except AttributeError:
    pass
try:
    ScheduledTransactionResponseData.model_rebuild()
    ScheduledTransactionResponse.model_rebuild()
except AttributeError:
    pass
try:
    ScheduledTransactionFrequency.model_rebuild()
except AttributeError:
    pass
try:
    SaveScheduledTransaction.model_rebuild()
except AttributeError:
    pass
try:
    PutScheduledTransactionWrapper.model_rebuild()
except AttributeError:
    pass
try:
    PostScheduledTransactionWrapper.model_rebuild()
except AttributeError:
    pass
try:
    MonthSummary.model_rebuild()
except AttributeError:
    pass
try:
    MonthSummariesResponseData.model_rebuild()
    MonthSummariesResponse.model_rebuild()
except AttributeError:
    pass
try:
    MonthDetail.model_rebuild()
except AttributeError:
    pass
try:
    MonthDetailResponseData.model_rebuild()
    MonthDetailResponse.model_rebuild()
except AttributeError:
    pass
try:
    MoneyMovementBase.model_rebuild()
except AttributeError:
    pass
try:
    MoneyMovement.model_rebuild()
except AttributeError:
    pass
try:
    MoneyMovementsResponseData.model_rebuild()
    MoneyMovementsResponse.model_rebuild()
except AttributeError:
    pass
try:
    MoneyMovementGroup.model_rebuild()
except AttributeError:
    pass
try:
    MoneyMovementGroupsResponseData.model_rebuild()
    MoneyMovementGroupsResponse.model_rebuild()
except AttributeError:
    pass