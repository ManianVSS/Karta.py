from enum import Enum
from typing import Optional

from pydantic.v1 import BaseModel
from selenium.webdriver.common.by import By

from framework.core.models.generic import Context


class Browser(Enum):
    FIREFOX = "firefox"
    CHROME = "chrome"
    EDGE = "edge"
    SAFARI = "Safari"


class ScreenSize(BaseModel):
    maximized: Optional[bool] = False
    fullscreen: Optional[bool] = False
    width: Optional[int] = 1920
    height: Optional[int] = 1080

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class WebDriverConfig(BaseModel):
    driver_location: Optional[str] = "chromedriver"
    binary_location: Optional[str] = None
    browser: Optional[Browser] = Browser.CHROME
    proxy_configuration: Optional[dict] = {}
    remote: Optional[bool] = False
    use_service: Optional[bool] = False
    service_args: Optional[list[str]] = []
    service_port: Optional[int] = 4444
    delete_all_cookies: Optional[bool] = True
    headless: Optional[bool] = False
    ignore_certificates: Optional[bool] = True
    resize: Optional[bool] = False
    screen_size: Optional[ScreenSize] = ScreenSize()
    implicit_wait: Optional[int] = 0
    explicit_wait: Optional[int] = 0
    additionalArguments: Optional[list[str]] = []
    capabilities: Optional[dict] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


LocatorType: Context = Context({
    'ID': By.ID,
    'XPATH': By.XPATH,
    'LINK_TEXT': By.LINK_TEXT,
    'PARTIAL_LINK_TEXT': By.PARTIAL_LINK_TEXT,
    'NAME': By.NAME,
    'TAG': By.TAG_NAME,
    'CLASS': By.CLASS_NAME,
    'CSS': By.CSS_SELECTOR
})


class Locator(BaseModel):
    """
    Locator class for web elements

    Attributes:
        type (str): The type of locator (ID, XPATH, etc.)
        selector (str): The selector string for the locator
        multiple (bool): Whether to find multiple elements or not

        iframe (Optional[str]): The iframe locator name if this element is inside an iframe.
                                This loator should be present in the page's locator.
        shadow_root (Optional[str]): The shadown root locator name if this element is inside a shadow root.
                                This loator should be present in the page's locator.
                                Iframe take precedence over shadow_root.
    """
    type: Optional[str] = LocatorType.CSS
    selector: str = ""
    multiple: Optional[bool] = False
    iframe: Optional[str] = None
    shadow_root: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_selenium_by(self) -> tuple[str, str]:
        """
        Get the selenium By tuple for the locator type sutable for use with Selenium's find element methods.
        :return: tuple of (by, selector)
        """
        if self.type in LocatorType.keys():
            return LocatorType[self.type], self.selector
        else:
            raise ValueError(f"Invalid locator type: {self.type}")

    @classmethod
    def convert_from_dict(cls, locator_dict: dict) -> Optional['Locator']:
        """
        Validate and convert a dictionary to a Locator object.
        :param locator_dict: The dictionary to convert
        :return: A Locator object or None if the dictionary is invalid
        """

        if not isinstance(locator_dict, dict):
            return None
            # Check if all locators in locators_data have right parameters
        if not all(key in ['type', 'selector', 'multiple', 'iframe', 'shadow_root'] for key in
                   locator_dict.keys()):
            return None
        if 'selector' not in locator_dict:
            return None

        locator = Locator(
            type=locator_dict.get('type', 'CSS'),
            selector=locator_dict['selector'],
            multiple=locator_dict.get('multiple', False),
        )

        return locator
