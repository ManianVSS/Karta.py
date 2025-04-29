import abc
from enum import Enum
from typing import Optional
from typing import Union

from pydantic.v1 import BaseModel
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver


class Browser(Enum):
    FIREFOX = "firefox",
    CHROME = "chrome",
    EDGE = "edge",
    SAFARI = "Safari",


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



