from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from config import settings
from pages.base_page import BasePage


class DynamicPropertiesPage(BasePage):
    """demoqa "Dynamic Properties": 5 seconds after loading, one button turns on and another appears."""

    path = "/dynamic-properties"

    ENABLE_AFTER = (By.ID, "enableAfter")
    VISIBLE_AFTER = (By.ID, "visibleAfter")

    def delayed_button_is_enabled(self):
        return self.find(self.ENABLE_AFTER).is_enabled()

    def wait_until_delayed_button_is_enabled(self):
        # Stops as soon as the button can be clicked, instead of always sleeping 5 seconds.
        self.wait.until(
            EC.element_to_be_clickable(self.ENABLE_AFTER),
            f"Button still disabled after {settings.TIMEOUT}s: {self.ENABLE_AFTER}",
        )
        return self

    def hidden_button_is_shown(self):
        return any(button.is_displayed() for button in self.driver.find_elements(*self.VISIBLE_AFTER))

    def wait_for_hidden_button(self):
        return self.find(self.VISIBLE_AFTER)
