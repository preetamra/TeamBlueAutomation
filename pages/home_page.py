from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class HomePage(BasePage):
    path = "/"

    CATEGORY_NAMES = (By.CSS_SELECTOR, ".top-card h5")

    def category_names(self):
        cards = self.wait.until(EC.visibility_of_all_elements_located(self.CATEGORY_NAMES))
        return [card.text for card in cards]
