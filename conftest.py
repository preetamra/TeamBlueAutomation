from pathlib import Path
import shutil
import tempfile

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

    # Profil isole et options de stabilite pour eviter les collisions et plantages Chrome
    profile_dir = tempfile.mkdtemp(prefix="chrome_profile_")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    browser = webdriver.Chrome(options=options)  # Selenium Manager downloads the matching driver
    yield browser
    browser.quit()
    shutil.rmtree(profile_dir, ignore_errors=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """When a UI test fails, save a screenshot of the page as evidence (reports/screenshots/)."""
    outcome = yield
    report = outcome.get_result()
    browser = item.funcargs.get("driver")
    if report.when == "call" and report.failed and browser is not None:
        folder = Path("reports/screenshots")
        folder.mkdir(parents=True, exist_ok=True)
        browser.save_screenshot(str(folder / f"{item.name}.png"))
