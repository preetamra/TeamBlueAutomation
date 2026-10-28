import os
import requests
from dotenv import load_dotenv

load_dotenv()


class ParaBankClient:
    """Client centralisé pour interagir avec l'API REST de ParaBank."""

    def __init__(self):
        self.base_url = os.getenv(
            "API_URL", "http://localhost:8080/parabank/services/bank"
        ).rstrip("/")
        self.timeout = int(os.getenv("TIMEOUT", "10"))
        self.session = requests.Session()
        # ParaBank renvoie du XML par défaut ; on demande explicitement du JSON
        self.session.headers.update({"Accept": "application/json"})

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def login(self, username: str, password: str) -> requests.Response:
        """API-01 & API-N1 : Authentification d'un client."""
        return self.session.get(
            self._url(f"login/{username}/{password}"),
            timeout=self.timeout,
        )

    def get_customer_accounts(self, customer_id: int) -> requests.Response:
        """API-02 : Récupère la liste de tous les comptes d'un client."""
        return self.session.get(
            self._url(f"customers/{customer_id}/accounts"),
            timeout=self.timeout,
        )

    def get_account(self, account_id: int) -> requests.Response:
        """API-N2 : Récupère les détails d'un compte précis par son ID."""
        return self.session.get(
            self._url(f"accounts/{account_id}"),
            timeout=self.timeout,
        )

    def create_account(
        self, customer_id: int, new_account_type: int, from_account_id: int
    ) -> requests.Response:
        """API-03 : Crée un nouveau compte bancaire (0 = CHECKING, 1 = SAVINGS)."""
        params = {
            "customerId": customer_id,
            "newAccountType": new_account_type,
            "fromAccountId": from_account_id,
        }
        return self.session.post(
            self._url("createAccount"),
            params=params,
            timeout=self.timeout,
        )

    def deposit(self, account_id: int, amount) -> requests.Response:
        """API-04 & API-N3 : Dépose un montant sur un compte."""
        params = {"accountId": account_id, "amount": amount}
        return self.session.post(
            self._url("deposit"),
            params=params,
            timeout=self.timeout,
        )

    def transfer(
        self, from_account_id: int, to_account_id: int, amount
    ) -> requests.Response:
        """API-05 & API-07 : Transfère de l'argent d'un compte source vers un compte cible."""
        params = {
            "fromAccountId": from_account_id,
            "toAccountId": to_account_id,
            "amount": amount,
        }
        return self.session.post(
            self._url("transfer"),
            params=params,
            timeout=self.timeout,
        )

    def request_loan(
        self, customer_id: int, amount, down_payment, from_account_id: int
    ) -> requests.Response:
        """API-06 : Envoie une demande de prêt bancaire."""
        params = {
            "customerId": customer_id,
            "amount": amount,
            "downPayment": down_payment,
            "fromAccountId": from_account_id,
        }
        return self.session.post(
            self._url("requestLoan"),
            params=params,
            timeout=self.timeout,
        )