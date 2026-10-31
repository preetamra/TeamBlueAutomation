import os
import pytest
from api.client import ParaBankClient

USERNAME = os.getenv("PARABANK_USER", "john")
PASSWORD = os.getenv("PARABANK_PASS", "demo")


@pytest.fixture
def api_client():
    """A clean API client for every test."""
    return ParaBankClient()


@pytest.fixture
def customer_session(api_client):
    """Log the known customer in; return its id, one existing account and the profile."""
    login_resp = api_client.login(USERNAME, PASSWORD)
    assert login_resp.status_code == 200, f"Initial login failed: {login_resp.text}"
    customer = login_resp.json()
    customer_id = customer["id"]

    accounts_resp = api_client.get_customer_accounts(customer_id)
    assert accounts_resp.status_code == 200
    accounts = accounts_resp.json()
    assert len(accounts) > 0, "The customer must own at least one base account"

    return {
        "customer_id": customer_id,
        "base_account_id": accounts[0]["id"],
        "customer": customer,
    }
