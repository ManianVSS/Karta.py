from typing import Optional

from selenium.common import StaleElementReferenceException, NoSuchElementException, TimeoutException

from karta.web.factory import WebAUT, Page, PageException
from karta.web.models import WebDriverConfig


class W3SchoolsApp(WebAUT):
    """
    W3Schools web application object factory for web automation testing.
    This class is used to create and manage web application objects for testing purposes.
    """

    def __init__(self, web_driver_config: WebDriverConfig, locator_file: str):
        super().__init__(web_driver_config)
        self.name = "W3Schools"
        self.url = "https://www.w3schools.com/"

        self.load_locators_from_file(locator_file)

    def initialize_application(self) -> "HomePage":
        self.init_web_driver()
        self.driver.get(self.url)
        return HomePage(self)

    # Add properties for commonly accessed pages if needed
    @property
    def home_page(self) -> "HomePage":
        # Check if current page is HomePage, if not raise an exception
        if self.current_page and isinstance(self.current_page, HomePage):
            return self.current_page
        else:
            raise PageException("Current page is not HomePage")

    @property
    def html_home_page(self) -> "HTMLHomePage":
        # Check if current page is HTMLHomePage, if not raise an exception
        if self.current_page and isinstance(self.current_page, HTMLHomePage):
            return self.current_page
        else:
            raise PageException("Current page is not HTMLHomePage")

    @property
    def html_introduction_page(self) -> "HTMLIntroductionPage":
        # Check if current page is HTMLIntroductionPage, if not raise an exception
        if self.current_page and isinstance(self.current_page, HTMLIntroductionPage):
            return self.current_page
        else:
            raise PageException("Current page is not HTMLIntroductionPage")


class HomePage(Page):
    """
    Home page of W3Schools web application.
    This class is used to represent the home page of the W3Schools web application.
    """

    def __init__(self, app: WebAUT):
        super().__init__(app)

    def validate(self) -> bool:
        try:
            return self.logo.wait_for_visibility()
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as _:
            return False

    def open_learn_html_page(self) -> "HTMLHomePage":
        self.learn_html_button.click()
        return HTMLHomePage(self.application)


class HTMLHomePage(Page):
    """
    HTML Home page of W3Schools web application.
    This class is used to represent the HTML home page of the W3Schools web application.
    """

    def __init__(self, application: WebAUT):
        super().__init__(application)

    def validate(self) -> bool:
        try:
            return self.html_tuturial_text.wait_for_visibility()
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as _:
            return False

    def open_home_page(self) -> "HomePage":
        self.logo.click()
        return HomePage(self.application)

    def open_html_intro_page(self) -> "HTMLIntroductionPage":
        self.html_introduction_button.click()
        return HTMLIntroductionPage(self.application)


class HTMLIntroductionPage(Page):
    """
    HTML introduction page of W3Schools web application.
    This class is used to represent the HTML introduction page of the W3Schools web application.
    """

    def __init__(self, application: WebAUT):
        super().__init__(application)

    def validate(self) -> bool:
        try:
            return self.html_introduction_text.wait_for_visibility()
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as _:
            return False

    def open_home_page(self) -> "HomePage":
        self.logo.click()
        return HomePage(self.application)

    def open_learn_html_page(self) -> "HTMLHomePage":
        self.html_home_button.click()
        return HTMLHomePage(self.application)
