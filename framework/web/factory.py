import abc
import os
from typing import Optional
from typing import Union

import yaml
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver import Proxy
from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from framework.web.models import WebDriverConfig, Browser, Locator

HEADLESS = "--headless"
ALLOW_ORIGINS_ = "--remote-allow-origins=*"
NO_SANDBOX = "--no-sandbox"

desired_capability_map = {
    Browser.CHROME: DesiredCapabilities.CHROME,
    Browser.FIREFOX: DesiredCapabilities.FIREFOX,
    Browser.EDGE: DesiredCapabilities.EDGE,
    Browser.SAFARI: DesiredCapabilities.SAFARI
}

webdriver_options_classmap = {
    Browser.CHROME: ChromeOptions,
    Browser.FIREFOX: FirefoxOptions,
    Browser.EDGE: EdgeOptions,
    Browser.SAFARI: SafariOptions
}

webdriver_service_classmap = {
    Browser.CHROME: ChromeService,
    Browser.FIREFOX: FirefoxService,
    Browser.EDGE: EdgeService,
    Browser.SAFARI: SafariService
}

webdriver_classmap = {
    Browser.CHROME: ChromeDriver,
    Browser.FIREFOX: FirefoxDriver,
    Browser.EDGE: EdgeDriver,
    Browser.SAFARI: SafariDriver
}

default_browser_arguments = {
    Browser.CHROME: [NO_SANDBOX, ALLOW_ORIGINS_],
    Browser.EDGE: [NO_SANDBOX, ALLOW_ORIGINS_],
}


def create_web_driver(webdriver_config: WebDriverConfig):
    """
    Create a web driver instance based on the provided options.
    """
    webdriver = None

    webdriver_options = webdriver_options_classmap[webdriver_config.browser]()

    if webdriver_config.binary_location:
        webdriver_options.binary_location = webdriver_config.binary_location

    if webdriver_config.headless:
        webdriver_options.add_argument(HEADLESS)

    webdriver_options.accept_insecure_certs = webdriver_config.ignore_certificates

    if webdriver_config.browser in default_browser_arguments:
        for argument in default_browser_arguments[webdriver_config.browser]:
            webdriver_options.add_argument(argument)

    for additional_argument in webdriver_config.additionalArguments:
        webdriver_options.add_argument(additional_argument)

    for capability, value in webdriver_config.capabilities:
        webdriver_options.set_capability(capability, value)

    if webdriver_config.proxy_configuration:
        proxy = Proxy(webdriver_config.proxy_configuration)
        webdriver_options.proxy(proxy)

    if webdriver_config.remote:
        capabilities = desired_capability_map[webdriver_config.browser].copy()
        capabilities.update(webdriver_config.capabilities)
        webdriver = Remote(options=webdriver_options, )
    elif webdriver_config.use_service:
        webdriver_service = webdriver_service_classmap[webdriver_config.browser](
            executable_path=webdriver_config.driver_location,
            port=webdriver_config.service_port,
            args=webdriver_config.service_args,
            env=os.environ)

        webdriver = webdriver_classmap[webdriver_config.browser](service=webdriver_service,
                                                                 options=webdriver_options)
    else:
        webdriver = webdriver_classmap[webdriver_config.browser](options=webdriver_options)

    if webdriver_config.delete_all_cookies:
        webdriver.delete_all_cookies()

    if webdriver_config.resize:
        if webdriver_config.screen_size.maximized:
            webdriver.maximize_window()
        elif webdriver_config.screen_size.fullscreen:
            webdriver.fullscreen_window()
        else:
            webdriver.set_window_size(webdriver_config.screen_size.width,
                                      webdriver_config.screen_size.height)

    webdriver.timeouts.implicit_wait = webdriver_config.implicit_wait

    return webdriver


class PageException(Exception):
    """Custom exception for page-related errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class Element:
    driver: Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver, Remote] = None
    locator: Locator
    _element: WebElement

    def __init__(self, locator: Locator, driver: Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver]):
        if not locator or not isinstance(locator, Locator):
            raise TypeError("locator must be an instance of Locator")
        if not driver or not isinstance(driver, (ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver, Remote)):
            raise ValueError("driver must be provided of type WebDriver")
        self.locator = locator
        self.driver = driver

    # TODO: All methods need to handle parent iframe and shadow roots
    def wait_for_visibility(self, timeout: int = 10) -> bool:
        """
        Wait for the element to be visible on the page.
        :param timeout:
        :return:
        """
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((self.locator.get_selenium_by())))
        return True

    def wait_for_clickable(self, timeout: int = 10) -> bool:
        """
        Wait for the element to be clickable on the page.
        :param timeout:
        :return:
        """
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((self.locator.get_selenium_by())))
        return True

    def wait_for_invisibility(self, timeout: int = 10) -> bool:
        """
        Wait for the element to be invisible on the page.
        :param timeout:
        :return:
        """
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((self.locator.get_selenium_by())))
        return True

    def click(self):
        """
        Click the element.
        :return:
        """
        self.wait_for_visibility()
        self.wait_for_clickable()
        self._element = self.driver.find_element(*self.locator.get_selenium_by())
        self._element.click()

    def send_keys(self, keys: str):
        """
        Send keys to the element.
        :param keys:
        :return:
        """
        self.wait_for_visibility()
        self.wait_for_clickable()
        self._element = self.driver.find_element(*self.locator.get_selenium_by())
        self._element.send_keys(keys)

    def get_text(self) -> str:
        """
        Get the text of the element.
        :return:
        """
        self.wait_for_visibility()
        self._element = self.driver.find_element(*self.locator.get_selenium_by())
        return self._element.text

    def get_attribute(self, attribute: str) -> str:
        """
        Get the attribute of the element.
        :param attribute:
        :return:
        """
        self.wait_for_visibility()
        self._element = self.driver.find_element(*self.locator.get_selenium_by())
        return self._element.get_attribute(attribute)

    def is_displayed(self) -> bool:
        """
        Check if the element is displayed.
        :return:
        """
        try:
            self._element = self.driver.find_element(*self.locator.get_selenium_by())
            return self._element.is_displayed()
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as _:
            return False

    def is_enabled(self) -> bool:
        """
        Check if the element is enabled.
        :return:
        """
        try:
            self._element = self.driver.find_element(*self.locator.get_selenium_by())
            return self._element.is_enabled()
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as _:
            return False

    def is_selected(self) -> bool:
        """
        Check if the element is selected.
        :return:
        """
        try:
            self._element = self.driver.find_element(*self.locator.get_selenium_by())
            return self._element.is_selected()
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as _:
            return False

    def get_element(self) -> WebElement:
        """
        Get the web element.
        :return:
        """
        self.wait_for_visibility()
        self._element = self.driver.find_element(*self.locator.get_selenium_by())
        return self._element

    def get_elements(self) -> list[WebElement]:
        """
        Get the web elements.
        :return:
        """
        self.wait_for_visibility()
        elements = self.driver.find_elements(*self.locator.get_selenium_by())
        return elements if elements else []

    def get_screenshot(self, filename: str):
        """
        Take a screenshot of the element.
        :param filename:
        :return:
        """
        self.wait_for_visibility()
        self._element = self.driver.find_element(*self.locator.get_selenium_by())
        self._element.screenshot(filename)

    def get_screenshot_as_base64(self) -> str:
        """
        Get the screenshot of the element as base64.
        :return:
        """
        self.wait_for_visibility()
        self._element = self.driver.find_element(*self.locator.get_selenium_by())
        return self._element.screenshot_as_base64

    def get_screenshot_as_png(self) -> bytes:
        """
        Get the screenshot of the element as png.
        :return:
        """
        self.wait_for_visibility()
        self._element = self.driver.find_element(*self.locator.get_selenium_by())
        return self._element.screenshot_as_png

    def save_screenshot_to_file(self, filename: str) -> bool:
        """
        Get the screenshot of the element as file.
        :param filename:
        :return:
        """
        self.wait_for_visibility()
        self._element = self.driver.find_element(*self.locator.get_selenium_by())
        return self._element.screenshot(filename)

    def __str__(self):
        return f"Element(locator={self.locator}, driver={self.driver})"

    def __repr__(self):
        return f"Element(locator={self.locator}, driver={self.driver})"

    def __eq__(self, other):
        if not isinstance(other, Element):
            return False
        return self.locator == other.locator and self.driver == other.driver

    def __hash__(self):
        return hash((self.locator, self.driver))


class Page(metaclass=abc.ABCMeta):
    elements: Optional[dict[str, Element]] = {}
    driver: Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver, Remote] = None
    application: Optional['WebAUT'] = None

    def __init__(self, application: 'WebAUT'):
        if not application or not isinstance(application, WebAUT):
            raise TypeError("application must be an instance of WebAUT")
        if not application.driver:
            raise ValueError("WebAUT instance must have a driver")
        self.driver = application.driver
        self.application = application
        self.application.current_page = self

        # For each locator from WebAUT page_locators, create an Element instance
        for element_name, locator in self.application.page_locators[self.__class__.__name__].items():
            if not isinstance(locator, Locator):
                raise TypeError(f"Locator for {element_name} must be an instance of Locator")
            self.elements[element_name] = Element(locator, self.driver)

        if not self.validate():
            raise PageException(f"Page validation failed for {self.__class__.__name__}")

    def __getattr__(self, attr):
        """
        This method is called when an attribute is not found in the instance.
        It allows accessing elements by their names.
        :param attr:
        :return:
        """
        if attr in self.__dict__:
            return self.__dict__[attr]
        elif attr in self.elements:
            return self.elements[attr]
        else:
            raise AttributeError(f"Attribute or element '{attr}' not found in page class {self.__class__.__name__}")

    @abc.abstractmethod
    def validate(self) -> bool:
        raise NotImplementedError


class WebAUT(metaclass=abc.ABCMeta):
    name: Optional[str] = None
    url: Optional[str] = None

    webdriver_config: Optional[WebDriverConfig] = None
    page_locators: Optional[dict[str, dict[str, Locator]]] = {}

    driver: Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver, None] = None
    current_page: Optional[Page] = None

    def __init__(self, webdriver_config: WebDriverConfig):
        if not webdriver_config or not isinstance(webdriver_config, WebDriverConfig):
            raise TypeError("webdriver_config must be an instance of WebDriverConfig")
        self.webdriver_config = webdriver_config

    def init_web_driver(self):
        """
        Create a web driver instance based on the provided options.
        """
        self.driver = create_web_driver(self.webdriver_config)
        if not self.driver:
            raise ValueError("Failed to create web driver instance")

    def load_locators_from_file(self, locators_file: str):
        """
        Load locators from a file.
        :param locators_file:
        :return:
        """
        if not os.path.exists(locators_file):
            raise FileNotFoundError(f"File not found: {locators_file}")

        # Read the locators YAML file and parse it
        with open(locators_file, 'r') as file:
            locators_data = yaml.safe_load(file)

        # Validate the structure of the locators data
        if not isinstance(locators_data, dict):
            raise ValueError("Invalid locators file format. Expected a dictionary.")

        page_locators = {}
        for page_name, page_locator_data in locators_data.items():
            if not isinstance(page_locator_data, dict):
                raise ValueError(f"Invalid locators format for page '{page_name}'. Expected a dictionary.")

            page_locators[page_name] = {}
            for element_name, locator_data in page_locator_data.items():
                locator = Locator.convert_from_dict(locator_data)
                if not locator or not isinstance(locator, Locator):
                    raise ValueError(f"Invalid locator format for element '{element_name}' on page '{page_name}'. "
                                     f"Check syntax.")

                page_locators[page_name][element_name] = locator
        self.page_locators = page_locators

    @abc.abstractmethod
    def initialize_application(self) -> Optional[Page]:
        """
        Initialize the application by creating the web driver instance and return start page.
        :return:
        """
        raise NotImplementedError

    def close(self):
        """
        Close the web driver instance.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        """
        Enter the context manager.
        Web driver will not initialize automatically. Need to call initialize_application() explicitly.
        :return:
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager.
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.close()
