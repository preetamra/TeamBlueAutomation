from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from config import settings
from pages.base_page import BasePage


class AlertsPage(BasePage):
    """demoqa "Alerts": buttons that open real browser dialogs (alert, confirm, prompt)."""

    path = "/alerts"

    CONFIRM_BUTTON = (By.ID, "confirmButton")
    CONFIRM_RESULT = (By.ID, "confirmResult")

    def answer_confirm(self, accept):
        """Open the browser confirm box, answer it, and return the question it showed."""
        self.click(self.CONFIRM_BUTTON)
        # A browser dialog is not part of the page: no locator, we switch to it.
        alert = self.wait.until(EC.alert_is_present(), "No browser dialog appeared")
        question = alert.text
        if accept:
            alert.accept()
        else:
            alert.dismiss()
        return question

    def confirm_result(self):
        return self.text_of(self.CONFIRM_RESULT)


class ModalDialogsPage(BasePage):
    """demoqa "Modal Dialogs": a pop-up built in HTML inside the page, handled with normal locators."""

    path = "/modal-dialogs"

    OPEN_SMALL_MODAL = (By.ID, "showSmallModal")
    MODAL_TITLE = (By.ID, "example-modal-sizes-title-sm")
    MODAL_BODY = (By.CSS_SELECTOR, ".modal-body")
    CLOSE_BUTTON = (By.ID, "closeSmallModal")

    def open_small_modal(self):
        self.click(self.OPEN_SMALL_MODAL)
        return self

    def modal_title(self):
        return self.text_of(self.MODAL_TITLE)

    def modal_body(self):
        return self.text_of(self.MODAL_BODY)

    def close_modal(self):
        self.click(self.CLOSE_BUTTON)
        return self

    def modal_is_closed(self):
        return self.wait.until(
            EC.invisibility_of_element_located(self.MODAL_TITLE),
            f"The pop-up is still open after {settings.TIMEOUT}s",
        )
