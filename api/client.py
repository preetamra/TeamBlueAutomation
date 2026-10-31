import os
import re
import tempfile
import time

import requests
from dotenv import load_dotenv
from filelock import FileLock

load_dotenv()

# Lock shared between the pytest-xdist workers (they are separate processes).
# ParaBank (embedded database) handles concurrent writes badly, so every request
# that modifies data (POST) is serialised. Reads (GET) still run in parallel.
_WRITE_LOCK = FileLock(
    os.path.join(tempfile.gettempdir(), "parabank_write.lock"), timeout=60
)


def _log_response(response, *args, **kwargs):
    """Evidence for the HTML report: one line per call. pytest captures stdout,
    so the lines show up in the report of the test that made the call."""
    # Hide the password of GET /login/{username}/{password}
    masked_url = re.sub(r"(/login/[^/]+/)[^/?]+", r"\1***", response.url)
    body = " ".join(response.text[:200].split())
    print(f"{response.request.method} {masked_url} -> {response.status_code} {body}")


class ParaBankClient:
    """Single entry point for the ParaBank REST API."""

    def __init__(self):
        self.base_url = os.getenv(
            "API_URL", "https://parabank.parasoft.com/parabank/services/bank"
        ).rstrip("/")
        self.timeout = int(os.getenv("TIMEOUT", "10"))
        self.session = requests.Session()
        # ParaBank answers in XML by default; ask explicitly for JSON
        self.session.headers.update({"Accept": "application/json"})
        self.session.hooks["response"].append(_log_response)

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _post(self, path: str, params: dict) -> requests.Response:
        """Send a POST, serialised with the other workers."""
        with _WRITE_LOCK:
            return self.session.post(
                self._url(path), params=params, timeout=self.timeout
            )

    def login(self, username: str, password: str) -> requests.Response:
        """API-01 & API-N1: authenticate a customer."""
        return self.session.get(
            self._url(f"login/{username}/{password}"),
            timeout=self.timeout,
        )

    def get_customer_accounts(self, customer_id: int) -> requests.Response:
        """API-02: list all the accounts of a customer."""
        return self.session.get(
            self._url(f"customers/{customer_id}/accounts"),
            timeout=self.timeout,
        )

    def get_account(self, account_id: int) -> requests.Response:
        """API-N2: get the details of one account by its id."""
        return self.session.get(
            self._url(f"accounts/{account_id}"),
            timeout=self.timeout,
        )

    def create_account(
        self, customer_id: int, new_account_type: int, from_account_id: int
    ) -> requests.Response:
        """API-03: create an account (0 = CHECKING, 1 = SAVINGS).

        Creating an account debits the source account: the call is serialised with
        the other writes and retried up to 3 times when ParaBank fails (HTTP 5xx).
        A 4xx, including a 429 rate limit, is returned as is: a retry would not fix it.
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
                if response.status_code < 500:
                    return response
                time.sleep(0.5 * (attempt + 1))
            return response

    def deposit(self, account_id: int, amount) -> requests.Response:
        """API-04 & API-N3: deposit an amount on an account."""
        return self._post("deposit", {"accountId": account_id, "amount": amount})

    def transfer(
        self, from_account_id: int, to_account_id: int, amount
    ) -> requests.Response:
        """API-05 & API-07: move money from a source account to a target account."""
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
        """API-06: send a loan request."""
        return self._post(
            "requestLoan",
            {
                "customerId": customer_id,
                "amount": amount,
                "downPayment": down_payment,
                "fromAccountId": from_account_id,
            },
        )
