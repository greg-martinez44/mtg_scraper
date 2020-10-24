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

    def click(self, page_number):
        self.driver.execute_script(f"PageSubmit({page_number});")
        time.sleep(1)

    def get_page_source(self):
        return self.driver.page_source

    def get_by_selector(self, selector):
        return self.driver.find_element_by_css_selector(selector)

    def get_by_selectors(self, selectors):
        return self.driver.find_elements_by_css_selectors(selectors)

    def execute(self, script, argument):
        self.driver.execute_script(f"{script}({argument});")

    def close(self):
        self.driver.close()
