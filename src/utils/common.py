import calendar
import hashlib
import os
import re
import shutil
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import cv2
from fastapi import UploadFile

from src import constants
from src.database import database


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
        path = os.path.join(styles_dir, filename)

        if os.path.isdir(path):
            for sub_filename in os.listdir(path):
                hashes.append(get_hash(os.path.join(path, sub_filename)))
        else:
            hashes.append(get_hash(path))

    for filename in os.listdir(js_dir):
        path = os.path.join(js_dir, filename)

        if os.path.isdir(path):
            for sub_filename in os.listdir(path):
                hashes.append(get_hash(os.path.join(path, sub_filename)))
        else:
            hashes.append(get_hash(path))

    statis_hash = "_".join(hashes)
    hash_md5 = hashlib.md5()
    hash_md5.update(statis_hash.encode("utf-8"))

    return hash_md5.hexdigest()


def crop_image(path: str, x: float, y: float, size: float) -> None:
    image = cv2.imread(path)
    height, width = image.shape[:2]
    size = int(size * min(height, width))
    x = int(x * min(height, width))
    y = int(y * min(height, width))

    image = image[y:y + size, x:x + size]
    image = cv2.resize(image, (constants.CROP_IMAGE_SIZE, constants.CROP_IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, image)


def preview_image(original_path: str, preview_path: str, preview_width: int = 220, preview_height: int = 200) -> None:
    image = cv2.imread(original_path)
    height, width = image.shape[:2]
    preview_aspect_ratio = preview_width / preview_height

    if width / height > 1.2:
        target_width = int(height * preview_aspect_ratio)
        x = (width - target_width) // 2
        image = image[:, x:x + target_width]
    elif width / height < 0.8:
        target_height = int(width / preview_aspect_ratio)
        y = (height - target_height) // 2
        image = image[y:y + target_height]

    image = cv2.resize(image, (preview_width, preview_height), interpolation=cv2.INTER_AREA)
    cv2.imwrite(preview_path, image, [cv2.IMWRITE_JPEG_QUALITY, 80])


def save_image(image: UploadFile, path: str) -> str:
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_name = image.filename.split("/")[-1]
        file_path = os.path.join(tmp_dir, file_name)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        finally:
            image.file.close()

        if os.path.isdir(path):
            path = os.path.join(path, f"{get_hash(file_path)}.jpg")

        shutil.move(file_path, path)

    return path


def parse_date(date: str) -> datetime:
    if match := re.fullmatch(r"(?P<year>\d\d\d\d)-(?P<month>\d\d?)-(?P<day>\d\d?)", date):
        return datetime(int(match.group("year")), int(match.group("month")), int(match.group("day")))

    if match := re.fullmatch(r"(?P<month>\d\d?)-(?P<year>\d\d\d\d)", date):
        return datetime(int(match.group("year")), int(match.group("month")), 1)

    if match := re.fullmatch(fr'(?P<month>({"|".join(constants.MONTH_TO_RUS.values())}))-(?P<year>\d\d\d\d)', date):
        rus2month = {month_rus: month for month, month_rus in constants.MONTH_TO_RUS.items()}
        return datetime(int(match.group("year")), rus2month[match.group("month")], 1)

    return datetime.now()


def parse_time(time: str) -> Tuple[int, int]:
    hour, minute = time.split(":")
    return int(hour), int(minute)


def quiz_to_datetime(quiz: dict) -> datetime:
    date = quiz["date"]
    hours, minutes = parse_time(quiz["time"])
    return datetime(date.year, date.month, date.day, hours, minutes, 0, 0)


def get_quizzes(start_date: datetime, end_date: datetime) -> Dict[datetime, List[dict]]:
    quizzes = list(database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}))
    date2quizzes = defaultdict(list)

    for quiz in quizzes:
        quiz_date = quiz["date"]
        quiz["date"] = {"year": quiz_date.year, "month": quiz_date.month, "day": quiz_date.day}
        quiz["_id"] = str(quiz["_id"])
        date2quizzes[quiz_date].append(quiz)

    for date, date_quizzes in date2quizzes.items():
        date2quizzes[date] = sorted(date_quizzes, key=lambda quiz: parse_time(quiz["time"]))

    return date2quizzes


def get_schedule(schedule_date: datetime) -> dict:
    start_weekday, num_days = calendar.monthrange(schedule_date.year, schedule_date.month)
    start_date = datetime(schedule_date.year, schedule_date.month, 1)
    end_date = datetime(schedule_date.year, schedule_date.month, num_days)
    prev_date = start_date + timedelta(days=-1)
    next_date = end_date + timedelta(days=1)

    date_quizzes = get_quizzes(start_date, end_date)
    places = sorted({quiz["place"] for quizzes in date_quizzes.values() for quiz in quizzes})

    rows = (num_days + start_weekday + 6) // 7
    calendar_cells = []

    weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

    for row in range(rows):
        cells = []

        for day in range(7):
            date = start_date + timedelta(days=day - start_weekday + 7 * row)
            cells.append({
                "year": date.year,
                "month": date.month,
                "day": date.day,
                "weekday": weekdays[date.weekday()],
                "current": date.month == schedule_date.month,
                "quizzes": date_quizzes.get(date, [])
            })

        calendar_cells.append(cells)

    return {
        "prev_date": f"{constants.MONTH_TO_RUS[prev_date.month]}-{prev_date.year}",
        "next_date": f"{constants.MONTH_TO_RUS[next_date.month]}-{next_date.year}",
        "month": constants.MONTH_TO_RUS[schedule_date.month],
        "year": schedule_date.year,
        "calendar": calendar_cells,
        "places": places
    }
