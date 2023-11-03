import calendar
import hashlib
import os
from datetime import datetime
from typing import Tuple


def get_hash(filename: str) -> str:
    hash_md5 = hashlib.md5()

    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def get_static_hash() -> str:
    hashes = []
    styles_dir = os.path.join(os.path.dirname(__file__), "..", "..", "web", "styles")
    js_dir = os.path.join(os.path.dirname(__file__), "..", "..", "web", "js")

    for filename in os.listdir(styles_dir):
        hashes.append(get_hash(os.path.join(styles_dir, filename)))

    for filename in os.listdir(js_dir):
        hashes.append(get_hash(os.path.join(js_dir, filename)))

    statis_hash = "_".join(hashes)
    hash_md5 = hashlib.md5()
    hash_md5.update(statis_hash.encode("utf-8"))

    return hash_md5.hexdigest()


def get_calendar() -> Tuple[int, int]:
    today = datetime.now()
    start_weekday, num_days = calendar.monthrange(today.year, today.month)
    end_weekday = datetime(today.year, today.month, num_days).weekday()

    return start_weekday, end_weekday
