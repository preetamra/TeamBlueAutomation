"""UI-08 and UI-09: dialogs and an element that changes after a delay."""
import pytest

from pages.dialog_page import AlertsPage, ModalDialogsPage
from pages.dynamic_page import DynamicPropertiesPage


@pytest.mark.parametrize(
    "accept, expected_result",
    [(True, "You selected Ok"), (False, "You selected Cancel")],
    ids=["ok", "cancel"],
)
def test_confirm_dialog_shows_the_answer_on_the_page(driver, accept, expected_result):
    """UI-08 (dialog, browser alert): the question is right and the page shows the user's answer."""
    page = AlertsPage(driver).open()

    question = page.answer_confirm(accept)

    assert question == "Do you confirm action?"
    assert page.confirm_result() == expected_result


def test_html_popup_shows_its_text_and_closes(driver):
    """UI-08 (dialog, HTML pop-up): the pop-up shows its title and text, then really closes."""
    page = ModalDialogsPage(driver).open().open_small_modal()

    assert page.modal_title() == "Small Modal"
    assert "This is a small modal" in page.modal_body()

    page.close_modal()
    assert page.modal_is_closed()


def test_delayed_buttons_become_enabled_and_visible(driver):
    """UI-09 (dynamic element): the test waits for both changes, without a fixed sleep."""
    page = DynamicPropertiesPage(driver).open()

    # Right after loading: one button is disabled and the other is not on screen yet.
    assert not page.delayed_button_is_enabled()
    assert not page.hidden_button_is_shown()

    page.wait_until_delayed_button_is_enabled()
    assert page.delayed_button_is_enabled()
    assert page.wait_for_hidden_button().text == "Visible After 5 Seconds"
