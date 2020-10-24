import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

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

    def get_by_selector(self, selector):
        return self.driver.find_element_by_css_selector(selector)

    def execute(self, script, argument):
        self.driver.execute_script(f"{script}({argument});")

    def close(self):
        self.driver.close()

class ElementSelector(Scraper):

    def __init__(self, selector):
        super().__init__()
        self.selector = selector

    def get_first_by_css(self):
        return self.driver.find_element_by_css_selector(selector)

    def get_all_by_css(self):
        return self.driver.find_elements_by_css_selector(selector)
