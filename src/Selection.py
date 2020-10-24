from selenium.common.exceptions import (
    InvalidArgumentException,
    NoSuchElementException
)


def create_selector(driver, element_type, selector):
    if element_type == "css":
        return SelectorCSS(driver, selector)
    if element_type == "name":
        return SelectorName(driver, selector)
    return None


def _check_result(func):
    def check_result(self):
        try:
            return [func(self)]
        except NoSuchElementException:
            return []
    return check_result


class Selector:
    def __init__(self, driver):
        self.driver = driver

    def get_first(self):
        pass

    def get_all(self):
        pass


class SelectorCSS(Selector):
    def __init__(self, driver, selector):
        super().__init__(driver)
        self.selector = selector

    @_check_result
    def get_first(self):
        return self.driver.find_element_by_css_selector(self.selector)

    def get_all(self):
        return self.driver.find_elements_by_css_selector(self.selector)


class SelectorName(Selector):
    def __init__(self, driver, selector):
        super().__init__(driver)
        self.selector = selector

    @_check_result
    def get_first(self):
        return self.driver.find_element_by_name(self.selector)

    def get_all(self):
        return self.driver.find_elements_by_name(self.selector)
