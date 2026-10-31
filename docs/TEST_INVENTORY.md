# Test inventory

Every automated test, with its ID, type, expected result and the result of the last full run. Test functions are in `tests/ui` and `tests/api`; data-driven tests list one line per data set.

Last full run: 31 October 2026 (afternoon), macOS, Chrome headless, `pytest -n 4`, 37 tests in 55 s (UI on demoqa.com, API on the public ParaBank): **37 passed**. Report committed as `evidence/report_2026-10-31_n4_37_passed.html`, console log with the worker ids as `evidence/console_n4_2026-10-31.txt`. Earlier runs: 30 October, 34 tests, 34 passed (`evidence/report_2026-10-30_n2_34_passed.html`); 29 October, 29 tests, 28 passed, API-06 failed with HTTP 500 on the public site and UI-04a failed on macOS (`evidence/report_2026-10-29_2_failed.html`). The public ParaBank rate-limits (HTTP 429) after about four API runs in ten minutes; the runs above were spaced out.

## UI tests (demoqa.com)

| ID | Test | Type | Expected result | Status |
| --- | --- | --- | --- | --- |
| UI-00 | `test_home_page_shows_the_sections_we_test` | Setup check (not graded) | Home page lists Elements, Forms, Alerts/Frame/Windows, Widgets | Pass |
| UI-01 | `test_text_box_displays_submitted_name_and_address` | Positive, text input + text area, state check | Submitted name and address are shown under the form | Pass |
| UI-01b | `test_text_box_edit_and_clear_update_the_output` | Positive, text input edit and clear, state check | A second submit shows the new name; clearing the address removes its line under the form | Pass (31 Oct) |
| UI-02a | `test_age_field_accepts_digits` | Positive, number input, state check | Age 25 accepted: the dialog closes and the new record is in the table | Pass |
| UI-02b | `test_age_field_rejects_letters_on_submit` | Negative, field validation | Form stays open, Age field invalid, no record added to the table | Pass |
| UI-02c | `test_age_accepts_one_or_two_digits[1]` | Boundary, data-driven | `1` accepted and valid | Pass |
| UI-02d | `test_age_accepts_one_or_two_digits[99]` | Boundary, data-driven | `99` accepted and valid | Pass |
| UI-02e | `test_age_input_limits_entry_to_two_characters` | Boundary | Typing `123` leaves `12` | Pass |
| UI-03a | `test_dropdown_displays_selected_color` | Positive, dropdown | Selected option reads `Blue` | Pass |
| UI-03b | `test_dropdown_values_appear_after_form_submission` | Positive, dynamic dropdown + dialog, state check | Result dialog shows `NCR` and `Delhi` | Pass |
| UI-04a | `test_date_picker_displays_valid_date` | Positive, date picker | Field shows `06/15/2020` | Pass (failed on macOS before the fix, see `FAILURE_INVESTIGATION.md`) |
| UI-04b | `test_date_picker_does_not_keep_invalid_date` | Negative, date validation | 06/15/2020 is kept, 02/30/2024 is refused and the field still shows 06/15/2020 | Pass |
| UI-05 | `test_upload_shows_the_name_of_the_uploaded_pdf` | Positive, file upload, file validation | Uploaded file name `sample.pdf` is shown under the field. demoqa has no file-type restriction (no accept attribute, no server check), so rejecting an unsupported file cannot be tested there; UI-07 is the rejection test | Pass |
| UI-06 | `test_form_accepts_a_png_picture_and_shows_its_name` | Positive, image upload, state check | Confirmation lists `photo.png` | Pass |
| UI-07 | `test_form_with_empty_required_fields_is_rejected` | Negative, failure-oriented, error handling | First Name, Last Name, Gender, Mobile marked invalid; no confirmation | Pass |
| UI-08a | `test_confirm_dialog_shows_the_answer_on_the_page[ok]` | Dialog (browser confirm), positive | Question is `Do you confirm action?`, page shows `You selected Ok` | Pass |
| UI-08b | `test_confirm_dialog_shows_the_answer_on_the_page[cancel]` | Dialog, data-driven | Page shows `You selected Cancel` | Pass |
| UI-08c | `test_html_popup_shows_its_text_and_closes` | Dialog (HTML pop-up), state check | Title `Small Modal`, text shown, pop-up really closes | Pass |
| UI-09 | `test_delayed_buttons_become_enabled_and_visible` | Dynamic element, explicit wait | Disabled button becomes enabled, hidden button appears after 5 s | Pass |
| UI-10a | `test_ui10_text_box_accepts_each_data_set[standard_user]` | Data-driven, positive | Name, email and address typed in come back unchanged under the form | Pass |
| UI-10b | `test_ui10_text_box_accepts_each_data_set[long_name]` | Data-driven, boundary (64-character name) | The long name is shown in full | Pass |
| UI-10c | `test_ui10_text_box_accepts_each_data_set[special_characters]` | Data-driven, special characters | Accents, apostrophe and `&` are shown as typed | Pass |
| UI-10d | `test_ui10_text_box_accepts_each_data_set[missing_email]` | Data-driven, empty optional field | Name and address shown, no email value | Pass |
| UI-10e | `test_ui10_text_box_accepts_each_data_set[long_address]` | Data-driven, boundary (long text area) | The full address is shown | Pass |
| UI-10f | `test_ui10_text_box_accepts_each_data_set[multi_line_address]` | Data-driven, text area multi-line | Both lines of the address are shown | Pass (31 Oct) |
| UI-10g | `test_ui10_text_box_accepts_each_data_set[plus_in_email]` | Data-driven, negative (email with `+`) | The email field is marked invalid and nothing is shown under the form | Pass (31 Oct) |

UI-10 ran on 29 October 2026 against the real demoqa.com (Windows, Chrome 156 headless): 5 passed in 33.8 s. One data set had to change first: demoqa refuses an email containing `+`, so `lea+qa@example.com` blocked the submission. The email became `lea.qa@example.com`; the test and its assertions were not touched. On 31 October the `+` email came back as a negative data set that expects the rejection (UI-10g), and a two-line address was added for the text area (UI-10f). Same session, whole UI suite: 23 passed in 174 s serially, 23 passed in 137 s with `-n 4` (the site's own response time is the bottleneck, not the framework).

## API tests (ParaBank REST API)

| ID | Test | Method and endpoint | Type | Expected result | Status |
| --- | --- | --- | --- | --- | --- |
| API-01 | `test_api_01_login_returns_customer_id_and_name` | `GET login/{user}/{password}` | Status code, schema, auth | 200 and a customer object with id, firstName, lastName | Pass |
| API-02 | `test_api_02_get_customer_accounts_validates_schema_and_headers` | `GET customers/{id}/accounts` | Headers, schema | 200, JSON content type, every account matches the schema | Pass |
| API-03 | `test_api_03_create_account_appears_in_customer_account_list` | `POST createAccount` | CRUD create, data validation | New account id appears in the customer's list, type SAVINGS, owned by the customer | Pass |
| API-04 | `test_api_04_deposit_increases_balance_by_exact_amount` | `POST deposit` | CRUD update, data validation | Balance rises by exactly 250.00 | Pass |
| API-05 | `test_api_05_transfer_moves_exact_amount_between_two_accounts` | `POST transfer` | Data validation, state check | Source down by 125.50, target up by 125.50 | Pass |
| API-06 | `test_api_06_request_loan_returns_decision_and_creates_account_when_approved` | `POST requestLoan` | Schema, business rule | 200, `approved` true, the loan account exists and belongs to the customer | Pass (30 Oct, public site). On 29 Oct the public loan service answered HTTP 500, reproduced with curl; see `FAILURE_INVESTIGATION.md` |
| API-07a | `test_api_07_transfer_boundary_zero_and_very_large_amount[0]` | `POST transfer (amount 0)` | Boundary | Transfer of 0 accepted, money conserved between accounts | Pass |
| API-07b | `test_api_07_transfer_boundary_zero_and_very_large_amount[1000000000]` | `POST transfer (amount 1 000 000 000)` | Boundary | Money conserved; ParaBank accepts it and leaves the source at −999 999 900, no balance check (application defect, noted in the test) | Pass |
| API-N1 | `test_api_n1_login_with_wrong_password_returns_error_and_no_customer_data` | `GET login/{user}/{wrong password}` | Negative, auth, error handling | 4xx (observed 400 `Invalid username and/or password`), no customer data in the body | Pass |
| API-N2 | `test_api_n2_get_non_existent_account_returns_clear_error` | `GET accounts/999999999` | Negative, error handling | 4xx (observed 400) and the message names the account id | Pass |
| API-N3 | `test_api_n3_deposit_with_text_amount_is_refused` | `POST deposit (amount abc)` | Negative, data validation | 4xx for amount `abc` (observed 404 with an empty body: JAX-RS cannot convert the parameter), nothing deposited | Pass |

Totals for the run: 37 passed, 0 failed. UI: 10 test cases, 25 runs (UI-01 to UI-10 with their data sets), plus the setup check. API: 10 test cases, 11 runs (API-01 to API-07, API-N1 to API-N3).

Preconditions for every API test: login as the public demo customer (`PARABANK_USER` / `PARABANK_PASS`); every account that receives a write is created by the test itself with `POST createAccount`; request parameters are in the test body and in `api/client.py`; the request line, the status and the start of the body of every call are printed into the HTML report (request and response evidence, password masked).
