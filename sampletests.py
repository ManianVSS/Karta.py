from framework.runner.runtime import karta_runtime
from framework.core.utils.logger import logger

# feature_result1 = karta_runtime.run_feature_file('features/test.yaml')
# logger.info('Feature result1 is %s', str(feature_result1))
# feature_result2 = karta_runtime.run_feature_file('features/test2.yaml')
# logger.info('Feature result2 is %s', str(feature_result2))
# feature_result3 = karta_runtime.run_feature_file('features/test3.feature')
# logger.info('Feature result3 is %s', str(feature_result3))
# feature_result4 = karta_runtime.run_feature_file('features/test4.feature')
# logger.info('Feature result4 is %s', str(feature_result4))

tags_list = [['my_tag1', 'my_scenario_tag_3'], ['my_tag4', 'my_tag3', 'my_tag2']]

for tag_list in tags_list:
    logger.info(
        'Running scenarios with tags {} and result is {}'.format(tag_list, str(karta_runtime.run_tags(tag_list))))
