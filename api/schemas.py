def assert_customer_schema(data: dict) -> None:
    """Vérifie la structure JSON d'un client (API-01)."""
    assert isinstance(data, dict), f"Un dictionnaire JSON était attendu, reçu: {type(data)}"
    required_keys = {"id", "firstName", "lastName"}
    assert required_keys.issubset(data.keys()), (
        f"Clés manquantes dans le profil client : {required_keys - set(data.keys())}"
    )
    assert isinstance(data["id"], int), "L'id du client doit être un nombre entier"
    assert isinstance(data["firstName"], str) and len(data["firstName"]) > 0, (
        "Le prénom du client doit être une chaîne non vide"
    )
    assert isinstance(data["lastName"], str) and len(data["lastName"]) > 0, (
        "Le nom du client doit être une chaîne non vide"
    )


def assert_account_schema(account: dict) -> None:
    """Vérifie la structure JSON d'un compte bancaire (API-02)."""
    assert isinstance(account, dict), f"Un objet compte (dict) était attendu, reçu: {type(account)}"
    required_keys = {"id", "customerId", "type", "balance"}
    assert required_keys.issubset(account.keys()), (
        f"Clés manquantes dans l'objet compte : {required_keys - set(account.keys())}"
    )
    assert isinstance(account["id"], int), f"L'id du compte doit être un entier, reçu: {type(account['id'])}"
    assert isinstance(account["type"], str) and len(account["type"]) > 0, (
        f"Le type du compte doit être du texte (ex: CHECKING/SAVINGS), reçu: {account['type']}"
    )
    assert isinstance(account["balance"], (int, float)), (
        f"Le solde (balance) doit être un nombre, reçu: {type(account['balance'])}"
    )


def assert_loan_response_schema(loan: dict) -> None:
    """Vérifie la structure JSON d'une réponse de demande de prêt (API-06)."""
    assert isinstance(loan, dict), "La réponse de prêt doit être un objet JSON"
    assert "approved" in loan, "Le champ 'approved' est obligatoire dans la réponse de prêt"
    assert isinstance(loan["approved"], bool), "Le champ 'approved' doit être un booléen (True/False)"

    if loan["approved"]:
        assert loan.get("accountId") is not None and isinstance(loan["accountId"], int), (
            "Un prêt approuvé doit créer et retourner un 'accountId' valide"
        )
    else:
        assert "message" in loan and isinstance(loan["message"], str) and len(loan["message"]) > 0, (
            "Un prêt refusé doit fournir une raison dans le champ 'message'"
        )