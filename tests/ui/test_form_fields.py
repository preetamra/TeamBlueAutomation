import pytest
from pages.form_page import (
    TextBoxPage,
    WebTablesPage,
    SelectMenuPage,
    DatePickerPage,
    StudentFormPage,
)


def test_text_box_displays_submitted_name_and_address(driver):
    """UI-01 (positive, text input and text area, state check): the submitted values are shown."""
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


def test_text_box_edit_and_clear_update_the_output(driver):
    """UI-01b (positive, text input edit and clear, state check): a second submit replaces the name
    and clearing the address removes its line under the form."""
    page = TextBoxPage(driver).open()
    page.fill_form("First Name", "10 Test Street, Lille")
    page.submit_form()
    assert "First Name" in page.displayed_name()
    assert page.address_is_shown()

    # Act: edit the name, clear the address, submit again.
    page.fill_form("Edited Name", "")
    page.submit_form()

    # Assert: the output follows the new state of the form.
    assert "Edited Name" in page.displayed_name()
    assert "First Name" not in page.displayed_name()
    assert not page.address_is_shown()


def test_age_field_accepts_digits(driver):
    """UI-02a (positive, number input, state check): a valid age is accepted and the record is added."""
    page = WebTablesPage(driver).open()
    page.open_registration_form()

    page.fill_other_fields()
    page.enter_age("25")
    page.submit_form()

    page.wait_until_form_closed()
    assert "test@example.com" in page.table_text()
    assert "25" in page.table_text()


def test_age_field_rejects_letters_on_submit(driver):
    """UI-02b (negative, field validation): letters in Age keep the form open and add no record."""
    page = WebTablesPage(driver).open()
    page.open_registration_form()

    page.fill_other_fields()
    page.enter_age("ab")
    page.submit_form()

    assert page.form_is_visible()
    assert not page.age_is_valid()
    assert "test@example.com" not in page.table_text()

@pytest.mark.parametrize("age", ["1", "99"])
def test_age_accepts_one_or_two_digits(driver, age):
    """UI-02c/d (boundary): the smallest and the largest two-digit age are valid."""
    page = WebTablesPage(driver).open()
    page.open_registration_form()

    page.enter_age(age)

    assert page.entered_age() == age
    assert page.age_is_valid()


def test_age_input_limits_entry_to_two_characters(driver):
    """UI-02e (boundary): a third digit is cut off, the field keeps two characters."""
    page = WebTablesPage(driver).open()
    page.open_registration_form()

    page.enter_age("123")

    assert page.entered_age() == "12"

def test_dropdown_displays_selected_color(driver):
    """UI-03a (positive, dropdown): the chosen option is the selected one."""
    page = SelectMenuPage(driver).open()

    page.select_color("Blue")

    assert page.selected_color() == "Blue"

def test_date_picker_displays_valid_date(driver):
    """UI-04a (positive, date picker): a valid date typed in is kept."""
    page = DatePickerPage(driver).open()

    page.enter_date("06/15/2020")

    assert page.selected_date() == "06/15/2020"    

def test_date_picker_does_not_keep_invalid_date(driver):
    """UI-04b (negative, date validation): a date that does not exist is refused, the valid one stays."""
    page = DatePickerPage(driver).open()
    page.enter_date("06/15/2020")
    assert page.selected_date() == "06/15/2020"

    page.enter_date("02/30/2024")

    assert page.selected_date() == "06/15/2020"

def test_dropdown_values_appear_after_form_submission(driver):
    """UI-03b (dynamic dropdowns, dialog, state check): state and city appear in the result dialog."""
    page = StudentFormPage(driver).open()

    page.fill_required_fields()
    page.select_state_and_city("NCR", "Delhi")
    page.submit_form()

    result = page.result_text()
    assert "NCR" in result
    assert "Delhi" in result


