import os
import tempfile
import time

import requests
from dotenv import load_dotenv
from filelock import FileLock

load_dotenv()

# Verrou partagé entre les workers pytest-xdist (ce sont des processus distincts).
# ParaBank (base de données embarquée) supporte mal les écritures simultanées :
# on sérialise donc toutes les requêtes qui modifient des données (POST).
# Les lectures (GET) restent exécutées en parallèle.
_WRITE_LOCK = FileLock(
    os.path.join(tempfile.gettempdir(), "parabank_write.lock"), timeout=60
)


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

    def _post(self, path: str, params: dict) -> requests.Response:
        """Envoie un POST en le sérialisant avec les autres workers."""
        with _WRITE_LOCK:
            return self.session.post(
                self._url(path), params=params, timeout=self.timeout
            )

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
        """API-03 : Crée un compte (0 = CHECKING, 1 = SAVINGS).

        La création débite le compte source : elle est sérialisée avec les autres
        écritures et réessayée jusqu'à 3 fois si ParaBank la refuse.
        """
        params = {
            "customerId": customer_id,
            "newAccountType": new_account_type,
            "fromAccountId": from_account_id,
        }
        with _WRITE_LOCK:
            response = None
            for attempt in range(3):
                response = self.session.post(
                    self._url("createAccount"), params=params, timeout=self.timeout
                )
                if response.status_code == 200:
                    return response
                time.sleep(0.5 * (attempt + 1))
            return response

    def deposit(self, account_id: int, amount) -> requests.Response:
        """API-04 & API-N3 : Dépose un montant sur un compte."""
        return self._post("deposit", {"accountId": account_id, "amount": amount})

    def transfer(
        self, from_account_id: int, to_account_id: int, amount
    ) -> requests.Response:
        """API-05 & API-07 : Transfère de l'argent d'un compte source vers un compte cible."""
        return self._post(
            "transfer",
            {
                "fromAccountId": from_account_id,
                "toAccountId": to_account_id,
                "amount": amount,
            },
        )

    def request_loan(
        self, customer_id: int, amount, down_payment, from_account_id: int
    ) -> requests.Response:
        """API-06 : Envoie une demande de prêt bancaire."""
        return self._post(
            "requestLoan",
            {
                "customerId": customer_id,
                "amount": amount,
                "downPayment": down_payment,
                "fromAccountId": from_account_id,
            },
        )