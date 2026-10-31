def assert_customer_schema(data: dict) -> None:
    """Check the JSON structure of a customer (API-01)."""
    assert isinstance(data, dict), f"A JSON object (dict) was expected, got: {type(data)}"
    required_keys = {"id", "firstName", "lastName"}
    assert required_keys.issubset(data.keys()), (
        f"Missing keys in the customer profile: {required_keys - set(data.keys())}"
    )
    assert isinstance(data["id"], int), "The customer id must be an integer"
    assert isinstance(data["firstName"], str) and len(data["firstName"]) > 0, (
        "The customer first name must be a non-empty string"
    )
    assert isinstance(data["lastName"], str) and len(data["lastName"]) > 0, (
        "The customer last name must be a non-empty string"
    )


def assert_account_schema(account: dict) -> None:
    """Check the JSON structure of a bank account (API-02)."""
    assert isinstance(account, dict), f"An account object (dict) was expected, got: {type(account)}"
    required_keys = {"id", "customerId", "type", "balance"}
    assert required_keys.issubset(account.keys()), (
        f"Missing keys in the account object: {required_keys - set(account.keys())}"
    )
    assert isinstance(account["id"], int), f"The account id must be an integer, got: {type(account['id'])}"
    assert isinstance(account["type"], str) and len(account["type"]) > 0, (
        f"The account type must be text (e.g. CHECKING/SAVINGS), got: {account['type']}"
    )
    assert isinstance(account["balance"], (int, float)), (
        f"The balance must be a number, got: {type(account['balance'])}"
    )


def assert_loan_response_schema(loan: dict) -> None:
    """Check the JSON structure of a loan request response (API-06)."""
    assert isinstance(loan, dict), "The loan response must be a JSON object"
    assert "approved" in loan, "The 'approved' field is mandatory in the loan response"
    assert isinstance(loan["approved"], bool), "The 'approved' field must be a boolean (True/False)"

    if loan["approved"]:
        assert loan.get("accountId") is not None and isinstance(loan["accountId"], int), (
            "An approved loan must create and return a valid 'accountId'"
        )
    else:
        assert "message" in loan and isinstance(loan["message"], str) and len(loan["message"]) > 0, (
            "A refused loan must give a reason in the 'message' field"
        )
