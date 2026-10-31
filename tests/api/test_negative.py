import os

USERNAME = os.getenv("PARABANK_USER", "john")


def test_api_n1_login_with_wrong_password_returns_error_and_no_customer_data(
    api_client,
):
    """API-N1: login with a wrong password -> 4xx error and no customer data."""
    response = api_client.login(USERNAME, "wrong_password_99999")

    assert 400 <= response.status_code < 500, (
        f"A 4xx client error was expected, got: {response.status_code}"
    )
    assert len(response.text.strip()) > 0, "An error message must be returned"
    assert "firstName" not in response.text, (
        "No personal customer data may be exposed when the login fails"
    )


def test_api_n2_get_non_existent_account_returns_clear_error(api_client):
    """API-N2: reading an account that does not exist -> 4xx error naming the account."""
    non_existent_id = 999999999
    response = api_client.get_account(non_existent_id)

    assert 400 <= response.status_code < 500, (
        f"A 4xx client error was expected for an unknown account, got: {response.status_code}"
    )
    assert str(non_existent_id) in response.text, (
        f"The error message should name the unknown account {non_existent_id}: {response.text}"
    )


def test_api_n3_deposit_with_text_amount_is_refused(api_client, customer_session):
    """API-N3: deposit with a text amount ('abc') -> the request is refused with a 4xx error.

    Observed ParaBank behaviour (31 Oct 2026): 404 with an empty body. JAX-RS answers
    404 when a query parameter cannot be converted (here 'abc' into a number).
    """
    response = api_client.deposit(
        account_id=customer_session["base_account_id"], amount="abc"
    )

    assert 400 <= response.status_code < 500, (
        f"A non-numeric amount ('abc') must be rejected with a 4xx, got: {response.status_code}"
    )
    # Nothing was processed: no success message and no account data in the answer
    assert "Successfully deposited" not in response.text, (
        f"The deposit must not be processed: {response.text}"
    )
    assert "balance" not in response.text, (
        f"No account data is expected in a refusal: {response.text}"
    )
