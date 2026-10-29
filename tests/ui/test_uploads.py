"""UI-05 to UI-07: file upload, image upload, and the error-handling test."""
from pathlib import Path

from pages.upload_page import PracticeFormPage, UploadPage

FILES = Path(__file__).resolve().parents[2] / "data" / "files"


def test_upload_shows_the_name_of_the_uploaded_pdf(driver):
    """UI-05 (positive, file validation): the uploaded PDF's name appears under the field."""
    page = UploadPage(driver).open().upload(FILES / "sample.pdf")

    # Browsers hide the real folder and show C:\fakepath\<name>, so we check the file name.
    assert page.uploaded_file_text().endswith("sample.pdf")


def test_form_accepts_a_png_picture_and_shows_its_name(driver):
    """UI-06 (positive): a PNG picture is accepted and listed in the confirmation."""
    form = PracticeFormPage(driver).open()
    form.fill_required_fields("Imene", "Blue", "0612345678")
    form.attach_picture(FILES / "photo.png")
    form.submit()

    assert form.confirmation_title() == "Thanks for submitting the form"
    assert form.picture_in_confirmation() == "photo.png"


def test_form_with_empty_required_fields_is_rejected(driver):
    """UI-07 (negative, error handling): an empty form is refused and nothing is submitted.

    demoqa accepts every file type, so the error test uses the form's required fields instead.
    """
    form = PracticeFormPage(driver).open()
    form.submit()
    form.wait_until_validation_has_run()

    assert form.invalid_required_fields() == ["First Name", "Last Name", "Gender", "Mobile"]
    assert not form.confirmation_is_shown(), "The form was submitted although it is empty"