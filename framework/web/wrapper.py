from typing import Union

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver


class WebDriverWrapper:
    driver: Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver]

    def __init__(self, driver):
        self.driver = driver

    def get(self, url):
        self.driver.get(url)

    def find_element(self, *args, **kwargs):
        return self.driver.find_element(*args, **kwargs)

    def save_screenshot(self, filename):
        self.driver.save_screenshot(filename)

    def quit(self):
        self.driver.quit()
