import selenium
import unittest

from src import (
    main,
    Scraper
    )

URL = "https://www.mtgtop8.com/format?f=ST"

class TestMain(unittest.TestCase):

    def setUp(self):
        self.main = main.get_event_links(URL)

    def test_main_makes_scraper(self):
        result = self.main
        self.assertIsInstance(result, Scraper.Scraper)

    def test_main_gets_correct_url(self):
        result = self.main
        self.assertEqual(result.get_url(), URL)

    def tearDown(self):
        self.main.quit()

