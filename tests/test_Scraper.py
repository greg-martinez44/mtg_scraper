import unittest

from selenium import webdriver
from selenium.common.exceptions import (
    InvalidArgumentException,
    NoSuchElementException
)
"""
Hold for future? If not used, DELETE
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
"""

from src.Scraper import Scraper

URL = "https://www.mtgtop8.com/format?f=ST"


class TestDriver(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper(URL)

    def test_get_mtgtop8(self):
        page_title = self.scraper.get_title().lower()
        self.assertIn("mtg", page_title)
        self.assertEqual(self.scraper.driver.current_url, URL)

    def test_stable_should_be_in_page_one_body(self):
        page_source = self.scraper.get_page_source()
        self.assertIn("Stable", page_source)
        self.assertNotIn("Stttbl", page_source)

    def test_should_return_a_string_for_page_source(self):
        this_scraper = self.scraper
        page_source = this_scraper.get_page_source()
        self.assertIsInstance(page_source, str)

    def test_is_page_one_with_no_previous_button(self):
        page = 2
        page_source = self.scraper.get_page_source()
        stable = self.scraper.get_by("css", "table.Stable")
        self.assertIn("Nav_PN_no", page_source)
        self.assertIn(f"PageSubmit({page})", page_source)
        self.assertIsNotNone(stable)

    def test_get_button_to_go_to_page_two(self):
        self.scraper.execute("PageSubmit", 2)
        stable = self.scraper.get_by("css", "table.Stable")
        self.assertNotIn("Nav_PN_no", stable)

    def test_first_page_should_have_this_event_title(self):
        event_title = "Artisan ! @ Lotus eSports"

    def tearDown(self):
        self.scraper.quit()

# Skipping because it is gumming up the webdriver access...
@unittest.SkipTest
class TestDriverWithBadInputsDefaultExceptions(unittest.TestCase):

    def test_should_return_with_empty_page(self):
        with self.assertRaises(InvalidArgumentException):
            scraper = Scraper("adfa")
            scraper.quit()

    def test_should_get_mad_if_no_keys_in_selector(self):
        scraper = Scraper(URL)
        result = scraper.get_by("css", "table.NotATable")
        self.assertFalse(result)
        scraper.quit()


class TestGettingSpecificElements(unittest.TestCase):

    def setUp(self):
        self.scraper = Scraper(URL)

    def test_should_give_all_tables_with_class_Stable(self):
        table_elements = self.scraper.get_by(
            "css", "table.Stable", get_all=True)
        self.assertTrue(len(table_elements) > 1)
        self.assertIsInstance(table_elements, list)

    def test_should_give_first_table_with_class_stable(self):
        table_element = self.scraper.get_by("css", "table.Stable")
        self.assertEqual(len(table_element), 1)

    def test_finding_one_thing_by_name(self):
        result = self.scraper.get_by("name", "meta")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)

    def test_finding_one_thing_by_id(self):
        result = self.scraper.get_by("id", "other_tooltip")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)

    def tearDown(self):
        self.scraper.quit()


if __name__ == "__main__":
    unittest.main()
