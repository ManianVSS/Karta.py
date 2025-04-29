import time

from framework.web.factory import create_web_driver, ChromeDriver, FirefoxDriver
from framework.web.models import WebDriverConfig, Browser, ScreenSize


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


if __name__ == '__main__':
    test_chrome_driver_creation()
    test_firefox_driver_creation()
    test_firefox_marionette_service_creation()
    test_firefox_remote_driver_creation()
