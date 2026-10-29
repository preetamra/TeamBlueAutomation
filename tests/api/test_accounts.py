import os
import pytest
from api.client import ParaBankClient
from api.schemas import (
    assert_account_schema,
    assert_customer_schema,
    assert_loan_response_schema,
)

USERNAME = os.getenv("PARABANK_USER", "john")
PASSWORD = os.getenv("PARABANK_PASS", "demo")


@pytest.fixture
def api_client():
    """Fournit une instance propre du client API à chaque test."""
    return ParaBankClient()


@pytest.fixture
def customer_session(api_client):
    """Connecte le client connu et récupère son ID ainsi qu'un compte existant."""
    login_resp = api_client.login(USERNAME, PASSWORD)
    assert login_resp.status_code == 200, f"Échec du login initial: {login_resp.text}"
    customer = login_resp.json()
    customer_id = customer["id"]

    accounts_resp = api_client.get_customer_accounts(customer_id)
    assert accounts_resp.status_code == 200
    accounts = accounts_resp.json()
    assert len(accounts) > 0, "Le client doit posséder au moins un compte de base"

    return {
        "customer_id": customer_id,
        "base_account_id": accounts[0]["id"],
        "customer": customer,
    }


def create_checking_account(api_client, customer_session):
    """Crée un compte courant et échoue avec un message clair si ParaBank refuse."""
    resp = api_client.create_account(
        customer_session["customer_id"], 0, customer_session["base_account_id"]
    )
    assert resp.status_code == 200, (
        f"createAccount a échoué ({resp.status_code}): {resp.text}"
    )
    return resp.json()


def assert_ok(response, action):
    """Vérifie un statut 200 et affiche la réponse de ParaBank en cas d'échec."""
    assert response.status_code == 200, (
        f"{action} a échoué ({response.status_code}): {response.text}"
    )


@pytest.fixture
def fresh_account(api_client, customer_session):
    """Crée un compte bancaire neuf et isolé pour garantir l'indépendance en parallèle."""
    return create_checking_account(api_client, customer_session)


@pytest.mark.regression
def test_api_01_login_returns_customer_id_and_name(api_client):
    """API-01 : Connexion valide -> statut 200 + id et nom du client présents."""
    response = api_client.login(USERNAME, PASSWORD)

    assert response.status_code == 200
    body = response.json()
    assert_customer_schema(body)


@pytest.mark.regression
def test_api_02_get_customer_accounts_validates_schema_and_headers(
    api_client, customer_session
):
    """API-02 : Liste des comptes -> Content-Type JSON + validation du schéma de chaque compte."""
    response = api_client.get_customer_accounts(customer_session["customer_id"])

    assert response.status_code == 200
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type.lower(), (
        f"Content-Type JSON attendu, reçu: {content_type}"
    )

    accounts = response.json()
    assert isinstance(accounts, list) and len(accounts) > 0, (
        "La liste des comptes ne doit pas être vide"
    )
    for account in accounts:
        assert_account_schema(account)


@pytest.mark.regression
def test_api_03_create_account_appears_in_customer_account_list(
    api_client, customer_session
):
    """API-03 : Création d'un compte (CRUD Create) -> nouvel ID présent dans la liste du client."""
    create_resp = api_client.create_account(
        customer_id=customer_session["customer_id"],
        new_account_type=1,  # 1 = SAVINGS
        from_account_id=customer_session["base_account_id"],
    )
    assert_ok(create_resp, "createAccount")
    new_account = create_resp.json()
    assert_account_schema(new_account)
    new_account_id = new_account["id"]

    # Vérifie que le nouveau compte apparaît bien dans la liste des comptes du client
    list_resp = api_client.get_customer_accounts(customer_session["customer_id"])
    assert list_resp.status_code == 200
    account_ids = [acc["id"] for acc in list_resp.json()]
    assert new_account_id in account_ids, (
        f"Le nouveau compte {new_account_id} devrait figurer dans {account_ids}"
    )


@pytest.mark.regression
def test_api_04_deposit_increases_balance_by_exact_amount(api_client, fresh_account):
    """API-04 : Dépôt (CRUD Update) -> le solde augmente exactement du montant déposé."""
    account_id = fresh_account["id"]
    # On relit le solde réel via l'API : la réponse de createAccount n'inclut pas
    # le dépôt d'ouverture que ParaBank crédite au nouveau compte.
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
    """API-05 : Virement -> le compte source diminue de X et le compte cible augmente de X."""
    # Création de deux comptes isolés propres à ce test
    source_acc = create_checking_account(api_client, customer_session)
    target_acc = create_checking_account(api_client, customer_session)

    # On crédite le compte source pour garantir les fonds
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
    """API-06 : Demande de prêt -> vérifie le statut d'approbation et le compte créé."""
    # On assure un solde suffisant pour couvrir l'apport (downPayment)
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
    assert loan_data["approved"] is True, f"Le prêt valide aurait dû être approuvé: {loan_data}"


@pytest.mark.parametrize("boundary_amount", [0, 1000000000])
def test_api_07_transfer_boundary_zero_and_very_large_amount(
    api_client, customer_session, boundary_amount
):
    """API-07 : Valeurs limites -> virement de 0 et d'un montant très élevé."""
    source_acc = create_checking_account(api_client, customer_session)
    target_acc = create_checking_account(api_client, customer_session)

    source_before = float(api_client.get_account(source_acc["id"]).json()["balance"])
    target_before = float(api_client.get_account(target_acc["id"]).json()["balance"])

    resp = api_client.transfer(
        from_account_id=source_acc["id"],
        to_account_id=target_acc["id"],
        amount=boundary_amount,
    )
    assert_ok(resp, f"transfer de {boundary_amount}")

    source_after = float(api_client.get_account(source_acc["id"]).json()["balance"])
    target_after = float(api_client.get_account(target_acc["id"]).json()["balance"])

    # La conservation mathématique de l'argent entre les deux comptes doit être respectée
    assert source_before - source_after == pytest.approx(
        target_after - target_before, abs=0.01
    )