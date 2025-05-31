from enum import Enum
from typing import Optional

from pydantic.v1 import BaseModel
from selenium.webdriver.common.by import By


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


class LocatoryType(Enum):
    ID = "ID"
    XPATH = "XPATH"
    LINK_TEXT = "LINK_TEXT"
    PARTIAL_LINK_TEXT = "PARTIAL_LINK_TEXT"
    NAME = "NAME"
    TAG = "TAG"
    CLASS = "CLASS"
    CSS = "CSS"


class ContainerType(Enum):
    IFRAME = "IFRAME"
    SHADOW_ROOT = "SHADOW_ROOT"
    BUTTON = "BUTTON"
    TEXT_FIELD = "TEXT_FIELD"
    CHECKBOX = "CHECKBOX"
    LISTBOX = "LISTBOX"
    COMBOBOX = "COMBOBOX"
    GENERIC_ELEMENT = "GENERIC_ELEMENT"


class Locator(BaseModel):
    """
    Locator class for web elements

    Attributes:
        type (LocatoryType): The type of locator (ID, XPATH, etc.)
        selector (str): The selector string for the locator
        multiple (bool): Whether to find multiple elements or not
        container_type (ContainerType): The type of container this element is if it is a parent(IFRAME, SHADOW_ROOT)
        parent (Optional[str]): The parent locator name if this element is inside a container.
                                This loator should be present in the page's locator.
    """
    type: Optional[LocatoryType] = LocatoryType.CSS
    selector: str = ""
    multiple: Optional[bool] = False
    container_type: Optional[ContainerType] = None
    parent: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_selenium_by(self) -> tuple[str, str]:
        """
        Get the selenium By tuple for the locator type sutable for use with Selenium's find element methods.
        :return: tuple of (by, selector)
        """
        if self.type == LocatoryType.ID:
            return By.ID, self.selector
        elif self.type == LocatoryType.XPATH:
            return By.XPATH, self.selector
        elif self.type == LocatoryType.LINK_TEXT:
            return By.LINK_TEXT, self.selector
        elif self.type == LocatoryType.PARTIAL_LINK_TEXT:
            return By.PARTIAL_LINK_TEXT, self.selector
        elif self.type == LocatoryType.NAME:
            return By.NAME, self.selector
        elif self.type == LocatoryType.TAG:
            return By.TAG_NAME, self.selector
        elif self.type == LocatoryType.CLASS:
            return By.CLASS_NAME, self.selector
        elif self.type == LocatoryType.CSS:
            return By.CSS_SELECTOR, self.selector
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
        if not all(key in ['type', 'selector', 'multiple', 'container_type', 'parent'] for key in
                   locator_dict.keys()):
            return None
        if 'selector' not in locator_dict:
            return None

        locator = Locator(
            type=locator_dict.get('type', LocatoryType.CSS),
            selector=locator_dict['selector'],
            multiple=locator_dict.get('multiple', False),
            container_type=ContainerType(
                locator_dict['container_type']) if 'container_type' in locator_dict else None
        )

        return locator
