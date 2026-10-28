import os
import pytest
from api.client import ParaBankClient

USERNAME = os.getenv("PARABANK_USER", "john")


@pytest.fixture
def api_client():
    return ParaBankClient()


def test_api_n1_login_with_wrong_password_returns_error_and_no_customer_data(
    api_client,
):
    """API-N1 : Connexion avec un mauvais mot de passe -> statut d'erreur et aucune donnée client."""
    response = api_client.login(USERNAME, "wrong_password_99999")

    assert response.status_code >= 400, (
        f"Un code d'erreur HTTP (>=400) était attendu, reçu: {response.status_code}"
    )
    assert len(response.text.strip()) > 0, "Un message d'erreur doit être retourné"
    assert "firstName" not in response.text, (
        "Aucune donnée personnelle du client ne doit être exposée en cas d'échec"
    )


def test_api_n2_get_non_existent_account_returns_clear_error(api_client):
    """API-N2 : Consultation d'un compte inexistant -> statut d'erreur et message clair."""
    non_existent_id = 999999999
    response = api_client.get_account(non_existent_id)

    assert response.status_code >= 400, (
        f"Un code d'erreur HTTP (>=400) était attendu pour un compte inexistant, reçu: {response.status_code}"
    )
    assert len(response.text.strip()) > 0, "Le message d'erreur ne doit pas être vide"


def test_api_n3_deposit_with_text_amount_is_refused(api_client):
    """API-N3 : Dépôt avec un montant texte ('abc') -> la requête est refusée avec une erreur."""
    response = api_client.deposit(account_id=12345, amount="abc")

    assert response.status_code >= 400, (
        f"Un montant non numérique ('abc') doit être rejeté avec un code >=400, reçu: {response.status_code}"
    )