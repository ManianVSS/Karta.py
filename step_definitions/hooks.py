from app_object_factory.w3schools import W3SchoolsApp
from framework.core.utils.logger import logger
from framework.plugins.dependency_injector import Inject
from framework.plugins.kriya import before_run, before_feature, before_scenario, after_scenario, after_feature, \
    after_run
from framework.web.models import WebDriverConfig

test_properties = Inject("properties")


@before_run()
def before_run_hook(context=None):
    logger.info("Before run hook")


@before_feature()
def before_feature_hook(context=None):
    logger.info("Before feature hook")


@before_scenario()
def before_scenario_hook(context=None):
    logger.info("Before scenario hook")


@before_scenario("^chrome$")
def before_chrome_scenario_hook(context=None):
    logger.info("Before chrome scenario hook")
    web_driver_config = WebDriverConfig.validate(test_properties["w3schools_webdriver_config_chrome"])
    context.w3schools_app = W3SchoolsApp(web_driver_config, 'locators/W3SchoolsApp.yaml')
    context.w3schools_app.initialize_application()


@before_scenario("^firefox$")
def before_firefox_scenario_hook(context=None):
    logger.info("Before firefox scenario hook")
    web_driver_config = WebDriverConfig.validate(test_properties["w3schools_webdriver_config_firefox"])
    context.w3schools_app = W3SchoolsApp(web_driver_config, 'locators/W3SchoolsApp.yaml')
    context.w3schools_app.initialize_application()


@after_scenario("^(w3schools|firefox|chrome)$")
def after_web_test_scenario_hook(context=None):
    logger.info("After web test scenario hook")
    context.w3schools_app.close()
    context.w3schools_app = None


@after_scenario()
def after_scenario_hook(context=None):
    logger.info("After scenario hook")


@after_feature()
def after_feature_hook(context=None):
    logger.info("After feature hook")


@after_run()
def after_run_hook(context=None):
    logger.info("After run hook")
