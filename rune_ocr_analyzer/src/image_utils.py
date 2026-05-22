import numpy as np
import cv2
from PIL import ImageGrab, Image
from math import hypot
from typing import List, Tuple, Optional

from src.constants import DEFAULT_CONFIDENCE

template_cache = {}


def load_template(path: str) -> np.ndarray:
    if path not in template_cache:
        template_cache[path] = cv2.cvtColor(
            np.array(Image.open(path)), cv2.COLOR_RGB2BGR
        )
    return template_cache[path]


def take_screenshot(region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
    return cv2.cvtColor(np.array(ImageGrab.grab(bbox=region)), cv2.COLOR_RGB2BGR)


def find_image_position(
    screen: np.ndarray,
    template: np.ndarray,
    confidence: float = DEFAULT_CONFIDENCE,
) -> List[Tuple[int, int]]:
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    return list(zip(*np.where(result >= confidence)[::-1]))


def filter_close_matches(
    matches: List[Tuple[int, int]],
    threshold: float = 10.0,
) -> List[Tuple[int, int]]:
    out = []
    for x1, y1 in matches:
        if all(hypot(x1 - x2, y1 - y2) > threshold for (x2, y2) in out):
            out.append((x1, y1))
    return out


def is_color_similar(
    template: np.ndarray,
    matched: np.ndarray,
    sat_thresh: float = 30.0,
    val_thresh: float = 40.0,
) -> bool:
    thsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
    mhsv = cv2.cvtColor(matched, cv2.COLOR_BGR2HSV)
    if thsv.shape != mhsv.shape:
        mhsv = cv2.resize(mhsv, (thsv.shape[1], thsv.shape[0]))
    _, s1, v1 = cv2.mean(thsv)[:3]
    _, s2, v2 = cv2.mean(mhsv)[:3]
    return abs(s1 - s2) < sat_thresh and abs(v1 - v2) < val_thresh


def has_red_pixel(
    region: Tuple[int, int, int, int], red_threshold=180, diff_threshold=80
) -> bool:
    x, y, w, h = region
    left, top, right, bottom = x, y, x + w, y + h

    if right <= left or bottom <= top:
        raise ValueError(f"Invalid region dimensions: {region}")

    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    pixels = np.array(screenshot)

    red, green, blue = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
    red_enough = red > red_threshold
    red_dominant = (red - green > diff_threshold) & (red - blue > diff_threshold)

    return np.any(red_enough & red_dominant)
