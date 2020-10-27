import unittest
import time

from selenium.common.exceptions import (
    InvalidArgumentException,
)

from src.Scraper import Scraper, _Scraper

URL = "https://www.mtgtop8.com/format?f=ST"

class TestDriver(unittest.TestCase):

    def test_get_mtgtop8(self):
        with Scraper(URL) as scraper:
            page_title = scraper.get_title().lower()
            self.assertIn("mtg", page_title)
            self.assertEqual(scraper.get_url(), URL)

    def test_stable_should_be_in_page_one_body(self):
        with Scraper(URL) as scraper:
            page_source = scraper.get_page_source()
            self.assertIn("Stable", page_source)
            self.assertNotIn("Stttbl", page_source)

    def test_should_return_a_string_for_page_source(self):
        with Scraper(URL) as scraper:
            page_source = scraper.get_page_source()
            self.assertIsInstance(page_source, str)

    def test_is_page_one_with_no_previous_button(self):
        page = 2
        with Scraper(URL) as scraper:
            page_source = scraper.get_page_source()
            stable = scraper.get_by("css", "table.Stable")
        self.assertIn("Nav_PN_no", page_source)
        self.assertIn(f"PageSubmit({page})", page_source)
        self.assertIsNotNone(stable)

    def test_get_button_to_go_to_page_two(self):
        with Scraper(URL) as scraper:
            scraper.execute("PageSubmit", 2)
            stable = scraper.get_by("css", "table.Stable")
        self.assertNotIn("Nav_PN_no", stable)

    def test_first_page_should_have_this_event_title(self):
        event_title = "FNM @ Deckmaster Games"
        with Scraper(URL) as scraper:
            page_source = scraper.get_page_source()
        self.assertIn(event_title, page_source)


# Skipping because it is gumming up the webdriver access...
@unittest.SkipTest
class TestDriverWithBadInputsDefaultExceptions(unittest.TestCase):

    def test_should_return_with_empty_page(self):
        with self.assertRaises(InvalidArgumentException):
            scraper = Scraper("adfa")
            scraper.quit()

    def test_should_get_mad_if_no_keys_in_selector(self):
        with Scraper(URL) as scraper:
            result = scraper.get_by("css", "table.NotATable")
        self.assertFalse(result)


class TestGettingSpecificElements(unittest.TestCase):


    def test_should_give_all_tables_with_class_Stable(self):
        with Scraper(URL) as scraper:
            table_elements = scraper.get_all_by(
                "css", "table.Stable")
        self.assertTrue(len(table_elements) > 1)
        self.assertIsInstance(table_elements, list)

    def test_should_give_first_table_with_class_stable(self):
        with Scraper(URL) as scraper:
            table_element = scraper.get_by("css", "table.Stable")
        self.assertEqual(len(table_element), 1)

    def test_finding_one_thing_by_name(self):
        with Scraper(URL) as scraper:
            result = scraper.get_by("name", "meta")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)

    def test_finding_one_thing_by_id(self):
        with Scraper(URL) as scraper:
            result = scraper.get_by("id", "other_tooltip")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)

    def test_finding_one_thing_by_class_not_css(self):
        with Scraper(URL) as scraper:
            result = scraper.get_by("class", "S14")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result, list)
            self.assertIn("Players Tour Online", result[0].text)

    def test_finding_all_things_by_class_not_css(self):
        with Scraper(URL) as scraper:
            result = scraper.get_all_by("class", "S14")
            self.assertGreaterEqual(len(result), 2)
            self.assertEqual("1243 decks", result[1].text)

    def test_find_one_row_of_stable_with_xpath(self):
        with Scraper(URL) as scraper:
            result = scraper.get_by("xpath", "//table[@class='Stable'][2]//tr[@class='hover_tr']//a")
            self.assertEqual(len(result), 1)
            self.assertEqual("Japan Championship 2020 Autumn - Last Chance Trial @ BIG Magic", result[0].text)
            self.assertIn("event?e=27876&f=ST", result[0].get_attribute("href"))

    def test_find_all_rows_in_stable_with_xpath(self):
        with Scraper(URL) as scraper:
            results = scraper.get_all_by(
                "xpath", "//table[@class='Stable'][2]//tr[@class='hover_tr']//a"
                )
            self.assertEqual(len(results), 10)
            events = [item.text for item in results]
            links = [item.get_attribute("href") for item in results]
            self.assertIn("FNM @ Deckmaster Games", events)
            self.assertIn("https://www.mtgtop8.com/event?e=27847&f=ST", links)

    def test_xpath_finds_things_on_other_pages(self):
        with Scraper(URL) as scraper:
            scraper.execute("PageSubmit", 9)
            time.sleep(2)
            results = scraper.get_all_by(
                "xpath", "//table[@class='Stable'][2]//tr[@class='hover_tr']//a"
            )
            self.assertEqual(len(results), 10)
            events = [item.text for item in results]
            links = [item.get_attribute("href") for item in results]
            self.assertIn("Monday Night Magic 2 @ Plague League", events)
            self.assertIn("https://www.mtgtop8.com/event?e=27623&f=ST", links)

class TestWithContextManager(unittest.TestCase):

    def test_should_return_scraper_object(self):
        with Scraper(URL) as scraper:
            self.assertIsInstance(scraper, _Scraper)

if __name__ == "__main__":
    unittest.main()
