from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException



class TextBoxPage(BasePage):
    """The DemoQA Text Box page and its actions."""

    path = "/text-box"

    FULL_NAME = (By.ID, "userName")
    CURRENT_ADDRESS = (By.ID, "currentAddress")
    SUBMIT_BUTTON = (By.ID, "submit")

    OUTPUT_NAME = (By.CSS_SELECTOR, "#output #name")
    OUTPUT_ADDRESS = (By.CSS_SELECTOR, "#output #currentAddress")

    def fill_form(self, name, address):
        self.fill(self.FULL_NAME, name)
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

        try:
            self.wait.until(
                click_submit_when_ready,
                "The Text Box Submit button remained blocked.",
            )
        except Exception:
            self.driver.save_screenshot("text_box_error.png")
            raise

    def displayed_name(self):
        return self.text_of(self.OUTPUT_NAME)

    def displayed_address(self):
        return self.text_of(self.OUTPUT_ADDRESS)


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
        return self.find(self.REGISTRATION_FORM).is_displayed()

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
        field = self.find(self.DATE_FIELD)
        field.send_keys(Keys.CONTROL, "a")
        field.send_keys(date)
        field.send_keys(Keys.ENTER)

    def selected_date(self):
        return self.find(self.DATE_FIELD).get_attribute("value")    

class StudentFormPage(BasePage):
    """The DemoQA practice form."""

    path = "/automation-practice-form"

    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    GENDER_MALE = (By.CSS_SELECTOR, "label[for='gender-radio-1']")
    MOBILE = (By.ID, "userNumber")
    STATE_INPUT = (By.ID, "react-select-3-input")
    CITY_INPUT = (By.ID, "react-select-4-input")
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

        try:
            self.wait.until(
                click_submit_when_ready,
                "The Submit button remained blocked.",
            )
        except Exception:
            self.driver.save_screenshot("student_form_error.png")
            raise

    def result_text(self):
        return self.text_of(self.RESULT_MODAL)    

    