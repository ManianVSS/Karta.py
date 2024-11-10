import json

from framework.core.runner.main import *
from framework.core.utils import JSONEncoders

karta_runtime = KartaRuntime(step_def_package='step_definitions')
karta_runtime.init_framework()

feature_result1 = karta_runtime.run_feature_file('features/test.yaml')
feature_result2 = karta_runtime.run_feature_file('features/test2.yaml')
print('Feature result1 is ' + str(feature_result1))
print('Feature result2 is ' + str(feature_result2))
