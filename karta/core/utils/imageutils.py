import queue
import threading
import time
from typing import Optional, Union

import mss
from mss import tools

from karta.core.utils.waitutil import wait_until


class ImageFrame:
    def __init__(self, data, timestamp: Optional[float] = None, index: Optional[int] = None,
                 same_as_previous: bool = False):
        if not timestamp:
            timestamp = time.time()
        if not index:
            index = 0

        self.index = index
        self.data = data
        self.timestamp = timestamp
        self.same_as_previous = False

    def __str__(self):
        return f"ImageFrame(index={self.index}, timestamp={self.timestamp}, same_as_previous={self.same_as_previous})"

    def __eq__(self, other):
        return self.data == other.data


class ScreenCapture:

    def __init__(self, frame_rate: Optional[int] = None, monitor: Optional[int] = None,
                 screen_area: Optional[Union[dict[str, int], tuple[int, int, int, int]]] = None):
        self.capture_thread = None
        self.capturing = False
        self.frame_queue = queue.Queue()

        self.first_frame = None
        self.previous_matching_frame = None

        if frame_rate:
            if frame_rate <= 0:
                raise ValueError("Frame rate must be a positive integer.")
            self.frame_rate = frame_rate
        else:
            self.frame_rate = 30

        self.wait_time_per_frame = 1.0 / self.frame_rate

        with mss.mss() as sct:
            if monitor and screen_area:
                raise ValueError("Specify either monitor or screen_area, not both.")

            if monitor:
                self.monitor = sct.monitors[monitor]
            elif screen_area:
                if not isinstance(screen_area, (tuple, dict)):
                    raise ValueError("screen_area must be a dict or tuple specifying the area to capture.")
                self.screen_area = screen_area
            else:
                self.monitor = sct.monitors[1]

    def start_capture(self):
        if self.capturing and self.capture_thread.is_alive:
            return  # Already capturing

        self.capturing = True
        self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()

    def stop_capture(self):
        if self.capture_thread:
            self.capturing = False
            if self.capture_thread.is_alive():
                self.capture_thread.join()
            self.capture_thread = None
        else:
            self.capturing = False

        # Clear the frame queue
        if self.frame_queue:
            self.frame_queue.queue.clear()

        if self.first_frame:
            self.first_frame = None

        if self.previous_matching_frame:
            self.previous_matching_frame = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_capture()

    def capture_frame(self):
        capture_param = self.monitor if hasattr(self, 'monitor') else self.screen_area
        with mss.mss() as sct:
            return sct.grab(capture_param)

    def save_screenshot(self, filepath: str):
        screenshot = self.capture_frame()
        tools.to_png(screenshot.rgb, screenshot.size, output=filepath)

    def _capture_frames(self):
        self.capturing = True
        capture_param = self.monitor if hasattr(self, 'monitor') else self.screen_area
        frame_index = 0
        with mss.mss() as sct:
            while self.capturing:
                start_time = time.time()
                image = sct.grab(capture_param)
                frame = ImageFrame(data=image.rgb, timestamp=time.time(), index=frame_index)
                frame_index += 1

                if self.first_frame is None:
                    frame.same_as_previous = True
                    self.first_frame = frame
                    self.previous_matching_frame = frame
                else:
                    if frame == self.previous_matching_frame:
                        # Use data from previous matching frame to save memory
                        frame.data = self.previous_matching_frame.data
                        frame.same_as_previous = True
                    else:
                        frame.same_as_previous = False
                        self.previous_matching_frame = frame

                self.frame_queue.put(frame)

                elapsed_time = time.time() - start_time
                sleep_time = max(0.0, self.wait_time_per_frame - elapsed_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

    def has_frame_changed(self):
        if not self.capturing:
            raise RuntimeError("Screen capture is not running. Call start_capture() first.")

        while True:
            try:
                frame = self.frame_queue.get_nowait()
                if not frame.same_as_previous:
                    return True, frame.timestamp
            except queue.Empty:
                return False, time.time()

    def wait_until_frame_changes(self, timeout: float, check_interval: float = 0.1) -> tuple:
        if not check_interval or check_interval <= 0:
            check_interval = 0.1

        self.start_capture()

        try:
            wait_result, image_change_time = wait_until(self.has_frame_changed, timeout, check_interval)
            if not image_change_time:
                image_change_time = time.time()
            return wait_result, image_change_time
        finally:
            self.stop_capture()

    def is_frame_matching(self, image_rgb_data: bytes):
        if not self.capturing:
            raise RuntimeError("Screen capture is not running. Call start_capture() first.")

        while True:
            try:
                frame = self.frame_queue.get_nowait()
                if frame.data == image_rgb_data:
                    return True, frame.timestamp
            except queue.Empty:
                return False, time.time()

    def wait_until_frame_matches(self, image_rgb_data: bytes, timeout: float, check_interval: float = 0.1) -> tuple:
        if not check_interval or check_interval <= 0:
            check_interval = 0.1

        self.start_capture()
        try:
            wait_result, image_appear_time = wait_until(self.is_frame_matching, timeout, check_interval, image_rgb_data)
            if not image_appear_time:
                image_appear_time = time.time()
            return wait_result, image_appear_time
        finally:
            self.start_capture()
