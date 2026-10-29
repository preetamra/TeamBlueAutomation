# Test inventory

Every automated test, with its ID, type, expected result and the result of the last full run. Test functions are in `tests/ui` and `tests/api`; data-driven tests list one line per data set.

Last full run: 29 October 2026 (evening), macOS, Chrome headless, `pytest -n 2`, 29 tests in 81 s (UI on demoqa.com, API on the public ParaBank because Docker was not available): 28 passed, 1 failed (API-06, see below). Report: `reports/report.html`.

## UI tests (demoqa.com)

| ID | Test | Type | Expected result | Status |
| --- | --- | --- | --- | --- |
| UI-00 | `test_home_page_shows_the_sections_we_test` | Setup check (not graded) | Home page lists Elements, Forms, Alerts/Frame/Windows, Widgets | Pass |
| UI-01 | `test_text_box_displays_submitted_name_and_address` | Positive, text input + text area, state check | Submitted name and address are shown under the form | Pass |
| UI-02a | `test_age_field_accepts_digits` | Positive, number input | Age field holds `25` | Pass |
| UI-02b | `test_age_field_rejects_letters_on_submit` | Negative, field validation | Form stays open and the age field is invalid | Pass |
| UI-02c | `test_age_accepts_one_or_two_digits[1]` | Boundary, data-driven | `1` accepted and valid | Pass |
| UI-02d | `test_age_accepts_one_or_two_digits[99]` | Boundary, data-driven | `99` accepted and valid | Pass |
| UI-02e | `test_age_input_limits_entry_to_two_characters` | Boundary | Typing `123` leaves `12` | Pass |
| UI-03a | `test_dropdown_displays_selected_color` | Positive, dropdown | Selected option reads `Blue` | Pass |
| UI-03b | `test_dropdown_values_appear_after_form_submission` | Positive, dynamic dropdown + dialog, state check | Result dialog shows `NCR` and `Delhi` | Pass |
| UI-04a | `test_date_picker_displays_valid_date` | Positive, date picker | Field shows `06/15/2020` | Pass (failed on macOS before the fix, see `FAILURE_INVESTIGATION.md`) |
| UI-04b | `test_date_picker_does_not_keep_invalid_date` | Negative, date validation | `02/30/2024` is not kept | Pass |
| UI-05 | `test_upload_shows_the_name_of_the_uploaded_pdf` | Positive, file upload, file validation | Uploaded file name `sample.pdf` is shown under the field | Pass |
| UI-06 | `test_form_accepts_a_png_picture_and_shows_its_name` | Positive, image upload, state check | Confirmation lists `photo.png` | Pass |
| UI-07 | `test_form_with_empty_required_fields_is_rejected` | Negative, failure-oriented, error handling | First Name, Last Name, Gender, Mobile marked invalid; no confirmation | Pass |
| UI-08a | `test_confirm_dialog_shows_the_answer_on_the_page[ok]` | Dialog (browser confirm), positive | Question is `Do you confirm action?`, page shows `You selected Ok` | Pass |
| UI-08b | `test_confirm_dialog_shows_the_answer_on_the_page[cancel]` | Dialog, data-driven | Page shows `You selected Cancel` | Pass |
| UI-08c | `test_html_popup_shows_its_text_and_closes` | Dialog (HTML pop-up), state check | Title `Small Modal`, text shown, pop-up really closes | Pass |
| UI-09 | `test_delayed_buttons_become_enabled_and_visible` | Dynamic element, explicit wait | Disabled button becomes enabled, hidden button appears after 5 s | Pass |
| UI-10a | `test_ui10_text_box_accepts_each_data_set[standard_user]` | Data-driven, positive | Name, email and address typed in come back unchanged under the form | Pass (29 Oct, réel) |
| UI-10b | `test_ui10_text_box_accepts_each_data_set[long_name]` | Data-driven, boundary (64-character name) | The long name is shown in full | Pass (29 Oct, réel) |
| UI-10c | `test_ui10_text_box_accepts_each_data_set[special_characters]` | Data-driven, special characters | Accents, apostrophe and `&` are shown as typed | Pass (29 Oct, réel) |
| UI-10d | `test_ui10_text_box_accepts_each_data_set[missing_email]` | Data-driven, empty optional field | Name and address shown, no email value | Pass (29 Oct, réel) |
| UI-10e | `test_ui10_text_box_accepts_each_data_set[long_address]` | Data-driven, boundary (long text area) | The full address is shown | Pass (29 Oct, réel) |

UI-10 ran on 29 October 2026 against the real demoqa.com (Windows, Chrome 156 headless): 5 passed in 33.8 s. One data set had to change first: demoqa refuses an email containing `+`, so `lea+qa@example.com` blocked the submission. The address became `lea.qa@example.com`; the test and its assertions were not touched. Same session, whole UI suite: 23 passed in 174 s serially, 23 passed in 137 s with `-n 4` (the site's own response time is the bottleneck, not the framework).

## API tests (ParaBank REST API)

| ID | Test | Type | Expected result | Status |
| --- | --- | --- | --- | --- |
| API-01 | `test_api_01_login_returns_customer_id_and_name` | Status code, schema, auth | 200 and a customer object with id, firstName, lastName | Pass |
| API-02 | `test_api_02_get_customer_accounts_validates_schema_and_headers` | Headers, schema | 200, JSON content type, every account matches the schema | Pass |
| API-03 | `test_api_03_create_account_appears_in_customer_account_list` | CRUD create, data validation | New account id appears in the customer's list | Pass |
| API-04 | `test_api_04_deposit_increases_balance_by_exact_amount` | CRUD update, data validation | Balance rises by exactly 250.00 | Pass |
| API-05 | `test_api_05_transfer_moves_exact_amount_between_two_accounts` | Data validation, state check | Source down by 125.50, target up by 125.50 | Pass |
| API-06 | `test_api_06_request_loan_returns_decision_and_creates_account_when_approved` | Schema, business rule | 200, `approved` true, account id returned | Fail on the public site (HTTP 500, its loan service is down, reproduced with curl). Docker copy: _to run_ |
| API-07a | `test_api_07_transfer_boundary_zero_and_very_large_amount[0]` | Boundary | Transfer of 0 accepted, money conserved between accounts | Pass |
| API-07b | `test_api_07_transfer_boundary_zero_and_very_large_amount[1000000000]` | Boundary | Money conserved; ParaBank accepts it and leaves the source at −999 999 900, no balance check (application defect, noted in the test) | Pass |
| API-N1 | `test_api_n1_login_with_wrong_password_returns_error_and_no_customer_data` | Negative, auth, error handling | Error status, no customer data in the body | Pass |
| API-N2 | `test_api_n2_get_non_existent_account_returns_clear_error` | Negative, error handling | Error status with a message | Pass |
| API-N3 | `test_api_n3_deposit_with_text_amount_is_refused` | Negative, data validation | Error status for amount `abc` | Pass |

Totals for the run: 28 passed, 1 failed (API-06, environment issue on the public site). UI tests: 17 graded tests pass (UI-01 to UI-09), plus the setup check; UI-10 is still to come.
