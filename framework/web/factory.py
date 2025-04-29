import abc
import os
from typing import Optional
from typing import Union

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
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver

from framework.web.models import WebDriverConfig, Browser

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

    for additonal_argument in webdriver_config.additionalArguments:
        webdriver_options.add_argument(additonal_argument)

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


class Page(metaclass=abc.ABCMeta):
    driver: Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver] = None
    application: Optional['WebAUT'] = None

    def __init__(self, application: 'WebAUT'):
        if not application or not isinstance(application, WebAUT):
            raise TypeError("application must be an instance of WebAUT")
        if not application.driver:
            raise ValueError("WebAUT instance must have a driver")
        self.driver = application.driver
        self.application = application

    @abc.abstractmethod
    def validate(self):
        raise NotImplementedError


class WebAUT(metaclass=abc.ABCMeta):
    name: Optional[str] = None
    webdriver_config: Optional[WebDriverConfig] = None
    driver: Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver] = None

    @abc.abstractmethod
    def open_start_page(self):
        raise NotImplementedError
