"""UI-10: one test function, one run per line of `data/form_data.csv`.

The CSV holds the test data and the expected result of each line, so a new case
is added by writing a line, not by copying the test.
"""
import csv
from pathlib import Path

import pytest

from pages.form_page import TextBoxPage

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "form_data.csv"


def load_cases():
    with DATA_FILE.open(newline="", encoding="utf-8") as stream:
        cases = list(csv.DictReader(stream))
    if not cases:
        raise RuntimeError(f"No data set found in {DATA_FILE}")
    return cases


CASES = load_cases()


@pytest.mark.regression
@pytest.mark.parametrize("case", CASES, ids=[case["case"] for case in CASES])
def test_ui10_text_box_accepts_each_data_set(driver, case):
    """UI-10 (data-driven, boundary): each data set fills the form and is checked on its own."""
    page = TextBoxPage(driver).open()

    # Act: the same steps for every line of the CSV.
    page.fill_form(case["name"], case["address"], case["email"])
    page.submit_form()

    if case["expected"] == "rejected":
        # demoqa refuses the email, marks the field and shows nothing under the form.
        assert page.email_is_marked_invalid(), "the refused email should be marked invalid"
        assert not page.output_is_shown(), "a refused form must not show any output"
        return

    # Assert: what we typed must come back unchanged under the form. The address is checked line
    # by line because Selenium's .text joins the lines of a text area with a space.
    assert case["name"] in page.displayed_name()
    for line in case["address"].splitlines():
        assert line in page.displayed_address()

    if case["expected"] == "shown":
        assert page.displayed_email() == case["email"]
    elif case["expected"] == "no_email":
        assert page.displayed_email() == ""
    else:
        pytest.fail(f"unknown 'expected' value in the CSV: {case['expected']}")
