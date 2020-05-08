from django.conf import settings
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait


class CustomChromeWebDriver(Chrome):
    """Our own WebDriver with some helpers added"""
    def clean(self, elems):
        found = len(elems)
        if found == 1:
            return elems[0]
        elif not elems:
            raise NoSuchElementException(id)
        return elems

    def find_css(self, css_selector):
        """Shortcut to find elements by CSS. Returns either a list or singleton"""
        elems = self.find_elements_by_css_selector(css_selector)
        return self.clean(elems)

    def wait_for_css(self, css_selector, timeout=7):
        """ Shortcut for WebDriverWait"""
        return WebDriverWait(self, timeout).until(lambda driver : driver.find_css(css_selector))

    def find_id(self, id):
        elems = self.find_elements_by_id(id)
        return self.clean(elems)

    def find_xpath(self, xpath):
        elems = self.find_elements_by_xpath(xpath)
        return self.clean(elems)

    def find_link_text(self, text):
        elems = self.find_elements_by_link_text(text)
        return self.clean(elems)

    def find_name(self, name):
        elems = self.find_elements_by_name(name)
        return self.clean(elems)

    def find_class(self, cname):
        elems = self.find_elements_by_class_name(cname)
        return self.clean(elems)