import os
import pytest
from api.schemas import (
    assert_account_schema,
    assert_customer_schema,
    assert_loan_response_schema,
)

USERNAME = os.getenv("PARABANK_USER", "john")
PASSWORD = os.getenv("PARABANK_PASS", "demo")


def create_checking_account(api_client, customer_session):
    """Create a checking account; fail with a clear message if ParaBank refuses."""
    resp = api_client.create_account(
        customer_session["customer_id"], 0, customer_session["base_account_id"]
    )
    assert resp.status_code == 200, (
        f"createAccount failed ({resp.status_code}): {resp.text}"
    )
    return resp.json()


def assert_ok(response, action):
    """Check for a 200 and show ParaBank's answer when it is not."""
    assert response.status_code == 200, (
        f"{action} failed ({response.status_code}): {response.text}"
    )


@pytest.fixture
def fresh_account(api_client, customer_session):
    """A brand-new, isolated bank account, so tests stay independent when run in parallel."""
    return create_checking_account(api_client, customer_session)


@pytest.mark.regression
def test_api_01_login_returns_customer_id_and_name(api_client):
    """API-01: valid login -> status 200 + customer id and name present."""
    response = api_client.login(USERNAME, PASSWORD)

    assert response.status_code == 200
    body = response.json()
    assert_customer_schema(body)


@pytest.mark.regression
def test_api_02_get_customer_accounts_validates_schema_and_headers(
    api_client, customer_session
):
    """API-02: account list -> JSON Content-Type + schema check of every account."""
    response = api_client.get_customer_accounts(customer_session["customer_id"])

    assert response.status_code == 200
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type.lower(), (
        f"JSON Content-Type expected, got: {content_type}"
    )

    accounts = response.json()
    assert isinstance(accounts, list) and len(accounts) > 0, (
        "The account list must not be empty"
    )
    for account in accounts:
        assert_account_schema(account)


@pytest.mark.regression
def test_api_03_create_account_appears_in_customer_account_list(
    api_client, customer_session
):
    """API-03: create an account (CRUD Create) -> the new id is in the customer's list."""
    create_resp = api_client.create_account(
        customer_id=customer_session["customer_id"],
        new_account_type=1,  # 1 = SAVINGS
        from_account_id=customer_session["base_account_id"],
    )
    assert_ok(create_resp, "createAccount")
    new_account = create_resp.json()
    assert_account_schema(new_account)
    new_account_id = new_account["id"]

    # The account must be of the requested type and belong to the logged-in customer
    assert new_account["type"] == "SAVINGS", (
        f"A SAVINGS account was requested, got: {new_account['type']}"
    )
    assert new_account["customerId"] == customer_session["customer_id"], (
        f"The new account belongs to customer {new_account['customerId']}, "
        f"expected {customer_session['customer_id']}"
    )

    # Check that the new account appears in the customer's account list
    list_resp = api_client.get_customer_accounts(customer_session["customer_id"])
    assert list_resp.status_code == 200
    account_ids = [acc["id"] for acc in list_resp.json()]
    assert new_account_id in account_ids, (
        f"The new account {new_account_id} should be in {account_ids}"
    )


@pytest.mark.regression
def test_api_04_deposit_increases_balance_by_exact_amount(api_client, fresh_account):
    """API-04: deposit (CRUD Update) -> the balance grows by exactly the deposited amount."""
    account_id = fresh_account["id"]
    # Re-read the real balance through the API: the createAccount response does not
    # include the opening deposit that ParaBank credits to a new account.
    initial_resp = api_client.get_account(account_id)
    assert initial_resp.status_code == 200
    initial_balance = float(initial_resp.json()["balance"])
    deposit_amount = 250.00

    deposit_resp = api_client.deposit(account_id=account_id, amount=deposit_amount)
    assert_ok(deposit_resp, "deposit")

    updated_resp = api_client.get_account(account_id)
    assert updated_resp.status_code == 200
    updated_balance = float(updated_resp.json()["balance"])

    assert updated_balance == pytest.approx(initial_balance + deposit_amount, abs=0.01)


@pytest.mark.regression
def test_api_05_transfer_moves_exact_amount_between_two_accounts(
    api_client, customer_session
):
    """API-05: transfer -> the source account drops by X and the target account grows by X."""
    # Two isolated accounts that belong to this test only
    source_acc = create_checking_account(api_client, customer_session)
    target_acc = create_checking_account(api_client, customer_session)

    # Fund the source account so the transfer cannot fail for lack of money
    assert_ok(api_client.deposit(source_acc["id"], 500.00), "deposit")

    source_before = float(api_client.get_account(source_acc["id"]).json()["balance"])
    target_before = float(api_client.get_account(target_acc["id"]).json()["balance"])
    transfer_amount = 125.50

    transfer_resp = api_client.transfer(
        from_account_id=source_acc["id"],
        to_account_id=target_acc["id"],
        amount=transfer_amount,
    )
    assert_ok(transfer_resp, "transfer")

    source_after = float(api_client.get_account(source_acc["id"]).json()["balance"])
    target_after = float(api_client.get_account(target_acc["id"]).json()["balance"])

    assert source_after == pytest.approx(source_before - transfer_amount, abs=0.01)
    assert target_after == pytest.approx(target_before + transfer_amount, abs=0.01)


def test_api_06_request_loan_returns_decision_and_creates_account_when_approved(
    api_client, customer_session, fresh_account
):
    """API-06: loan request -> check the approval status and the account created for the loan."""
    # Make sure the balance covers the down payment
    assert_ok(api_client.deposit(fresh_account["id"], 1000.00), "deposit")

    loan_resp = api_client.request_loan(
        customer_id=customer_session["customer_id"],
        amount=100.00,
        down_payment=20.00,
        from_account_id=fresh_account["id"],
    )
    assert_ok(loan_resp, "requestLoan")
    loan_data = loan_resp.json()
    assert_loan_response_schema(loan_data)
    assert loan_data["approved"] is True, f"A valid loan should have been approved: {loan_data}"

    # The loan account must exist and belong to the logged-in customer
    loan_account_resp = api_client.get_account(loan_data["accountId"])
    assert_ok(loan_account_resp, "GET loan account")
    loan_account = loan_account_resp.json()
    assert loan_account["customerId"] == customer_session["customer_id"], (
        f"The loan account should belong to customer {customer_session['customer_id']}: "
        f"{loan_account}"
    )


@pytest.mark.parametrize("boundary_amount", [0, 1000000000])
def test_api_07_transfer_boundary_zero_and_very_large_amount(
    api_client, customer_session, boundary_amount
):
    """API-07: boundary values -> transfer of 0 and of a very large amount.

       Observed ParaBank behaviour (29 Oct 2026): both transfers are accepted (200).
       The 1,000,000,000 transfer leaves the source at -999,999,900 $, so no balance
       check is done. Reported as an application defect; the test checks that money
       is conserved between the two accounts.
       """
    source_acc = create_checking_account(api_client, customer_session)
    target_acc = create_checking_account(api_client, customer_session)

    source_before = float(api_client.get_account(source_acc["id"]).json()["balance"])
    target_before = float(api_client.get_account(target_acc["id"]).json()["balance"])

    resp = api_client.transfer(
        from_account_id=source_acc["id"],
        to_account_id=target_acc["id"],
        amount=boundary_amount,
    )
    assert_ok(resp, f"transfer of {boundary_amount}")

    source_after = float(api_client.get_account(source_acc["id"]).json()["balance"])
    target_after = float(api_client.get_account(target_acc["id"]).json()["balance"])

    # Money must be conserved between the two accounts
    assert source_before - source_after == pytest.approx(
        target_after - target_before, abs=0.01
    )
