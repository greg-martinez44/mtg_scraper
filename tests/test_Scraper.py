import unittest
import time

from selenium.common.exceptions import (
    InvalidArgumentException,
)

from src.Scraper import Scraper

"""
Hold for future? If not used, DELETE
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
"""


URL = "https://www.mtgtop8.com/format?f=ST"


class TestDriver(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper(URL)

    def test_get_mtgtop8(self):
        page_title = self.scraper.get_title().lower()
        self.assertIn("mtg", page_title)
        self.assertEqual(self.scraper.get_url(), URL)

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
        page_source = self.scraper.get_page_source()
        self.assertIn(event_title, page_source)

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

    def test_finding_one_thing_by_class_not_css(self):
        result = self.scraper.get_by("class", "S14")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)
        self.assertIn("Players Tour Online", result[0].text)

    def test_finding_all_things_by_class_not_css(self):
        result = self.scraper.get_by("class", "S14", get_all=True)
        self.assertGreaterEqual(len(result), 2)
        self.assertEqual("1158 decks", result[1].text)

    def test_find_one_row_of_stable_with_xpath(self):
        result = self.scraper.get_by(
            "xpath", "//table[@class='Stable'][2]//tr[@class='hover_tr']//a"
            )
        self.assertEqual(len(result), 1)
        self.assertEqual(
            "Week of Wings Entry Event Friday Flight 1 @ Red Bull Untapped", result[0].text
            )
        self.assertIn("event?e=27834&f=ST", result[0].get_attribute("href"))

    def test_find_all_rows_in_stable_with_xpath(self):
        results = self.scraper.get_by(
            "xpath", "//table[@class='Stable'][2]//tr[@class='hover_tr']//a",
            get_all=True
            )
        self.assertEqual(len(results), 10)
        events = [item.text for item in results]
        links = [item.get_attribute("href") for item in results]
        self.assertIn("Torneios @ Loja Ludo Quest", events)
        self.assertIn("https://www.mtgtop8.com/event?e=27845&f=ST", links)

    def test_xpath_finds_things_on_other_pages(self):
        self.scraper.execute("PageSubmit", 8)
        time.sleep(2)
        results = self.scraper.get_by(
            "xpath", "//table[@class='Stable'][2]//tr[@class='hover_tr']//a",
            get_all=True
            )
        self.assertEqual(len(results), 10)
        events = [item.text for item in results]
        links = [item.get_attribute("href") for item in results]
        self.assertIn("Monday Night Magic 2 @ Plague League", events)
        self.assertIn("https://www.mtgtop8.com/event?e=27623&f=ST", links)

    def tearDown(self):
        self.scraper.quit()


if __name__ == "__main__":
    unittest.main()
