import pytest
from pages.form_page import (
    TextBoxPage,
    WebTablesPage,
    SelectMenuPage,
    DatePickerPage,
    StudentFormPage,
)


def test_text_box_displays_submitted_name_and_address(driver):
    # Arrange: open the page and prepare test data.
    page = TextBoxPage(driver).open()
    name = "Abdul Manan"
    address = "10 Test Street, Lille"

    # Act: fill in and submit the form.
    page.fill_form(name, address)
    page.submit_form()

    # Assert: check what the page displays after submission.
    assert name in page.displayed_name()
    assert address in page.displayed_address()

def test_age_field_accepts_digits(driver):
    page = WebTablesPage(driver).open()
    page.open_registration_form()

    page.enter_age("25")

    assert page.entered_age() == "25"


def test_age_field_rejects_letters_on_submit(driver):
    page = WebTablesPage(driver).open()
    page.open_registration_form()

    page.fill_other_fields()
    page.enter_age("ab")
    page.submit_form()

    assert page.form_is_visible()
    assert not page.age_is_valid()  

@pytest.mark.parametrize("age", ["1", "99"])
def test_age_accepts_one_or_two_digits(driver, age):
    page = WebTablesPage(driver).open()
    page.open_registration_form()

    page.enter_age(age)

    assert page.entered_age() == age
    assert page.age_is_valid()


def test_age_input_limits_entry_to_two_characters(driver):
    page = WebTablesPage(driver).open()
    page.open_registration_form()

    page.enter_age("123")

    assert page.entered_age() == "12"

def test_dropdown_displays_selected_color(driver):
    page = SelectMenuPage(driver).open()

    page.select_color("Blue")

    assert page.selected_color() == "Blue"

def test_date_picker_displays_valid_date(driver):
    page = DatePickerPage(driver).open()

    page.enter_date("06/15/2020")

    assert page.selected_date() == "06/15/2020"    

def test_date_picker_does_not_keep_invalid_date(driver):
    page = DatePickerPage(driver).open()

    initial_date = page.selected_date()
    page.enter_date("02/30/2024")
    result = page.selected_date()

    assert result in ("", initial_date)
    assert result != "02/30/2024"

def test_dropdown_values_appear_after_form_submission(driver):
    page = StudentFormPage(driver).open()

    page.fill_required_fields()
    page.select_state_and_city("NCR", "Delhi")
    page.submit_form()

    result = page.result_text()
    assert "NCR" in result
    assert "Delhi" in result


