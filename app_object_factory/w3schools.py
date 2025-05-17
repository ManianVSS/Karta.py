from typing import Optional

from selenium.common import StaleElementReferenceException, NoSuchElementException, TimeoutException

from framework.web.factory import WebAUT, Page
from framework.web.models import WebDriverConfig


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

    def initialize_application(self) -> Optional[Page]:
        self.init_web_driver()
        self.driver.get(self.url)
        return HomePage(self)


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

    def open_learn_html_page(self):
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

    def open_home_page(self):
        self.logo.click()
        return HomePage(self.application)

    def open_html_intro_page(self):
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

    def open_home_page(self):
        self.logo.click()
        return HomePage(self.application)

    def open_learn_html_page(self):
        self.html_home_button.click()
        return HTMLHomePage(self.application)
