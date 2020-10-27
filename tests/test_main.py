import selenium
import unittest

from src import (
    main,
    Scraper
    )

URL = "https://www.mtgtop8.com/format?f=ST"

class TestMain(unittest.TestCase):

    def test_main_makes_scraper(self):
        result = main.get_events(URL)
        self.assertIsInstance(result, list)


