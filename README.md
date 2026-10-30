# Team Blue: UI and API Test Automation

Automated tests for the JUNIA M1 Quality Software final project, written in Python with Selenium, requests and pytest.

- **UI tests** run on [demoqa.com](https://demoqa.com). It has every control the brief asks for: text input, number input, text area, file and image upload, dropdown, date picker, dialogs and dynamic elements.
- **API tests** run on ParaBank's REST API (`/parabank/services/bank`), either a local Docker copy or the public site.

The list of every test with its ID, type and last result is in [docs/TEST_INVENTORY.md](docs/TEST_INVENTORY.md). Who wrote what is in [docs/CONTRIBUTIONS.md](docs/CONTRIBUTIONS.md). The investigated failure is in [docs/FAILURE_INVESTIGATION.md](docs/FAILURE_INVESTIGATION.md).

## What you need

- Python 3.10 or newer
- Google Chrome. Selenium downloads the matching driver by itself.
- For the API tests: Docker Desktop (local ParaBank), or an internet connection (public ParaBank)

## Set up (once)

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

## Start ParaBank (API tests only)

**Option A, local Docker copy (what we use for the demo):**

```bash
docker run -d --name parabank -p 8080:8080 parasoft/parabank
```

Wait about a minute, then open http://localhost:8080/parabank to check it answers. `.env` already points `API_URL` at it.

**Option B, public site:** in `.env` set

```
API_URL=https://parabank.parasoft.com/parabank/services/bank
```

The tests log in as ParaBank's built-in demo customer `john` / `demo` and create their own accounts, so they never share data.

The public site sits behind Cloudflare and rate-limits repeated runs: after four or five API runs within a few minutes it answers HTTP 429 ("Error 1015: You are being rate limited") for about a minute. Wait a minute between runs, or use the Docker copy, which has no limit.

## Run the tests

| What | Command |
| --- | --- |
| All tests | `pytest` |
| UI tests only | `pytest tests/ui` |
| API tests only | `pytest tests/api` |
| Regression subset | `pytest -m regression` |
| 4 tests at the same time | `pytest -n 4` |
| With an HTML report | `pytest --html=reports/report.html --self-contained-html` |
| Without browser windows | set `HEADLESS=true` in `.env` |

Combine them, e.g. `pytest -n 4 --html=reports/report.html --self-contained-html`.

### Proof of parallel execution

In a parallel run each result line starts with the worker that ran it (`[gw0]`, `[gw1]`, ...), and several Chrome windows open at once. To compare times:

```bash
time pytest tests/ui          # one test after another
time pytest tests/ui -n 4     # four at a time
```

Tests can run in any order and at the same time because each test gets its own Chrome (`conftest.py`), opens its own page, and the API tests create fresh accounts instead of touching shared ones.

ParaBank's embedded database rejects simultaneous writes, so `api/client.py` serialises the POST calls (create, deposit, transfer, loan) across workers with a file lock and retries a refused `createAccount` up to three times. GET calls stay parallel.

### Reports and evidence

- `reports/report.html`: pass/fail per test, durations, and the error text of failures (open it in a browser).
- `reports/screenshots/<test name>.png`: taken automatically at the failing step of any UI test.
- Data-driven tests appear once per data set in the report, e.g. `test_age_accepts_one_or_two_digits[1]` and `[99]`, or `test_ui10_text_box_accepts_each_data_set[long_name]`.

## Settings

All settings live in `.env`. A real environment variable wins over the file.

| Setting | Default | Meaning |
| --- | --- | --- |
| `BASE_URL` | `https://demoqa.com` | Website for the UI tests |
| `API_URL` | `http://localhost:8080/parabank/services/bank` | ParaBank REST API |
| `PARABANK_USER` / `PARABANK_PASS` | `john` / `demo` | ParaBank's demo customer used by the API tests |
| `HEADLESS` | `false` | `true` runs Chrome without a window |
| `TIMEOUT` | `10` | Longest wait for an element or an API answer, in seconds |

## Project layout

```
config/settings.py      reads the settings
conftest.py             fresh Chrome per test; screenshot when a UI test fails
pages/                  one class per web page: its locators and actions (Page Object Model)
  base_page.py          shared explicit waits and actions (no fixed sleeps)
  home_page.py          demoqa home page
  form_page.py          text box, web tables, select menu, date picker, practice form
  upload_page.py        upload page and the practice form's picture field and validation
  dialog_page.py        browser alerts and the HTML pop-up
  dynamic_page.py       buttons that change after a delay
api/
  client.py             one method per ParaBank endpoint; POSTs serialised across workers
  schemas.py            checks on the JSON shape of customers, accounts and loans
tests/ui/               UI tests
  test_smoke.py         setup check (not one of the graded tests)
  test_form_fields.py   UI-01 to UI-04: text, number, dropdown, date picker
  test_uploads.py       UI-05 to UI-07: file upload, image upload, empty form rejected
  test_dialog_dynamic.py UI-08 to UI-09: confirm dialog, HTML pop-up, dynamic element
  test_data_driven.py   UI-10: text box with five data sets read from data/form_data.csv
tests/api/
  test_accounts.py      API-01 to API-07: login, accounts, create, deposit, transfer, loan, boundaries
  test_negative.py      API-N1 to API-N3: wrong password, unknown account, non-numeric amount
data/form_data.csv      the data sets of the data-driven test UI-10 (one line per case)
data/files/             files the upload tests send (a PDF and a PNG)
docs/                   test inventory, contribution record, failure investigation
reports/                HTML reports and failure screenshots (not committed)
```

## Adding a UI test (team guide)

1. Make a page class in `pages/` that extends `BasePage`. Set its `path` and put its locators at the top as constants.
2. Write the test in `tests/ui/test_<area>.py`. Ask for the `driver` fixture; each test gets its own browser.
3. Use `find`, `click`, `fill` and `text_of` from `BasePage`. Never `time.sleep`.
4. Assert the result on the page, not only that nothing crashed.
5. Add a line for it in `docs/TEST_INVENTORY.md`.

## How we work with git (team guide)

First time: accept the GitHub invite you received by email, then download the code:

```bash
git clone https://github.com/preetamra/TeamBlueAutomation.git
```

Every time you work:

1. `git pull` to get everyone's latest code before you start.
2. Change only your own files. Shared files (`conftest.py`, `pytest.ini`, `requirements.txt`, `README.md`): tell the team before you edit them, so two people don't change the same lines.
3. Run `pytest` and commit only when your tests pass.
4. Save and upload:

```bash
git add <your files>
git commit -m "Add form field tests UI-01 to UI-04"
git pull --rebase
git push
```

If `git push` is refused, run `git pull --rebase` and push again. If git reports a conflict, stop and ask the team.
