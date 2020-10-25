import unittest

from src import (
    main,
    Scraper
    )

URL = "https://www.mtgtop8.com/format?f=ST"

class TestMain(unittest.TestCase):

    def setUp(self):
        self.main = main.get_event_links(URL)

    def test_main_makes_list(self):
        result = self.main
        self.assertIsInstance(result, list)


