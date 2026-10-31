from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC

from config import settings



class TextBoxPage(BasePage):
    """The DemoQA Text Box page and its actions."""

    path = "/text-box"

    FULL_NAME = (By.ID, "userName")
    EMAIL = (By.ID, "userEmail")
    CURRENT_ADDRESS = (By.ID, "currentAddress")
    SUBMIT_BUTTON = (By.ID, "submit")

    OUTPUT_NAME = (By.CSS_SELECTOR, "#output #name")
    OUTPUT_EMAIL = (By.CSS_SELECTOR, "#output #email")
    OUTPUT_ADDRESS = (By.CSS_SELECTOR, "#output #currentAddress")

    def fill_form(self, name, address, email=None):
        self.fill(self.FULL_NAME, name)
        # Email stays optional: UI-01 calls fill_form(name, address) and must not change.
        if email is not None:
            self.fill(self.EMAIL, email)
        self.fill(self.CURRENT_ADDRESS, address)

    def submit_form(self):
        def click_submit_when_ready(driver):
            button = self.find(self.SUBMIT_BUTTON)

            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center',
                    behavior: 'instant'
                });
                """,
                button,
            )

            try:
                button.click()
                return True
            except ElementClickInterceptedException:
                return False

        # conftest.py already saves a screenshot when a test fails.
        self.wait.until(click_submit_when_ready, "The Text Box Submit button remained blocked.")

    def displayed_name(self):
        return self.text_of(self.OUTPUT_NAME)

    def displayed_address(self):
        return self.text_of(self.OUTPUT_ADDRESS)

    def displayed_email(self):
        """Email shown under the form without the 'Email:' prefix; '' when the line is absent."""
        elements = self.driver.find_elements(*self.OUTPUT_EMAIL)
        if not elements:
            return ""
        return elements[0].text.split(":", 1)[-1].strip()

    def address_is_shown(self):
        """True while the page shows an address line under the form (no wait: a state check)."""
        return bool(self.driver.find_elements(*self.OUTPUT_ADDRESS))

    def output_is_shown(self):
        """True once the page shows the submitted values under the form."""
        return bool(self.driver.find_elements(*self.OUTPUT_NAME))

    def email_is_marked_invalid(self):
        """demoqa marks a refused email with the 'field-error' class instead of a message."""
        return "field-error" in self.find(self.EMAIL).get_attribute("class")


class WebTablesPage(BasePage):
    """The DemoQA Web Tables page and its registration form."""

    path = "/webtables"

    ADD_BUTTON = (By.ID, "addNewRecordButton")
    AGE_FIELD = (By.ID, "age")
    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    EMAIL = (By.ID, "userEmail")
    SALARY = (By.ID, "salary")
    DEPARTMENT = (By.ID, "department")
    SUBMIT_BUTTON = (By.ID, "submit")
    REGISTRATION_FORM = (By.ID, "userForm")
    TABLE_BODY = (By.CSS_SELECTOR, ".web-tables-wrapper tbody")

    def open_registration_form(self):
        self.click(self.ADD_BUTTON)

    def enter_age(self, age):
        self.fill(self.AGE_FIELD, age)

    def entered_age(self):
        return self.find(self.AGE_FIELD).get_attribute("value")

    def fill_other_fields(self):
        self.fill(self.FIRST_NAME, "Test")
        self.fill(self.LAST_NAME, "Abdul")
        self.fill(self.EMAIL, "test@example.com")
        self.fill(self.SALARY, "5000")
        self.fill(self.DEPARTMENT, "Testing")

    def submit_form(self):
        self.click(self.SUBMIT_BUTTON)

    def form_is_visible(self):
        """No wait here: an accepted form disappears at once, a refused one stays open."""
        forms = self.driver.find_elements(*self.REGISTRATION_FORM)
        return bool(forms) and forms[0].is_displayed()

    def wait_until_form_closed(self):
        """An accepted record closes the dialog; the wait makes the fade-out explicit."""
        self.wait.until(
            EC.invisibility_of_element_located(self.REGISTRATION_FORM),
            f"The registration form was still open after {settings.TIMEOUT}s",
        )

    def table_text(self):
        """All rows of the web table, to check whether a submitted record was added."""
        return self.text_of(self.TABLE_BODY)

    def age_is_valid(self):
        age_field = self.find(self.AGE_FIELD)
        return age_field.get_property("validity")["valid"]

class SelectMenuPage(BasePage):
    """The DemoQA Select Menu page."""

    path = "/select-menu"

    OLD_STYLE_SELECT = (By.ID, "oldSelectMenu")

    def select_color(self, color):
        dropdown = Select(self.find(self.OLD_STYLE_SELECT))
        dropdown.select_by_visible_text(color)

    def selected_color(self):
        dropdown = Select(self.find(self.OLD_STYLE_SELECT))
        return dropdown.first_selected_option.text

class DatePickerPage(BasePage):
    """The DemoQA Date Picker page."""

    path = "/date-picker"

    DATE_FIELD = (By.ID, "datePickerMonthYearInput")

    def enter_date(self, date):
        # Ctrl+A does not select text on macOS (it needs Cmd+A), so the typed date was appended to
        # the old one and the picker rejected it. replace_text picks the right key per platform.
        self.replace_text(self.DATE_FIELD, date).send_keys(Keys.ENTER)

    def selected_date(self):
        return self.find(self.DATE_FIELD).get_attribute("value")    

class StudentFormPage(BasePage):
    """The DemoQA practice form."""

    path = "/automation-practice-form"

    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    GENDER_MALE = (By.CSS_SELECTOR, "label[for='gender-radio-1']")
    MOBILE = (By.ID, "userNumber")
    # react-select numbers its instances (react-select-3-input), so anchor on the stable containers.
    STATE_INPUT = (By.CSS_SELECTOR, "#state input")
    CITY_INPUT = (By.CSS_SELECTOR, "#city input")
    SUBMIT_BUTTON = (By.ID, "submit")
    RESULT_MODAL = (By.CLASS_NAME, "modal-content")

    def fill_required_fields(self):
        self.fill(self.FIRST_NAME, "Test")
        self.fill(self.LAST_NAME, "Abdul")
        self.click(self.GENDER_MALE)
        self.fill(self.MOBILE, "1234567890")

    def select_state_and_city(self, state, city):
        state_field = self.find(self.STATE_INPUT)
        state_field.send_keys(state)
        state_field.send_keys(Keys.ENTER)

        city_field = self.find(self.CITY_INPUT)
        city_field.send_keys(city)
        city_field.send_keys(Keys.ENTER)

    def submit_form(self):
        def click_submit_when_ready(driver):
            button = self.find(self.SUBMIT_BUTTON)

            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center',
                    behavior: 'instant'
                });
                """,
                button,
            )

            try:
                button.click()
                return True
            except ElementClickInterceptedException:
                return False

        self.wait.until(click_submit_when_ready, "The Submit button remained blocked.")

    def result_text(self):
        return self.text_of(self.RESULT_MODAL)    

    