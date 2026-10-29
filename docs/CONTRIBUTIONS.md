# Contribution record

Who wrote what, and what each person can explain or change live. One line per file, so the teacher can match names to code (`git log` shows the same authors).

| Member | Area | Files written | Can explain live |
| --- | --- | --- | --- |
| Preetam Rangadal (QA lead) | Framework and delivery | `conftest.py`, `config/settings.py`, `pages/base_page.py`, `pages/home_page.py`, `tests/ui/test_smoke.py`, `pytest.ini`, `requirements.txt`, `.env.example`, `README.md`, `docs/*` | Project setup, driver fixture, explicit waits, parallel run and reports, the failure investigation, the slides and the email to the teacher |
| Abdul Manan Omichessan | UI form fields (UI-01 to UI-04) | `pages/form_page.py`, `tests/ui/test_form_fields.py` | Text box, number field validation and boundaries, dropdowns, date picker; the page objects behind them |
| Imène Houlla | UI uploads, dialog, dynamic elements (UI-05 to UI-09) | `pages/upload_page.py`, `pages/dialog_page.py`, `pages/dynamic_page.py`, `tests/ui/test_uploads.py`, `tests/ui/test_dialog_dynamic.py`, `data/files/` | File and image upload, alert/confirm dialogs, dynamic element waits, the failure-oriented test |
| Frédérique Ransau | API tests (API-01 to API-07, API-N1 to API-N3) | `api/client.py`, `api/schemas.py`, `tests/api/test_accounts.py`, `tests/api/test_negative.py` | ParaBank client, schema checks, CRUD and transfer tests, negative tests, fresh accounts per test |
| Baye Cheikh Cissé | Data-driven test, parallel run, inventory (UI-10) | `tests/ui/test_data_driven.py`, `data/form_data.csv`, `docs/TEST_INVENTORY.md`, and the optional email field added to `pages/form_page.py` | Data-driven test with several data sets, parallel execution proof, the test inventory |

Each member keeps this table up to date for their own row.
