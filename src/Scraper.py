from selenium import webdriver
from selenium.common.exceptions import (
    InvalidArgumentException,
    NoSuchElementException
)

from src.Selection import create_selector

class Scraper:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Safari()
        self.driver.get(self.url)

    def get_title(self):
        return self.driver.title

    def quit(self):
        self.driver.quit()

    def get_page_source(self):
        return self.driver.page_source

    def get_by(self, element_type, selector, get_all=False):
        selector = create_selector(self.driver, element_type, selector)
        if get_all:
            return selector.get_all()
        return selector.get_first()

    def execute(self, script, argument):
        self.driver.execute_script(f"{script}({argument});")
