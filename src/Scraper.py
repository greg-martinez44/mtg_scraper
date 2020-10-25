from selenium import webdriver

from src.Selection import create_selector

#TODO: App should cycle through stable -> hover_tr for event names.Keep
#clicking Next until you have a class Nav_pn_no in page_source


class Scraper:
    def __init__(self, url):
        self.url = url
        self.scraper = _Scraper(self.url)
    def __enter__(self):
        return self.scraper

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.scraper.quit()

class _Scraper:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Safari()
        self.driver.get(self.url)

    def get_title(self):
        return self.driver.title

    def get_url(self):
        return self.driver.current_url

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
