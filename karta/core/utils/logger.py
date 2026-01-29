import logging
import os
import time

# Create a logger
logger = logging.getLogger('karta_logger')
logger.setLevel(logging.DEBUG)

# Create a formatter to define the log format
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')

os.makedirs("logs", exist_ok=True)
# Create a file handler to write logs to a file
file_name = 'logs/kartaRun{}.log'.format(time.strftime("%Y_%m_%d-%H_%M_%S"))
file_handler = logging.FileHandler(file_name)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create a stream handler to print logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # You can set the desired log level for console output
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
