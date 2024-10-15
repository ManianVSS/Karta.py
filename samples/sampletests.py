from framework.core.runner.main import *

init_framework('step_definitions')

run_feature_file('features/test.yaml')
run_feature_file('features/test2.yaml')
