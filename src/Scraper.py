"""
Selenium wrapper for traversing mtgtop8.com
"""
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Scraper:
    """Selenium wrapper for easy web navigation"""

    def __init__(self, url):
        """Establishes driver"""
        self.url = url
        self.driver = webdriver.Firefox()
        self.driver.get(self.url)

    def __enter__(self):
        """Enters the object as context manager"""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Quits the driver as context manager"""
        return self.driver.quit()

    def __repr__(self):
        """String representation of page source"""
        return self.driver.page_source

    def get_title(self):
        """Returns the title of a webpage"""
        return self.driver.title

    def get_url(self):
        """Returns the url of a webpage"""
        return self.driver.current_url

    def get_by(self, element_type, selector):
        """
        Calls a function factory to get an element by:
        xpath
        id
        css class
        """
        result = create_selector(self.driver, element_type, selector)
        return result.get_first()

    def get_all_by(self, element_type, selector):
        """Returns a list of all the elements of the given type."""
        result = create_selector(self.driver, element_type, selector)
        return result.get_all()

    def execute(self, script, argument):
        """Executes some javascript function on a webpage"""
        self.driver.execute_script(f"{script}({argument});")


def create_selector(driver, element_type, selector):
    """Factory function for finding elements in a website's body"""
    if element_type == "css":
        return SelectorCSS(driver, selector)
    if element_type == "name":
        return SelectorName(driver, selector)
    if element_type == "id":
        return SelectorID(driver, selector)
    if element_type == "class":
        return SelectorClass(driver, selector)
    if element_type == "xpath":
        return SelectorXpath(driver, selector)
    return None


def _check_result(func):
    """
    Wrapper for making single selections a list,
    or returning an empty list instead of an error if no elements are found.
    """
    def check_result(self):
        try:
            return [func(self)]
        except NoSuchElementException:
            return []
    return check_result


class Selector:
    """Abstract class for the selector objects"""

    def get_first(self):
        """Returns first item"""
        return

    def get_all(self):
        """Returns all items"""
        return


class SelectorCSS(Selector):
    """Select for CSS items"""
    def __init__(self, driver, selector):
        self.driver = driver
        self.selector = selector

    @_check_result
    def get_first(self):
        """Returns first item"""
        return self.driver.find_element_by_css_selector(self.selector)

    def get_all(self):
        """Returns all items"""
        return self.driver.find_elements_by_css_selector(self.selector)


class SelectorName(Selector):
    """Selector for Named items"""
    def __init__(self, driver, selector):
        self.driver = driver
        self.selector = selector

    @_check_result
    def get_first(self):
        """Returns first item"""
        return self.driver.find_element_by_name(self.selector)

    def get_all(self):
        """Returns all items"""
        return self.driver.find_elements_by_name(self.selector)

class SelectorID(Selector):
    """
    Selector for ID items.
    Only has the one method, since there should only
    be one element with a given ID.
    """
    def __init__(self, driver, selector):
        self.driver = driver
        self.selector = selector

    @_check_result
    def get_first(self):
        """Returns first item"""
        return self.driver.find_element_by_id(self.selector)

class SelectorClass(Selector):
    """Select for CSS Class items"""
    def __init__(self, driver, selector):
        self.driver = driver
        self.selector = selector

    @_check_result
    def get_first(self):
        """Returns first item"""
        return self.driver.find_element_by_class_name(self.selector)

    def get_all(self):
        """Returns all items"""
        return self.driver.find_elements_by_class_name(self.selector)

class SelectorXpath(Selector):
    """Selector for xpath strings; a more robust way to search for items"""
    def __init__(self, driver, selector):
        self.driver = driver
        self.selector = selector

    @_check_result
    def get_first(self):
        """Return first item"""
        return self.driver.find_element_by_xpath(self.selector)

    def get_all(self):
        """Return all items"""
        return self.driver.find_elements_by_xpath(self.selector)
