import time

import yaml

from w3schools import W3SchoolsApp, HomePage, HTMLHomePage, HTMLIntroductionPage
from karta.web.factory import create_web_driver, ChromeDriver
from karta.web.models import WebDriverConfig, Browser, ScreenSize


def test_chrome_driver_creation():
    """ Test the creation of a Chrome web driver instance """
    config = WebDriverConfig(
        browser=Browser.CHROME,
        driver_location="/usr/bin/chromedriver",
        headless=False,
        remote=False,
        resize=True,
        screen_site=ScreenSize(maximized=True),
    )
    driver = create_web_driver(config)
    driver.get("https://w3schools.com")
    time.sleep(1)  # Allow time for the driver to initialize
    assert isinstance(driver, ChromeDriver)


def test_firefox_driver_creation():
    """ Test the creation of a Firefox web driver instance """
    config = WebDriverConfig(
        browser=Browser.FIREFOX,
        driver_location="/usr/bin/geckodriver",
        binary_location="/home/manian/Downloads/firefox/firefox",
        resize=True,
        screen_site=ScreenSize(maximized=True),
    )
    driver = create_web_driver(config)
    driver.get("https://w3schools.com")
    time.sleep(1)  # Allow time for the driver to initialize
    driver.quit()


def test_firefox_marionette_service_creation():
    """
    Test the creation of a Firefox web driver using firefox service and marionette port to latch to existing browser
    """
    config = WebDriverConfig(
        browser=Browser.FIREFOX,
        driver_location="/usr/bin/geckodriver",
        binary_location="/home/manian/Downloads/firefox/firefox",
        use_service=True,
        service_args=['--marionette-port', '2828', '--connect-existing'],
        resize=True,
        screen_site=ScreenSize(maximized=True),
    )
    driver = create_web_driver(config)
    driver.get("https://w3schools.com")
    time.sleep(1)  # Allow time for the driver to initialize
    driver.quit()


def test_firefox_remote_driver_creation():
    """
    Test the creation of a Firefox web driver instance
    """
    config = WebDriverConfig(
        browser=Browser.FIREFOX,
        driver_location="/usr/bin/geckodriver",
        remote=True,
        resize=True,
        screen_site=ScreenSize(maximized=True),
    )
    driver = create_web_driver(config)
    driver.get("https://w3schools.com")
    time.sleep(1)  # Allow time for the driver to initialize
    driver.quit()


def test_appliction_objet_model():
    web_driver_config_file = '../properties/webdriver_config.yaml'
    with open(web_driver_config_file, 'r') as file:
        config_data = yaml.safe_load(file)
    web_driver_config = WebDriverConfig.validate(config_data["w3schools_webdriver_config_firefox"])

    with W3SchoolsApp(web_driver_config, '../locators/W3SchoolsApp.yaml') as w3schools_app:
        home_page: HomePage = w3schools_app.initialize_application()
        html_home_page = w3schools_app.home_page.open_learn_html_page()
        html_intro_page = w3schools_app.html_home_page.open_html_intro_page()
        html_home_page = w3schools_app.html_introduction_page.open_learn_html_page()
        home_page = w3schools_app.html_home_page.open_home_page()

        assert isinstance(home_page, HomePage) and (
                home_page == w3schools_app.current_page), "Home page is not initialized correctly"

    # Close the application using context manager and check if the driver is None
    assert w3schools_app.driver is None


if __name__ == '__main__':
    # test_chrome_driver_creation()
    # test_firefox_driver_creation()
    # test_firefox_marionette_service_creation()
    # test_firefox_remote_driver_creation()

    test_appliction_objet_model()
