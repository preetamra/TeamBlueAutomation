# Team Blue: UI and API Test Automation

Automated tests for the JUNIA M1 Quality Software final project, written in Python with Selenium and pytest.

- **UI tests** run on [demoqa.com](https://demoqa.com).
- **API tests** run on ParaBank's REST API, using a local Docker copy (coming soon).

## What you need

- Python 3.10 or newer
- Google Chrome. Selenium downloads the matching driver by itself.
- Docker Desktop, only for the API tests

## Set up (once)

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

## Run the tests

| What | Command |
| --- | --- |
| All tests | `pytest` |
| UI tests only | `pytest tests/ui` |
| 4 tests at the same time | `pytest -n 4` |
| With an HTML report | `pytest --html=reports/report.html --self-contained-html` |
| Without browser windows | set `HEADLESS=true` in `.env` |

In a parallel run, each result line shows which worker ran the test (`[gw0]`, `[gw1]`, ...).

## Settings

All settings live in `.env`. A real environment variable wins over the file.

| Setting | Default | Meaning |
| --- | --- | --- |
| `BASE_URL` | `https://demoqa.com` | Website for the UI tests |
| `API_URL` | `http://localhost:8080/parabank/services/bank` | ParaBank REST API |
| `HEADLESS` | `false` | `true` runs Chrome without a window |
| `TIMEOUT` | `10` | Longest wait for an element, in seconds |

## Project layout

```
config/settings.py   reads the settings
conftest.py          gives each test its own fresh Chrome and closes it afterwards
pages/               one class per web page: its locators and actions
  base_page.py       shared waits and actions (no fixed sleeps)
  home_page.py       demoqa home page
tests/ui/            UI tests
  test_smoke.py      setup check: Chrome starts and the site answers
```

## Adding a UI test (team guide)

1. Make a page class in `pages/` that extends `BasePage`. Set its `path` and put its locators at the top as constants.
2. Write the test in `tests/ui/test_<area>.py`. Ask for the `driver` fixture; each test gets its own browser.
3. Use `find`, `click`, `fill` and `text_of` from `BasePage`. Never `time.sleep`.
4. Assert the result on the page, not only that nothing crashed.
