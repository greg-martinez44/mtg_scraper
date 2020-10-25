import unittest
import requests
import re

from bs4 import BeautifulSoup

from src.Event import Event

@unittest.SkipTest
class TestResultsFromBeautifulSoup(unittest.TestCase):
    URL = "https://www.mtgtop8.com/format?f=ST"
    def setUp(self):
        self.page_source = requests.get(self.URL)
        self.this_source = self.page_source.content
        self.html = BeautifulSoup(self.this_source, features="lxml")

    def test_should_return_prettified_json(self):
        self.assertIn("Standard", self.html.title.contents[0])

    def test_soup_should_have_first_event_in_event_list(self):
        event = "Artisan ! @ Lotus eSports"
        self.assertIn(event, [string for string in self.html.stripped_strings])

    def test_soup_should_have_stable_element(self):
        event = "Artisan ! @ Lotus eSports"
        this_html = self.html
        stable = this_html.find_all("table", class_="Stable")
        self.assertIsNotNone(stable)
        self.assertIsInstance(stable, list)

