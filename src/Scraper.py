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

    def get_by(self, selector):
        return CSS_Selector(self.driver, selector).get_first()

    def execute(self, script, argument):
        self.driver.execute_script(f"{script}({argument});")

    def close(self):
        self.driver.close()


class Selector:

    def __init__(self, driver):
        self.driver = driver

    def get_first(self):
        pass
    
    def get_all(self):
        pass

class CSS_Selector(Selector):

    def __init__(self, driver, selector):
        super().__init__(driver)
        self.selector = selector

    def get_first(self):
        return self.driver.find_element_by_css_selector(self.selector)

    def get_all(self):
        return self.driver.find_elements_by_css_selector(self.selector)
