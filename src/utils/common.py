import calendar
import hashlib
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

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
        hashes.append(get_hash(os.path.join(styles_dir, filename)))

    for filename in os.listdir(js_dir):
        hashes.append(get_hash(os.path.join(js_dir, filename)))

    statis_hash = "_".join(hashes)
    hash_md5 = hashlib.md5()
    hash_md5.update(statis_hash.encode("utf-8"))

    return hash_md5.hexdigest()


def parse_time(time: str) -> Tuple[int, int]:
    hour, minute = time.split(":")
    return int(hour), int(minute)


def get_quizzes(start_date: datetime, end_date: datetime) -> Dict[datetime, List[dict]]:
    quizzes = list(database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}))
    date2quizzes = defaultdict(list)

    for quiz in quizzes:
        date2quizzes[quiz["date"]].append(quiz)

    for date, date_quizzes in date2quizzes.items():
        date2quizzes[date] = sorted(date_quizzes, key=lambda quiz: parse_time(quiz["time"]))

    return date2quizzes


def get_schedule() -> dict:
    today = datetime.now()

    start_weekday, num_days = calendar.monthrange(today.year, today.month)
    start_date = datetime(today.year, today.month, 1)
    end_date = datetime(today.year, today.month, num_days)

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
                "current": date.month == today.month,
                "today": date.day == today.day,
                "quizzes": date_quizzes.get(date, [])
            })

        calendar_cells.append(cells)

    return {
        "month": constants.MONTH_TO_RUS[today.month],
        "calendar": calendar_cells,
        "places": places
    }
