"""Setup check: the browser starts and the test site answers. Not one of the 8-10 graded UI tests."""
from pages.home_page import HomePage


def test_home_page_shows_the_sections_we_test(driver):
    names = HomePage(driver).open().category_names()

    # Our UI tests use pages from these four sections of the site.
    assert {"Elements", "Forms", "Alerts, Frame & Windows", "Widgets"} <= set(names)
