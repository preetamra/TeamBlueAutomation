from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings


class BasePage:
    """Actions every page shares. Each wait stops as soon as the element is ready: no fixed sleeps."""

    path = ""  # each page sets its own address, e.g. "/text-box"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.TIMEOUT)

    def open(self):
        self.driver.get(settings.BASE_URL + self.path)
        return self

    def find(self, locator):
        return self.wait.until(
            EC.visibility_of_element_located(locator),
            f"Not visible after {settings.TIMEOUT}s: {locator}",
        )

    def click(self, locator):
        self.wait.until(
            EC.element_to_be_clickable(locator),
            f"Not clickable after {settings.TIMEOUT}s: {locator}",
        ).click()

    def fill(self, locator, text):
        field = self.find(locator)
        field.clear()
        field.send_keys(text)

    def text_of(self, locator):
        return self.find(locator).text
