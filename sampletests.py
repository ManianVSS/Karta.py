from framework.core.runner.main import *

karta_runtime = KartaRuntime(step_def_package='step_definitions')
karta_runtime.init_framework()

feature_result1 = karta_runtime.run_feature_file('features/test.yaml')
print('Feature result1 is ' + str(feature_result1))
feature_result2 = karta_runtime.run_feature_file('features/test2.yaml')
print('Feature result2 is ' + str(feature_result2))
feature_result3 = karta_runtime.run_feature_file('features/test3.feature')
print('Feature result3 is ' + str(feature_result3))
