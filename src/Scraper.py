from selenium import webdriver

from src.Selection import create_selector


class Scraper:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Firefox()
        self.driver.get(self.url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.driver.quit()

    def __repr__(self):
        return self.driver.page_source

    def get_title(self):
        return self.driver.title

    def get_url(self):
        return self.driver.current_url

    def get_by(self, element_type, selector):
        result = create_selector(self.driver, element_type, selector)
        return result.get_first()

    def get_all_by(self, element_type, selector):
        result = create_selector(self.driver, element_type, selector)
        return result.get_all()

    def execute(self, script, argument):
        self.driver.execute_script(f"{script}({argument});")
