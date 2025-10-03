from karta.core.models.test_execution import TestIncident
from karta.web.factory import PageException

test_incident = TestIncident(message="Test incident occurred", tags={"tag1", "tag2"},
                             exception=PageException("Test exception"))

print(test_incident)
#
# try:
#     raise PageException("Testing raising exception")
# except PageException as e:
#     _, _, tb = sys.exc_info()
#
#     # Format the original traceback
#     formatted_trace = traceback.format_tb(tb)
#     print(formatted_trace)
#
#     # Add custom trace information
#     custom_trace = ["Custom trace added here:", "  File: custom_file.py, line 10, in custom_function",
#                     "    # Additional context"]
#
#     # Combine the traces
#     combined_trace = custom_trace + formatted_trace
#
#     # Format the combined trace for printing
#     formatted_combined_trace = "".join(combined_trace)
#
#     # Re-raise the exception with the modified traceback
#     raise type(e)(str(e) + "\n" + formatted_combined_trace).with_traceback(tb)
