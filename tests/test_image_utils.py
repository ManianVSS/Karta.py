from time import time

import numpy as np
from PIL import Image

from karta.core.utils.imageutils import ScreenCapture

if __name__ == '__main__':

    with ScreenCapture(frame_rate=10, monitor=2) as screen_capture:
        # Capture starting screenshot
        screen_capture.save_screenshot("initial_screenshot.png")

        start_time = time()
        changed, timestamp = screen_capture.wait_until_frame_changes(timeout=10, check_interval=0.5)
        if changed:
            print(f"Frame changed at {timestamp} in {timestamp - start_time} seconds")
        else:
            print("No frame change detected within the timeout period.")

        start_time = time()
        initial_image_data = np.array(Image.open("initial_screenshot.png")).tobytes()
        matched, timestamp = screen_capture.wait_until_frame_matches(
            image_rgb_data=initial_image_data,
            timeout=10,
            check_interval=0.5,
        )
        if matched:
            print(f"Frame matched initial screenshot at {timestamp} in {timestamp - start_time} seconds")
        else:
            print("No matching frame detected within the timeout period.")

        # Capture ending screenshot
        screen_capture.save_screenshot("final_screenshot.png")
