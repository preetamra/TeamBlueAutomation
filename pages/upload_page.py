from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from config import settings
from pages.base_page import BasePage


class UploadPage(BasePage):
    """demoqa "Upload and Download": one file field; the chosen file name is shown under it."""

    path = "/upload-download"

    FILE_INPUT = (By.ID, "uploadFile")
    UPLOADED_PATH = (By.ID, "uploadedFilePath")

    def upload(self, file_path):
        # The path goes straight into the <input type="file">: the computer's file window never opens.
        self.wait.until(
            EC.presence_of_element_located(self.FILE_INPUT),
            f"File field not found: {self.FILE_INPUT}",
        ).send_keys(str(file_path))
        return self

    def uploaded_file_text(self):
        return self.text_of(self.UPLOADED_PATH)


class PracticeFormPage(BasePage):
    """demoqa "Practice Form": only the parts the upload and error tests need."""

    path = "/automation-practice-form"

    FORM = (By.ID, "userForm")
    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    # The real radio input is covered by its label, so a user (and the test) clicks the label.
    GENDER_FEMALE_LABEL = (By.CSS_SELECTOR, "label[for='gender-radio-2']")
    GENDER_INPUT = (By.ID, "gender-radio-1")
    MOBILE = (By.ID, "userNumber")
    PICTURE_INPUT = (By.ID, "uploadPicture")
    SUBMIT = (By.ID, "submit")
    CONFIRMATION_TITLE = (By.ID, "example-modal-sizes-title-lg")
    # Relative XPath, used only here: the result table has no id, so we find the cell next to "Picture".
    PICTURE_RESULT = (By.XPATH, "//td[text()='Picture']/following-sibling::td")

    # Name shown in the test report -> locator of the required field
    REQUIRED_FIELDS = {
        "First Name": FIRST_NAME,
        "Last Name": LAST_NAME,
        "Gender": GENDER_INPUT,
        "Mobile": MOBILE,
    }

    def fill_required_fields(self, first_name, last_name, mobile):
        self.fill(self.FIRST_NAME, first_name)
        self.fill(self.LAST_NAME, last_name)
        self.click(self.GENDER_FEMALE_LABEL)
        self.fill(self.MOBILE, mobile)
        return self

    def attach_picture(self, file_path):
        self.wait.until(
            EC.presence_of_element_located(self.PICTURE_INPUT),
            f"Picture field not found: {self.PICTURE_INPUT}",
        ).send_keys(str(file_path))
        return self

    def submit(self):
        # Ads and the site footer can cover the Submit button. They are not part of the
        # form under test, so we remove them from the page before clicking.
        self.driver.execute_script(
            "document.querySelectorAll('footer, #fixedban, #adplus-anchor').forEach(e => e.remove());"
        )
        button = self.wait.until(
            EC.presence_of_element_located(self.SUBMIT),
            f"Submit button not found: {self.SUBMIT}",
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        self.driver.execute_script("arguments[0].click();", button)
        return self

    def confirmation_title(self):
        return self.text_of(self.CONFIRMATION_TITLE)

    def picture_in_confirmation(self):
        return self.text_of(self.PICTURE_RESULT)

    def wait_until_validation_has_run(self):
        # After a submit, the form gets the class "was-validated" and marks its invalid fields.
        self.wait.until(
            lambda d: "was-validated" in d.find_element(*self.FORM).get_attribute("class"),
            f"The form did not run its validation after {settings.TIMEOUT}s",
        )
        return self

    def invalid_required_fields(self):
        """Names of the required fields the browser considers invalid."""
        return [
            name
            for name, locator in self.REQUIRED_FIELDS.items()
            if not self.driver.execute_script(
                "return arguments[0].checkValidity();", self.driver.find_element(*locator)
            )
        ]

    def confirmation_is_shown(self):
        return any(title.is_displayed() for title in self.driver.find_elements(*self.CONFIRMATION_TITLE))