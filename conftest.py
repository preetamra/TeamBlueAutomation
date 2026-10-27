import pytest
from selenium import webdriver

from config import settings


@pytest.fixture
def driver():
    """A fresh Chrome for every test, closed afterwards, so tests never share a session."""
    options = webdriver.ChromeOptions()
    if settings.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    # Don't wait for ads and images to finish; our explicit waits decide when an element is ready.
    options.page_load_strategy = "eager"
    browser = webdriver.Chrome(options=options)  # Selenium Manager downloads the matching driver
    yield browser
    browser.quit()
