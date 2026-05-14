import logging
import os
import tempfile
from datetime import datetime
from enum import Enum
from queue import Queue, Empty
from threading import Event, Thread
from time import sleep, time
from typing import Optional, Union, Callable, Generator

import cv2
import mss
import numpy as np
from PIL import Image
from PIL.Image import Transpose
from mss import tools
from mss.base import MSSBase
from mss.models import Monitor

from karta.core.utils.waitutil import wait_until, ConditionCallSpec

import queue
import threading
import time
from typing import Optional, Union

import mss
from mss import tools


def get_screen_area(monitor: int = 1) -> tuple[int, int, int, int]:
    with mss.mss as sct:
        monitor = sct.monitors[monitor]
        return monitor['left'], monitor['top'], monitor['width'], monitor['height']


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

    def has_frame_changed(self)->tuple[bool,...]:
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
            wait_result, image_change_time = wait_until(ConditionCallSpec(self.has_frame_changed), timeout, check_interval)
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
