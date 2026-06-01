import ast
import logging
import os
import tempfile
from datetime import datetime
from enum import Enum
from queue import Queue, Empty
from threading import Event, Thread
from time import sleep, time
from typing import Optional, Union, Callable, Generator, Any

import cv2
import mss
import numpy as np
from PIL import Image
from PIL.Image import Transpose
from mss import tools
from mss.base import MSSBase
from mss.models import Monitor

from karta.core.utils.waitutil import wait_until, ConditionCallSpec, ConditionWaitSpec, WaitResult

import time


def is_grayscale(pixel: tuple, tolerance: int = 0) -> bool:
    r, g, b = pixel[:3]  # Ignore Alpha channel

    if tolerance <= 0:
        return r == g and g == b

    return (max(r, g, b) - min(r, g, b)) <= tolerance


def get_diff_image(image1: Image.Image, image2: Image.Image, highlight_color: tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
    array1 = np.array(image1.convert('RGB'))
    array2 = np.array(image2.convert('RGB'))
    if array1.shape != array2.shape:
        raise ValueError("Images must be of same shape and channels.")
    difference_mask = np.all(array1 == array2, axis=-1)
    diffence_image = np.zeros_like(array1)
    diffence_image[difference_mask] = highlight_color
    return Image.fromarray(diffence_image)


class ImagePercentageMatchAlgorithm(Enum):
    EXACT = 1
    HISTOGRAM = 2
    RMS = 3


def generate_screenshot_file_name(filename_prefix=None) -> str:
    if filename_prefix is None:
        filename_prefix = ''
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{filename_prefix}_{timestamp}.png"


def reduce_colors(image: Image.Image, color_reduction_factor: int = 16) -> Image.Image:
    arr = np.array(image.convert('RGB'))
    arr = (arr // color_reduction_factor) * color_reduction_factor
    new_image = Image.fromarray(arr)
    return new_image


def get_image_match_percentage(image1: Image.Image, image2: Image.Image,
                               algorithm: ImagePercentageMatchAlgorithm = ImagePercentageMatchAlgorithm.EXACT,
                               use_color_reduction: bool = False, color_reduction_factor: int = 16) -> float:
    if image1.size != image2.size:
        raise ValueError("Image size must be of same size and channels.")

    if algorithm == ImagePercentageMatchAlgorithm.HISTOGRAM:
        hist1 = np.array(image1.histogram())
        hist2 = np.array(image2.histogram())

        if len(hist1) == len(hist2):
            error = np.sqrt(((hist1 - hist2) ** 2).mean())
            error = str(error)[:2]
            return 100.0 - float(error)
        else:
            return 0.0
    else:
        arr1 = np.array(image1.convert('RGB'))
        arr2 = np.array(image2.convert('RGB'))

        if use_color_reduction:
            arr1 = (arr1 // color_reduction_factor) * color_reduction_factor
            arr2 = (arr2 // color_reduction_factor) * color_reduction_factor

        if algorithm == ImagePercentageMatchAlgorithm.EXACT:
            exact_matches = np.all(arr1 == arr2, axis=-1)
            return 100.0 * np.sum(exact_matches) / exact_matches.size

        elif algorithm == ImagePercentageMatchAlgorithm.RMS:
            mse = float(np.mean((arr1 - arr2) ** 2))
            max_mse = 255 ** 2
            match_percentage = 100.0 - (max_mse / mse) * 100.0
            return max(0.0, min(100.0, match_percentage))
        else:
            raise ValueError(f"Algorithm {algorithm} is not supported.")


class ImageFrame:
    sharpen_kernal = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

    @classmethod
    def static_color_generator(cls, red: int, blue: int, green: int):
        while True:
            yield red, blue, green

    @classmethod
    def random_color_generator(cls, max_red: int, max_blue: int, max_green: int):
        while True:
            yield np.random.randint(0, max_red), np.random.randint(0, max_blue), np.random.randint(0, max_green)

    @classmethod
    def load_from_file(cls, filename: str) -> 'ImageFrame':
        image = Image.open(filename).convert('RGB')  # Normalize to 3-byte RGB
        image_data = np.array(image).tobytes()
        return cls(data=image_data, size=image.size, timestamp=time())

    @classmethod
    def load_frames_from_files(cls, filenames: list[str]) -> list['ImageFrame']:
        frames = []
        for index, filename in enumerate(filenames):
            frame = cls.load_from_file(filename)
            frame.index = index
            frames.append(frame)
        return frames

    @classmethod
    def create_image(cls, width: int, height: int,
                     color_generator: Generator[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]) -> 'ImageFrame':
        color_array = np.empty((height, width, 3), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                color_array[y, x] = next(color_generator)
        image_data = color_array.tobytes()
        return cls(data=image_data, size=(height, width), timestamp=time())

    def __init__(self, data: bytes, size: tuple[int, int], timestamp: float, index: int = 0, same_as_previous: bool = False):
        self.data = data
        self.size = size
        self.timestamp = timestamp if timestamp else time()
        self.index = index
        self.same_as_previous = False

    def __str__(self):
        return f"ImageFrame(index={self.index}, size={self.size}, timestamp={self.timestamp}, same_as_previous={self.same_as_previous})"

    def __eq__(self, other):
        return self.data == other.data

    def is_first_frame(self) -> bool:
        return self.index == 0

    def is_first_frame_or_frame_changed(self) -> bool:
        return (self.index == 0) or not self.same_as_previous

    def save_screenshot(self, filename: str) -> 'ImageFrame':
        if not self.data:
            raise ValueError("No image data present to save.")
        tools.to_png(self.data, self.size, output=filename)
        return self

    def save_screenshot_as(self, path: str = '.', filename_prefix: str = 'screenshot') -> str:
        if not self.data:
            raise ValueError("No image data present to save.")
        if not os.path.exists(path):
            os.makedirs(path)
        filename = generate_screenshot_file_name(filename_prefix)
        full_path = os.path.join(path, filename)
        tools.to_png(self.data, self.size, output=full_path)
        return full_path

    def to_pil_image(self) -> Image.Image:
        return Image.frombytes('RGB', self.size, self.data)

    def get_image_match_percentage(self, other_frame: 'ImageFrame', algorithm: ImagePercentageMatchAlgorithm = ImagePercentageMatchAlgorithm.EXACT,
                                   use_color_reduction: bool = False, color_reduction_factor: int = 16) -> float:
        return get_image_match_percentage(self.to_pil_image(), other_frame.to_pil_image(), algorithm, use_color_reduction, color_reduction_factor)

    def get_image_change_percentage(self, other_frame: 'ImageFrame', algorithm: ImagePercentageMatchAlgorithm = ImagePercentageMatchAlgorithm.EXACT,
                                    use_color_reduction: bool = False, color_reduction_factor: int = 16) -> float:
        return 100.0 - get_image_match_percentage(self.to_pil_image(), other_frame.to_pil_image(), algorithm, use_color_reduction, color_reduction_factor)

    def copy(self) -> 'ImageFrame':
        return ImageFrame(self.data, self.size, self.timestamp, self.index, self.same_as_previous)

    @staticmethod
    def crop_image(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
        return image.crop(box)

    def crop(self, box: tuple[int, int, int, int]) -> 'ImageFrame':
        pil_image = self.to_pil_image()
        cropped_image = pil_image.crop(box)
        self.data = np.array(cropped_image).tobytes()
        return self

    def rotate(self, angle: float) -> 'ImageFrame':
        pil_image = self.to_pil_image()
        rotated_image = pil_image.rotate(angle)
        self.data = np.array(rotated_image).tobytes()
        return self

    def rotate_clockwise(self) -> 'ImageFrame':
        return self.rotate(90)

    def rotate_counterclockwise(self) -> 'ImageFrame':
        return self.rotate(-90)

    def flip_left_right(self) -> 'ImageFrame':
        pil_image = self.to_pil_image()
        flipped_image = pil_image.transpose(Transpose.FLIP_LEFT_RIGHT)
        self.data = np.array(flipped_image).tobytes()
        return self

    def flip_top_bottom(self) -> 'ImageFrame':
        pil_image = self.to_pil_image()
        flippped_image = pil_image.transpose(Transpose.FLIP_TOP_BOTTOM)
        self.data = np.array(flippped_image).tobytes()
        return self

    def to_grayscale(self) -> 'ImageFrame':
        pil_image = self.to_pil_image()
        gray_image = pil_image.convert('L').convert('RGB')
        self.data = np.array(gray_image).tobytes()
        return self

    def sharpen(self) -> 'ImageFrame':
        pil_image = self.to_pil_image()
        sharpened_array = cv2.filter2D(np.array(pil_image), -1, self.sharpen_kernal)
        sharpened_image = Image.fromarray(sharpened_array, mode='RGB')
        self.data = sharpened_image.tobytes()
        return self

    def grayscale_and_sharpen(self) -> 'ImageFrame':
        pil_image = self.to_pil_image()
        gray_image = pil_image.convert('L').convert('RGB')
        sharpened_array = cv2.filter2D(np.array(pil_image), -1, self.sharpen_kernal)
        sharpened_image = Image.fromarray(sharpened_array, mode='RGB')
        self.data = sharpened_image.tobytes()
        return self

    def is_black_exact(self) -> bool:
        pil_image = self.to_pil_image()
        array = np.array(pil_image.convert('RGB'))
        return np.all(array == 0)

    def get_black_percentage(self) -> float:
        pil_image = self.to_pil_image()
        array = np.array(pil_image.convert('RGB'))
        black_pixesl = float(np.sum(np.all(array == 0, axis=-1)))
        total_pixels = array.shape[0] * array.shape[1]
        black_percentage = black_pixesl / total_pixels * 100.0
        return black_percentage

    def is_black(self, percentage: float = 100.0) -> bool:
        if percentage >= 100.0:
            return self.is_black_exact()

        black_percentage = self.get_black_percentage()
        return black_percentage >= percentage

    def is_blank(self, percentage: float = 100.0) -> bool:
        pil_image = self.to_pil_image()
        array = np.array(pil_image.convert('RGB'))

        pixels = array.reshape(-1, 3)
        # Find the color which is predominant in the image
        unique_pixels, pixel_counts = np.unique(pixels, axis=0, return_counts=True)

        # Predominant pixel count is the max
        predominant_pixel_count = pixel_counts.max()
        total_pixels = array.shape[0] * array.shape[1]
        blank_percentage = predominant_pixel_count / total_pixels * 100.0
        return blank_percentage >= percentage

    def filter_image(self, filter_predicate: Callable, replaced_color: tuple[int, int, int] = (0, 0, 0), *predicate_args, **predicate_kwargs) -> 'ImageFrame':
        pil_image = self.to_pil_image()
        arr = np.array(pil_image.convert('RGB'))
        mask = np.apply_along_axis(filter_predicate, 2, arr, *predicate_args, **predicate_kwargs)
        arr[mask] = replaced_color
        self.data = arr.tobytes()
        return self

    def remove_grayscale_pixels(self, replaced_color: tuple[int, int, int] = (0, 0, 0), tolerance: int = 5) -> 'ImageFrame':
        return self.filter_image(is_grayscale, replaced_color, tolerance)

    def get_difference_image(self, compared_frame: 'ImageFrame', highlight_color: tuple[int, int, int] = (255, 0, 0)) -> "ImageFrame":
        pil_image1 = self.to_pil_image().convert('RGB')
        pil_image2 = self.to_pil_image().convert('RGB')
        arr1 = np.array(pil_image1)
        arr2 = np.array(pil_image2)
        difference_mask = np.any(arr1 != arr2, axis=-1)
        difference_image = np.zeros_like(arr1)
        difference_image[difference_mask] = highlight_color
        self.data = difference_image.tobytes()
        return self

    def reduce_colors(self, reduction_factor: int = 16) -> 'ImageFrame':
        pil_image = self.to_pil_image()
        arr = np.array(pil_image.convert('RGB'))
        arr = (arr // reduction_factor) * reduction_factor
        new_image = Image.fromarray(arr)
        self.data = new_image.tobytes()
        return self

    def filter_colors(self, filter_colors: list[tuple[int, int, int]], filter_out: bool = False) -> 'ImageFrame':
        if filter_out:
            predicate_function = lambda color: color in filter_colors
        else:
            predicate_function = lambda color: color not in filter_colors
        return self.filter_image(predicate_function)


class Position:
    @staticmethod
    def get_screen_cordinates(monitor: int = 1) -> tuple[int, int, int, int]:
        with mss.mss() as sct:
            monitor = sct.monitors[monitor]
            return monitor['left'], monitor['top'], monitor['width'], monitor['height']

    @staticmethod
    def get_screen_area(monitor: int = 1) -> tuple[int, int]:
        screen_cordinates = Position.get_screen_cordinates(monitor)
        return screen_cordinates[2], screen_cordinates[3]

    DEFAULT_SCREEN_CORDINATES: tuple[int, int, int, int] = get_screen_cordinates()
    DEFAULT_SCREEN_AREA: tuple[int, int] = DEFAULT_SCREEN_CORDINATES[2], DEFAULT_SCREEN_CORDINATES[3]

    DEFAULT_END_POSITION: tuple[int, int] = DEFAULT_SCREEN_CORDINATES[0] + DEFAULT_SCREEN_CORDINATES[2], \
                                            DEFAULT_SCREEN_CORDINATES[1] + DEFAULT_SCREEN_CORDINATES[3]
    DEFAULT_MID_POSITION: tuple[int, int] = DEFAULT_SCREEN_CORDINATES[0] + DEFAULT_SCREEN_CORDINATES[2] // 2, \
                                            DEFAULT_SCREEN_CORDINATES[1] + DEFAULT_SCREEN_CORDINATES[3] // 2

    POSITION_MAP_DICT: dict[str, int] = {
        'left': DEFAULT_SCREEN_CORDINATES[0],
        'top': DEFAULT_SCREEN_CORDINATES[1],
        'widht': DEFAULT_SCREEN_CORDINATES[2],
        'height': DEFAULT_SCREEN_CORDINATES[3],
        'right': DEFAULT_END_POSITION[0],
        'bottom': DEFAULT_END_POSITION[1],
        'center_x': DEFAULT_MID_POSITION[0],
        'center_y': DEFAULT_MID_POSITION[1],
        'mid_x': DEFAULT_MID_POSITION[0],
        'mid_y': DEFAULT_MID_POSITION[1],
    }

    @staticmethod
    def from_dict(position_dict: dict) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = Position.DEFAULT_SCREEN_CORDINATES

        if 'left' in position_dict:
            x1 = position_dict['left']
        if 'top' in position_dict:
            y1 = position_dict['top']
        if 'right' in position_dict:
            x2 = position_dict['right']
        if 'bottom' in position_dict:
            y2 = position_dict['bottom']
        if 'width' in position_dict:
            x2 = x1 + position_dict['width']
        if 'height' in position_dict:
            y2 = y1 + position_dict['height']
        return x1, y1, x2, y2

    @staticmethod
    def normalize(position_raw: Union[tuple, dict]) -> tuple[int, int, int, int]:
        screen_coordinates = Position.DEFAULT_SCREEN_CORDINATES

        if isinstance(position_raw, dict):
            position_raw = Position.from_dict(position_raw)

        pos_list: list[int] = [0, 0, 0, 0]

        for idx in range(4):
            if isinstance(position_raw[idx], int) or isinstance(position_raw[idx], float):
                if position_raw[idx] < 0:
                    max_coordinate_pos = screen_coordinates[2 + idx % 2]
                    pos_list[idx] = max_coordinate_pos + position_raw[idx]
                else:
                    pos_list[idx] = position_raw[idx]
            elif isinstance(position_raw[idx], str):

                # Replace string position with corresponding screen coordinate
                replaced_text = str(position_raw[idx])
                for replace_str, replace_value in Position.POSITION_MAP_DICT.items():
                    if replace_str in replaced_text:
                        replaced_text = replaced_text.replace(replace_str, str(replace_value))
                pos_list[idx] = ast.literal_eval(replaced_text)
            else:
                pos_list[idx] = screen_coordinates[idx]

        return pos_list[0], pos_list[1], pos_list[2], pos_list[3]


class ScreenGrabber:
    MINIMUM_SLEEP_TIME: float = 0.005
    DEFAULT_CHECK_INTERVAL: float = 0.033
    DEFAULT_MAX_TIMEOUT: float = 60

    def __init__(self,
                 check_interval: float = DEFAULT_CHECK_INTERVAL,
                 max_timeout: float = DEFAULT_MAX_TIMEOUT,
                 monitor: Optional[int] = None,
                 screen_area: Union[dict, tuple] = None):
        self.capture_thread = None
        self.grabbing = False
        self.max_timeout = max_timeout if max_timeout else self.DEFAULT_MAX_TIMEOUT
        self.grab_start_time: Optional[float] = time()
        self.grab_event: Event = Event()

        if check_interval <= self.MINIMUM_SLEEP_TIME:
            check_interval = self.DEFAULT_CHECK_INTERVAL

        self.frame_queue = Queue()

        self.wait_time_per_frame: float = check_interval
        self.first_frame = None
        self.previous_matching_frame = None
        self.frame_index = 0

        with mss.mss() as sct:
            if monitor and screen_area:
                raise ValueError("Specify either monitor or screen_area, not both.")

            if monitor:
                if not isinstance(monitor, int):
                    raise ValueError("Monitor must be an integer representing a monitor number.")
                self.monitor: Monitor = sct.monitors[monitor]
            elif screen_area:
                if not isinstance(screen_area, (tuple, dict)):
                    raise ValueError("screen_area must be a dict or tuple specifying the area to capture.")
                self.screen_area: tuple[int, int, int, int] = Position.normalize(screen_area)
            else:
                self.monitor = sct.monitors[1]

    def get_all_frames(self):
        frames = []
        while True:
            try:
                frames.append(self.frame_queue.get_nowait())
            except Empty:
                if self.grabbing:
                    self.grab_event.clear()
                break
        return frames

    def start(self, max_timeout: float = DEFAULT_MAX_TIMEOUT):
        self.max_timeout = max_timeout if max_timeout and max_timeout > 0 else self.DEFAULT_MAX_TIMEOUT

        if self.grabbing and self.capture_thread and self.capture_thread.is_alive:
            return  # Already capturing

        self.grabbing = True
        self.capture_thread = Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()

    def stop(self):
        if self.capture_thread:
            self.grabbing = False
            if self.capture_thread.is_alive():
                self.capture_thread.join()
            self.capture_thread = None
        else:
            self.grabbing = False

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
        self.stop()

    def grab(self):
        param = self.monitor if hasattr(self, 'monitor') else self.screen_area
        with mss.mss() as sct:
            return sct.grab(param)

    def _capture_frame(self, sct: MSSBase, grab_param):
        img = sct.grab(grab_param)
        frame = ImageFrame(data=img.rgb, size=img.size, timestamp=time(), index=self.frame_index, same_as_previous=False)
        self.frame_index += 1

        if frame.is_first_frame():
            frame.same_as_previous = True
            self.first_frame = frame
            self.previous_matching_frame = frame
        else:
            if frame.data == self.previous_matching_frame.data:
                frame.data = self.previous_matching_frame.data
                frame.same_as_previous = True
            else:
                frame.same_as_previous = False
                self.previous_matching_frame = frame
        return frame

    def grab_frame(self):
        param = self.monitor if hasattr(self, 'monitor') else self.screen_area
        with mss.mss() as sct:
            return self._capture_frame(sct, param)

    def _capture_frames(self):
        self.grabbing = True
        self.grab_start_time = time()

        grab_param = self.monitor if hasattr(self, 'monitor') else self.screen_area
        self.frame_index = 0
        with mss.mss() as sct:
            while self.grabbing and ((time() - self.grab_start_time) <= self.max_timeout):
                start_time = time()
                frame = self._capture_frame(sct, grab_param)

                self.frame_queue.put(frame)
                self.grab_event.set()

                elapsed_time = time() - start_time
                time_to_wait = max(0.0, self.wait_time_per_frame - elapsed_time)
                if time_to_wait > self.MINIMUM_SLEEP_TIME:
                    sleep(time_to_wait)

        # Grabbing stopped
        self.frame_index = 0
        self.grabbing = False


class ImageUtility:

    def __init__(self,
                 check_interval: float = ScreenGrabber.MINIMUM_SLEEP_TIME,
                 max_timeout: float = ScreenGrabber.DEFAULT_MAX_TIMEOUT,
                 monitor: Optional[int] = None,
                 screen_area: Optional[Union[tuple, dict]] = None,
                 use_grab_thread: bool = False,
                 ):
        self.check_interval = check_interval if check_interval else ScreenGrabber.DEFAULT_CHECK_INTERVAL
        self.max_timeout = max_timeout if max_timeout else ScreenGrabber.DEFAULT_MAX_TIMEOUT
        self.use_grab_thread = use_grab_thread
        self.monitor: Optional[int] = monitor
        self.screen_area: Optional[Union[tuple, dict]] = screen_area

        self.screen_grabber = ScreenGrabber(check_interval=self.check_interval, max_timeout=self.max_timeout, monitor=self.monitor,
                                            screen_area=self.screen_area)

    def __enter__(self):
        return self

    def stop(self):
        if self.screen_grabber:
            self.screen_grabber.stop()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def grab_frame(self) -> ImageFrame:
        return self.screen_grabber.grab_frame()

    def save_screenshot(self, filename: str):
        self.grab_frame().save_screenshot(filename)

    def wait_until(self, condition: Callable, timeout: float, *condition_args, **condition_kwargs) -> tuple[float, bool, ImageFrame, *tuple[Any, ...]]:
        if self.use_grab_thread:
            self.screen_grabber.start(max_timeout=timeout)

        try:
            start_time = time()
            wait_condition_spec = ConditionWaitSpec(ConditionCallSpec(condition, *condition_args, **condition_kwargs), timeout, self.check_interval,
                                                    self.screen_grabber.grab_event if self.use_grab_thread else None)
            wait_result = wait_condition_spec.wait_for()
            result = wait_result.result
            frame = wait_result.other_return_args[0] if len(wait_result.other_return_args) >= 1 else None
            other_return_args = wait_result.other_return_args[1:] if len(wait_result.other_return_args) >= 2 else tuple()

            # If there are still frames to be processed, check for condition again
            if not result and not self.screen_grabber.frame_queue.empty():
                result, frame, *other_return_args = condition(*condition_args, **condition_kwargs)

            if not frame:
                frame = self.screen_grabber.grab_frame()

            return frame.timestamp - start_time, result, frame, *other_return_args
        finally:
            if self.use_grab_thread:
                self.screen_grabber.stop()

    def _validate_screen_grab(self):
        if self.use_grab_thread:
            if not self.screen_grabber or not self.screen_grabber.grabbing:
                raise Exception("Screen grabber is not initialized or is not running")

    def has_frame_changed(self) -> tuple[bool, Optional[ImageFrame]]:
        self._validate_screen_grab()

        frame = None
        while True:
            try:
                frame = self.screen_grabber.frame_queue.get_nowait() if self.use_grab_thread else self.grab_frame()

                if not frame.same_as_previous:
                    return True, frame
                if not self.use_grab_thread:
                    return False, frame
                # Else pick another frame from queue
            except Empty:
                if self.use_grab_thread:
                    self.screen_grabber.grab_event.clear()
                return False, frame

    def wait_until_frame_changes(self, timeout: float) -> tuple[float, bool, ImageFrame]:
        time_taken, result, frame, *_ = self.wait_until(self.has_frame_changed, timeout)
        return time_taken, result, frame

    def is_frame_matching_reference(self, rreference_frame: ImageFrame) -> tuple[bool, Optional[ImageFrame]]:
        self._validate_screen_grab()

        if not rreference_frame:
            raise Exception("Reference frame cannot be empty")

        frame = None
        while True:
            try:
                frame = self.screen_grabber.frame_queue.get_nowait() if self.use_grab_thread else self.grab_frame()
                if frame.is_first_frame_or_frame_changed() and (frame.data == rreference_frame.data):
                    return True, frame
                if not self.use_grab_thread:
                    return False, frame
            except Empty:
                if self.use_grab_thread:
                    self.screen_grabber.grab_event.clear()
                return False, frame

    def wait_for_reference_image(self, timeout: float, reference_frame: ImageFrame) -> tuple[float, bool, ImageFrame]:
        time_taken, result, frame, *_ = self.wait_until(self.is_frame_matching_reference, timeout, reference_frame)
        return time_taken, result, frame

    def is_frame_matching_any_reference_image(self, refereence_frames: list[ImageFrame]) -> tuple[bool, Optional[ImageFrame], Optional[int]]:
        """
        Checks if the current screen matches any of the reference frames
        :param refereence_frames:
        :return:
            A tuple of (is_matching: bool, matching_frame: Optional[ImageFrame], matching_frame_index: Optional[int])
        """
        self._validate_screen_grab()

        if not refereence_frames:
            raise Exception("Reference frame cannot be empty")

        frame = None
        while True:
            try:
                frame = self.screen_grabber.frame_queue.get_nowait() if self.use_grab_thread else self.grab_frame()

                if frame.is_first_frame_or_frame_changed():
                    for idx, refereence_frame in enumerate(refereence_frames):
                        if frame.data == refereence_frame.data:
                            return True, frame, idx

                if not self.use_grab_thread:
                    return False, frame, -1

            except Empty:
                if self.use_grab_thread:
                    self.screen_grabber.grab_event.clear()
                return False, frame, -1

    def wait_for_any_reference_image(self, timeout: float, reference_frames: list[ImageFrame]) -> tuple[float, bool, ImageFrame, Optional[int]]:
        time_taken, result, frame, *rest = self.wait_until(self.is_frame_matching_any_reference_image, timeout, reference_frames)
        matching_frame_index = rest[0] if rest else -1
        return time_taken, result, frame, matching_frame_index

    def is_frame_not_matching_reference(self, reference_frame: ImageFrame) -> tuple[bool, Optional[ImageFrame]]:
        self._validate_screen_grab()
        if not reference_frame:
            raise Exception("Reference frame cannot be empty")
        frame = None
        while True:
            try:
                frame = self.screen_grabber.frame_queue.get_nowait() if self.use_grab_thread else self.grab_frame()
                if frame.is_first_frame_or_frame_changed() and (frame.data != reference_frame.data):
                    return True, frame
                if not self.use_grab_thread:
                    return False, frame
            except Empty:
                if self.use_grab_thread:
                    self.screen_grabber.grab_event.clear()
                return False, frame

    def wait_for_reference_image_to_change(self, timeout: float, reference_frame: ImageFrame) -> tuple[float, bool, ImageFrame]:
        time_taken, result, frame, *_ = self.wait_until(self.is_frame_not_matching_reference, timeout, reference_frame)
        return time_taken, result, frame

    def is_frame_not_matching_reference_and_non_black(self, reference_frame: ImageFrame) -> tuple[bool, Optional[ImageFrame]]:
        self._validate_screen_grab()
        if not reference_frame:
            raise Exception("Reference frame cannot be empty")
        frame = None
        while True:
            try:
                frame = self.screen_grabber.frame_queue.get_nowait() if self.use_grab_thread else self.grab_frame()
                if frame.is_first_frame_or_frame_changed() and (frame.data != reference_frame.data) and not frame.is_black_exact():
                    return True, frame
                if not self.use_grab_thread:
                    return False, frame
            except Empty:
                if self.use_grab_thread:
                    self.screen_grabber.grab_event.clear()
                return False, frame

    def wait_for_referenence_image_to_change_and_non_black(self, timeout: float, reference_frame: ImageFrame) -> tuple[float, bool, ImageFrame]:
        time_taken, result, frame, *_ = self.wait_until(self.is_frame_not_matching_reference_and_non_black, timeout, reference_frame)
        return time_taken, result, frame

    def is_frame_matching_reference_percentange(self, reference_frame: ImageFrame,
                                                match_threshold: float = 5.0,
                                                algorithm: ImagePercentageMatchAlgorithm = ImagePercentageMatchAlgorithm.EXACT,
                                                use_color_reduction: bool = False,
                                                color_reduction_factor: int = 16) -> tuple[bool, Optional[ImageFrame], float]:

        self._validate_screen_grab()

        if not reference_frame:
            raise Exception("Reference frame cannot be empty")

        frame = None
        match_percentage = -1
        while True:
            try:
                frame = self.screen_grabber.frame_queue.get_nowait() if self.use_grab_thread else self.grab_frame()
                if frame.is_first_frame_or_frame_changed():
                    match_percentage = reference_frame.get_image_match_percentage(frame, algorithm, use_color_reduction, color_reduction_factor)
                    if match_percentage >= match_threshold:
                        return True, frame, match_percentage
                if not self.use_grab_thread:
                    return False, frame, match_percentage
                    # Else pick another frame
            except Empty:
                if self.use_grab_thread:
                    self.screen_grabber.grab_event.clear()
                return False, frame, match_percentage

    def wait_for_reference_image_percentage(self, timeout: float, reference_frame: ImageFrame,
                                            match_threshold: float = 99.0,
                                            algorithm: ImagePercentageMatchAlgorithm = ImagePercentageMatchAlgorithm.EXACT,
                                            use_color_reduction: bool = False,
                                            color_reduction_factor: int = 16) -> tuple[float, bool, ImageFrame, float]:
        if use_color_reduction:
            reference_frame = reference_frame.reduce_colors(color_reduction_factor)

        time_taken, result, frame, *rest = self.wait_until(self.is_frame_matching_reference_percentange, timeout
                                                           , reference_frame,
                                                           match_threshold,
                                                           algorithm,
                                                           use_color_reduction,
                                                           color_reduction_factor)
        match_percent = rest[0] if len(rest) > 0 else -1

        if match_percent < 0:
            match_percent = reference_frame.get_image_match_percentage(frame, algorithm, use_color_reduction, color_reduction_factor)

        return time_taken, result, frame, match_percent

    def has_frame_changed_percentage(self, reference_frame: ImageFrame,
                                     change_threshold: float = 5.0,
                                     algorithm: ImagePercentageMatchAlgorithm = ImagePercentageMatchAlgorithm.EXACT,
                                     use_color_reduction: bool = False,
                                     color_reduction_factor: int = 16
                                     ) -> tuple[bool, Optional[ImageFrame], float]:

        self._validate_screen_grab()

        frame = None
        change_percentage = -1
        while True:
            try:
                frame = self.screen_grabber.frame_queue.get_nowait() if self.use_grab_thread else self.grab_frame()
                if frame.is_first_frame_or_frame_changed():
                    change_percentage = reference_frame.get_image_change_percentage(frame, algorithm, use_color_reduction, color_reduction_factor)
                    if change_percentage >= change_threshold:
                        return True, frame, change_percentage
                if not self.use_grab_thread:
                    return False, frame, change_percentage
                    # Else pick another frame
            except Empty:
                if self.use_grab_thread:
                    self.screen_grabber.grab_event.clear()
                return False, frame, change_percentage

    def wait_for_frame_change_percentage(self, timeout: float, reference_frame: ImageFrame,
                                         change_threshold: float = 5.0,
                                         algorithm: ImagePercentageMatchAlgorithm = ImagePercentageMatchAlgorithm.EXACT,
                                         use_color_reduction: bool = False,
                                         color_reduction_factor: int = 16) -> tuple[float, bool, ImageFrame, float]:
        if use_color_reduction:
            reference_frame = reference_frame.reduce_colors(color_reduction_factor)
        time_taken, result, frame, *rest = self.wait_until(self.has_frame_changed_percentage, timeout,
                                                           reference_frame,
                                                           change_threshold,
                                                           algorithm,
                                                           use_color_reduction,
                                                           color_reduction_factor)
        change_percent = rest[0] if len(rest) > 0 else -1
        if change_percent < 0:
            change_percent = reference_frame.get_image_change_percentage(frame, algorithm, use_color_reduction, color_reduction_factor)
        return time_taken, result, frame, change_percent

    def is_referece_image_presnt_inside(self, reference_frame: ImageFrame, match_threshold: float = 99.0) -> tuple[
        bool, Optional[ImageFrame], float, tuple[int, int]]:
        self._validate_screen_grab()

        if not reference_frame:
            raise Exception('Reference frame is empty')

        ref_image = np.array(reference_frame.to_pil_image())
        last_result: tuple[Optional[ImageFrame], float, tuple[int, int]] = (None, 0.0, (-1, -1))
        while True:
            try:
                frame = self.screen_grabber.frame_queue.get_nowait() if self.use_grab_thread else self.grab_frame()

                if frame.is_first_frame_or_frame_changed():
                    frame_image = np.array(frame.to_pil_image())
                    result = cv2.matchTemplate(frame_image, ref_image, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    last_result = frame, max_val * 100, (max_loc[0], max_loc[1])
                    if round(max_val * 100) >= match_threshold:
                        return True, last_result[0], last_result[1], last_result[2]

                if not self.use_grab_thread:
                    return False, last_result[0], last_result[1], last_result[2]

            except Empty:
                if self.use_grab_thread:
                    self.screen_grabber.grab_event.clear()
                return False, last_result[0], last_result[1], last_result[2]

    def wait_for_reference_image_inside(self, timeout: float, reference_frame: ImageFrame, threshold: float = 99.0) -> tuple[
        float, bool, ImageFrame, float, tuple[int, int]]:
        time_taken, result, frame, *rest = self.wait_until(self.is_referece_image_presnt_inside, timeout, reference_frame, threshold)

        # TODO: Check return value for failure cases
        match_value, match_location = rest if isinstance(rest, tuple) and len(rest) == 2 else (0, 0, (-1, -1))
        return time_taken, result, frame, match_value, match_location

    def capture_unique_frames_in_loop_until_first(self) -> list[ImageFrame]:
        unique_frames = []
        self.screen_grabber.start()
        try:
            first_frame: Optional[ImageFrame] = None

            while True:
                frame = self.screen_grabber.frame_queue.get()
                if not first_frame:
                    first_frame = frame
                    unique_frames.append(frame)
                else:
                    if frame.data == first_frame.data:
                        break
                    else:
                        unique_frames.append(frame)
        finally:
            self.screen_grabber.stop()
        return unique_frames

    def wait_for_all_frames(self, timeout: float, frame_list: list[ImageFrame]) -> tuple[float, bool, ImageFrame]:
        captured_frame = None
        current_time = time()
        elaspsed_time = 0
        matched_frame_count = 0
        wait_time = timeout

        self.screen_grabber.start()
        try:
            while len(frame_list) > 0:
                wait_result = ConditionWaitSpec(ConditionCallSpec(self.is_frame_matching_any_reference_image, frame_list), timeout - elaspsed_time,
                                                self.check_interval, self.screen_grabber.grab_event if self.use_grab_thread else None).wait_for()
                captured_frame = wait_result.other_return_args[0] if len(wait_result.other_return_args) >= 1 else self.grab_frame()
                index = wait_result.other_return_args[1] if len(wait_result.other_return_args) >= 2 else -1
                wait_time = wait_result.wait_time

                if not wait_result.result:
                    return wait_time, False, captured_frame

                elaspsed_time = time() - current_time

                if elaspsed_time >= timeout:
                    return wait_time, False, captured_frame

                matched_frame_count += 1

                if index is not None and (0 <= index < len(frame_list)):
                    frame_list.pop(index)
        finally:
            self.screen_grabber.stop()

        if not captured_frame:
            captured_frame = self.grab_frame()

        return wait_time, True, captured_frame


class ScreenCapture:
    @staticmethod
    def capture(screen_area=None, monitor=None) -> ImageFrame:
        with ScreenGrabber(screen_area=screen_area, monitor=monitor) as screen_grabber:
            return screen_grabber.grab_frame()

    def __init__(self, screen_area=None, monitor=None, frame: Optional[ImageFrame] = None):
        self.screen_area = screen_area
        self.monitor = monitor

        if not frame:
            frame = ScreenCapture.capture()

        self.size = frame.size
        self.index = frame.index
        self.timestamp = frame.timestamp
        self.same_as_previous = frame.same_as_previous

        # Create temporaty file to save sceenshot
        fd, self.temp_file = tempfile.mkstemp(prefix="screencapture_", suffix=".png")
        os.close(fd)

        # Save screen data to the temporary file created
        frame.save_screenshot(self.temp_file)

    def clean(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def __del__(self):
        self.clean()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean()

    def get_frame(self) -> ImageFrame:
        # Load image from temp time
        frame = ImageFrame.load_from_file(self.temp_file)
        frame.size = self.size
        frame.index = self.index
        frame.timestamp = self.timestamp
        frame.same_as_previous = self.same_as_previous
        return frame
