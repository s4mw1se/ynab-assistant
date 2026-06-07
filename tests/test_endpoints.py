import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.state import state

@pytest.fixture(autouse=True)
def run_around_tests():
    state.reset()
    yield

client = TestClient(app)


def test_get_user():
    
    response = client.get("/v1/user")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_plans():
    
    response = client.get("/v1/plans")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_plan_by_id():
    
    response = client.get("/v1/plans/plan_default")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_plan_settings_by_id():
    
    response = client.get("/v1/plans/plan_default/settings")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_accounts():
    
    response = client.get("/v1/plans/plan_default/accounts")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_create_account():
    
    response = client.post("/v1/plans/plan_default/accounts", json={"account": {"name": "New Savings", "type": "savings", "balance": 1000000}})
    assert response.status_code == 201
    data = response.json()
    assert "data" in data


def test_get_account_by_id():
    
    response = client.get("/v1/plans/plan_default/accounts/account_1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_categories():
    
    response = client.get("/v1/plans/plan_default/categories")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_create_category():
    
    response = client.post("/v1/plans/plan_default/categories", json={"category": {"name": "Subcategory"}})
    assert response.status_code == 201
    data = response.json()
    assert "data" in data


def test_get_category_by_id():
    
    response = client.get("/v1/plans/plan_default/categories/category_1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_update_category():
    
    response = client.patch("/v1/plans/plan_default/categories/category_1", json={"category": {"name": "Renamed Rent", "note": "Updated note"}})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_month_category_by_id():
    
    response = client.get("/v1/plans/plan_default/months/2026-06-01/categories/category_1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_update_month_category():
    
    response = client.patch("/v1/plans/plan_default/months/2026-06-01/categories/category_1", json={"category": {"budgeted": 1200000}})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_create_category_group():
    
    response = client.post("/v1/plans/plan_default/category_groups", json={"category_group": {"name": "New Group"}})
    assert response.status_code == 201
    data = response.json()
    assert "data" in data


def test_update_category_group():
    
    response = client.patch("/v1/plans/plan_default/category_groups/group_1", json={"category_group": {"name": "Updated Group Name"}})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_payees():
    
    response = client.get("/v1/plans/plan_default/payees")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_create_payee():
    
    response = client.post("/v1/plans/plan_default/payees", json={"payee": {"name": "New Payee"}})
    assert response.status_code == 201
    data = response.json()
    assert "data" in data


def test_get_payee_by_id():
    
    response = client.get("/v1/plans/plan_default/payees/payee_1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_update_payee():
    
    response = client.patch("/v1/plans/plan_default/payees/payee_1", json={"payee": {"name": "Updated Payee Name"}})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_payee_locations():
    
    response = client.get("/v1/plans/plan_default/payee_locations")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_payee_location_by_id():
    
    response = client.get("/v1/plans/plan_default/payee_locations/loc_1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_payee_locations_by_payee():
    
    response = client.get("/v1/plans/plan_default/payees/payee_1/payee_locations")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_plan_months():
    
    response = client.get("/v1/plans/plan_default/months")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_plan_month():
    
    response = client.get("/v1/plans/plan_default/months/2026-06-01")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_money_movements():
    
    response = client.get("/v1/plans/plan_default/money_movements")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_money_movements_by_month():
    
    response = client.get("/v1/plans/plan_default/months/2026-06-01/money_movements")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_money_movement_groups():
    
    response = client.get("/v1/plans/plan_default/money_movement_groups")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_money_movement_groups_by_month():
    
    response = client.get("/v1/plans/plan_default/months/2026-06-01/money_movement_groups")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_transactions():
    
    response = client.get("/v1/plans/plan_default/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_create_transaction():
    
    response = client.post("/v1/plans/plan_default/transactions", json={"transaction": {"account_id": "account_1", "date": "2026-06-01", "amount": -50000, "payee_id": "payee_1", "category_id": "category_1", "memo": "Coffee"}})
    assert response.status_code == 201
    data = response.json()
    assert "data" in data


def test_update_transactions():
    
    response = client.patch("/v1/plans/plan_default/transactions", json={"transactions": [{"id": "tx_1", "memo": "Updated Rent memo"}]})
    assert response.status_code == 209
    data = response.json()
    assert "data" in data


def test_import_transactions():
    
    response = client.post("/v1/plans/plan_default/transactions/import")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_transaction_by_id():
    
    response = client.get("/v1/plans/plan_default/transactions/tx_1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_update_transaction():
    
    response = client.put("/v1/plans/plan_default/transactions/tx_1", json={"transaction": {"account_id": "account_1", "date": "2026-06-01", "amount": -1000000, "payee_id": "payee_1", "category_id": "category_1", "memo": "Updated Rent Payment"}})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_delete_transaction():
    
    response = client.delete("/v1/plans/plan_default/transactions/tx_1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_transactions_by_account():
    
    response = client.get("/v1/plans/plan_default/accounts/account_1/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_transactions_by_category():
    
    response = client.get("/v1/plans/plan_default/categories/category_1/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_transactions_by_payee():
    
    response = client.get("/v1/plans/plan_default/payees/payee_1/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_transactions_by_month():
    
    response = client.get("/v1/plans/plan_default/months/2026-06-01/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_scheduled_transactions():
    
    response = client.get("/v1/plans/plan_default/scheduled_transactions")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_create_scheduled_transaction():
    
    response = client.post("/v1/plans/plan_default/scheduled_transactions", json={"scheduled_transaction": {"account_id": "account_1", "date": "2026-08-01", "frequency": "monthly", "amount": -50000, "payee_id": "payee_1", "category_id": "category_1", "memo": "Monthly Sub"}})
    assert response.status_code == 201
    data = response.json()
    assert "data" in data


def test_get_scheduled_transaction_by_id():
    
    response = client.get("/v1/plans/plan_default/scheduled_transactions/sch_1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_update_scheduled_transaction():
    
    response = client.put("/v1/plans/plan_default/scheduled_transactions/sch_1", json={"scheduled_transaction": {"account_id": "account_1", "date": "2026-08-01", "frequency": "monthly", "amount": -60000, "memo": "Updated Sub"}})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_delete_scheduled_transaction():
    
    response = client.delete("/v1/plans/plan_default/scheduled_transactions/sch_1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
