# Failure investigation: the date picker test fails on macOS

A real failure from our own runs, found on 29 October 2026 when the lead ran the whole suite for the first time on a Mac (4 workers, headless). The test had passed on its author's Windows laptop.

## What failed

`tests/ui/test_form_fields.py::test_date_picker_displays_valid_date` (UI-04a)

```
assert page.selected_date() == "06/15/2020"
AssertionError: assert '10/29/2026' == '06/15/2020'
```

The field ended with `10/29/2026`, the date of the run. That is the picker's starting value, so the date we typed was never accepted.

## Cause category

**Environment (operating system), through a test-code assumption.** Not an application defect, not a locator problem, not timing.

## How we investigated

1. **Read the failure.** The value was today's date, so the page had rejected our input and fallen back to its default.
2. **Ruled out parallel execution.** Ran the test alone, not in parallel: still failed. So no clash with other tests.
3. **Read the page action.** `DatePickerPage.enter_date` sent `Ctrl+A`, then the date, then `Enter`, to replace the existing text.
4. **Checked the platform.** On macOS, `Ctrl+A` in a text field moves the cursor to the start of the line; only `Cmd+A` selects everything. So the typed date was inserted in front of the old one, giving `06/15/202010/29/2026`. The React date picker cannot parse that, so on `Enter` it kept the previous date.
5. **Confirmed with the author.** The same test passed on Windows, where `Ctrl+A` does select all. Platform confirmed as the cause.

The negative test on the same page (`test_date_picker_does_not_keep_invalid_date`) was passing on macOS for the wrong reason: any input became invalid. The fix below makes it pass for the right reason.

## The fix

- `pages/base_page.py`: new `replace_text(locator, text)` that selects everything with `Cmd+A` on macOS and `Ctrl+A` elsewhere, then types.
- `pages/form_page.py`: `enter_date` now calls `replace_text` instead of sending the key chord itself.

We did not use `clear()`: on this React input it empties the box without updating the page state, so the picker still holds the old date.

## How we checked it, and how we stop it coming back

- Re-ran both date picker tests on macOS: 2 passed in 9 s. Re-ran the full suite: see `docs/TEST_INVENTORY.md`.
- Every "select all and type over" now goes through the one helper in `BasePage`, so the platform rule lives in one place.
- `conftest.py` now saves a screenshot of the page whenever a UI test fails (`reports/screenshots/`), so the next investigation starts with evidence.

## Also seen in the same run: loan request returns 500 on the public ParaBank

`test_api_06_request_loan_returns_decision_and_creates_account_when_approved` fails with HTTP 500 when `API_URL` points at https://parabank.parasoft.com. Calling the endpoint by hand with `curl` gives the same 500 and an HTML error page, for a new account and for the customer's base account, so the public site's loan service is down rather than our test being wrong. Category: **environment**. Our test environment is the local Docker copy, where the result is recorded in the inventory.
