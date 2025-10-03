from step_definitions._w3schools import W3SchoolsApp, HomePage, HTMLHomePage, HTMLIntroductionPage
from karta.core.utils.logger import logger
from karta.plugins.dependency_injector import Inject
from karta.plugins.kriya import step_def
from karta.web.models import WebDriverConfig

test_properties = Inject("properties")


@step_def("w3schools application is launched")
def my_sample_step_definition3(context=None):
    logger.info("context is %s", str(context))
    browser = context.step_data.get('browser', 'chrome')
    web_driver_config = WebDriverConfig.validate(test_properties["w3schools_webdriver_config_" + browser])
    context.w3schools_app = W3SchoolsApp(web_driver_config, 'locators/W3SchoolsApp.yaml')
    home_page = context.w3schools_app.initialize_application()
    return (home_page is not None) and (home_page == context.w3schools_app.current_page)


@step_def("w3schools home page is opened")
def w3schools_home_page_is_opened(context=None):
    logger.info("context is %s", str(context))
    home_page = context.w3schools_app.current_page.open_home_page()
    return isinstance(home_page, HomePage)


@step_def("w3schools learn html home page is opened")
def w3schools_learn_html_home_page_is_opened(context=None):
    logger.info("context is %s", str(context))
    home_page = context.w3schools_app.current_page.open_learn_html_page()
    return isinstance(home_page, HTMLHomePage)


@step_def("w3schools learn html introduction page is opened")
def w3schools_learn_html_introduction_page_is_opened(context=None):
    logger.info("context is %s", str(context))
    html_introduction_page = context.w3schools_app.current_page.open_html_intro_page()
    return isinstance(html_introduction_page, HTMLIntroductionPage)


@step_def("w3schools application is closed")
def w3schools_application_is_closed(context=None):
    logger.info("context is %s", str(context))
    context.w3schools_app.close()
    return context.w3schools_app.driver is None
