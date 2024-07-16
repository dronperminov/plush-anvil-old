import calendar
import hashlib
import os
import re
import shutil
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import cv2
from fastapi import UploadFile

from src import constants
from src.constants import SMUZI_POSITION_TO_SCORE, SMUZI_RATING_TO_NAME
from src.database import database
from src.dataclasses.quiz import Quiz


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

    k = min(height / preview_height, width / preview_width)

    target_width = int(preview_width * k)
    target_height = int(preview_height * k)
    x = (width - target_width) // 2
    y = (height - target_height) // 2
    image = image[y:y + target_height, x:x + target_width]

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


def get_date2quizzes(quizzes: List[dict]) -> Dict[datetime, List[dict]]:
    date2quizzes = defaultdict(list)

    for quiz in quizzes:
        quiz_date = quiz["date"]
        quiz["date"] = {"year": quiz_date.year, "month": quiz_date.month, "day": quiz_date.day}
        quiz["_id"] = str(quiz["_id"])
        date2quizzes[quiz_date].append(quiz)

    for date, date_quizzes in date2quizzes.items():
        date2quizzes[date] = sorted(date_quizzes, key=lambda quiz: parse_time(quiz["time"]))

    return date2quizzes


def get_word_form(count: int, word_forms: List[str]) -> str:
    if abs(count) % 10 in {0, 5, 6, 7, 8, 9} or abs(count) % 100 in {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}:
        return f"{count} {word_forms[0]}"

    if abs(count) % 10 in {2, 3, 4}:
        return f"{count} {word_forms[1]}"

    return f"{count} {word_forms[2]}"


def get_smuzi_rating() -> dict:
    query = {
        "date": {"$gte": datetime(2024, 1, 1)},
        "position": {"$ne": 0},
        "organizer": "Смузи",
        "ignore_rating": {"$ne": True}
    }

    quizzes = list(database.quizzes.find(query).sort("date", 1))
    rating = 0
    level = -1
    players = []
    history = []

    for quiz in quizzes:
        rating += SMUZI_POSITION_TO_SCORE.get(quiz["position"], 50)
        players.append(quiz.get("players", 0))

        if level < len(SMUZI_RATING_TO_NAME) - 1 and rating >= SMUZI_RATING_TO_NAME[level + 1]["score"]:
            level += 1
            history.append({"date": quiz["date"], "score": rating, "players": players, "mean_players": sum(players) / len(players)})
            players = []

    mean_rating = rating / max(len(quizzes), 1)
    next_level = None

    if level < len(SMUZI_RATING_TO_NAME) - 1:
        next_level = {
            "count": get_word_form(round((SMUZI_RATING_TO_NAME[level + 1]["score"] - rating) / mean_rating + 0.5), ["игр", "игры", "игра"]),
            "score": get_word_form(SMUZI_RATING_TO_NAME[level + 1]["score"] - rating, ["баллов", "балла", "балл"]),
            "info": SMUZI_RATING_TO_NAME[level + 1]
        }

    return {
        "score": rating,
        "mean": mean_rating,
        "total_games": len(quizzes),
        "total_games_text": get_word_form(len(quizzes), ["игр", "игры", "игру"]),
        "next_level": next_level,
        "info": SMUZI_RATING_TO_NAME[level],
        "players": players,
        "mean_players": sum(players) / max(len(players), 1),
        "history": history
    }


def get_dates_query(start_date: Optional[datetime], end_date: Optional[datetime]) -> dict:
    if start_date is None and end_date is None:
        return {}

    query = {"date": {}}
    if start_date is not None:
        query["date"]["$gte"] = start_date

    if end_date is not None:
        query["date"]["$lte"] = end_date

    return query


def get_categories_count(quizzes: List[Quiz]) -> Dict[str, int]:
    categories = {category: 0 for category in constants.CATEGORIES}

    for quiz in quizzes:
        categories[quiz.category] += 1

    return categories


def get_top_players(username2quizzes: Dict[str, List[Quiz]]) -> List[dict]:
    usernames = [username for username in username2quizzes]
    users = {user["username"]: user for user in database.users.find({"username": {"$in": usernames}}, {"_id": 0})}
    top_players = []

    for username, quizzes in username2quizzes.items():
        categories = [(category, count) for category, count in get_categories_count(quizzes).items() if count > 0]

        top_players.append({
            **users[username],
            "count": len(quizzes),
            "count_text": get_word_form(len(quizzes), ["игр", "игры", "игра"]),
            "categories": sorted(categories, key=lambda category: -category[1])
        })

    return sorted(top_players, key=lambda player: (-player["count"], player["fullname"]))


def get_analytics_data(quizzes: List[Quiz], only_main: bool = False) -> dict:
    data = {
        "games": len(quizzes),
        "wins": len([quiz for quiz in quizzes if quiz.is_win()]),
        "prizes": len([quiz for quiz in quizzes if quiz.is_prize()]),
        "top10": len([quiz for quiz in quizzes if quiz.is_top10()]),
        "last": len([quiz for quiz in quizzes if quiz.is_last()]),
        "rating": sum(quiz.smuzi_rating() for quiz in quizzes),
        "mean_position": sum(quiz.position for quiz in quizzes) / max(1, len(quizzes)),
        "mean_players": sum(quiz.players for quiz in quizzes) / max(1, len(quizzes))
    }

    if only_main:
        return data

    positions = {i: 0 for i in range(1, 17)}
    category_positions = {category: {i: 0 for i in range(1, 17)} for category in constants.CATEGORIES}
    category2positions = {category: [] for category in constants.CATEGORIES}
    categories = get_categories_count(quizzes)
    categories_wins = {category: 0 for category in constants.CATEGORIES}
    categories_prizes = {category: 0 for category in constants.CATEGORIES}
    username2quizzes = defaultdict(list)

    for quiz in quizzes:
        positions[min(quiz.position, 16)] += 1
        category_positions[quiz.category][min(quiz.position, 16)] += 1
        category2positions[quiz.category].append(quiz.position)

        if quiz.is_win():
            categories_wins[quiz.category] += 1

        if quiz.is_prize():
            categories_prizes[quiz.category] += 1

        for participant in quiz.participants:
            username2quizzes[participant["username"]].append(quiz)

    for category, cat_positions in category_positions.items():
        cat_positions["mean"] = sum(category2positions[category]) / max(1, len(category2positions[category]))

    data["positions"] = positions
    data["category_positions"] = category_positions
    data["categories"] = sorted([{"name": name, "value": count} for name, count in categories.items()], key=lambda info: (info["name"] == "прочее", -info["value"]))
    data["categories_wins"] = categories_wins
    data["categories_prizes"] = categories_prizes
    data["top_players"] = get_top_players(username2quizzes)

    return data


def get_analytics(start_date: Optional[datetime], end_date: Optional[datetime]) -> dict:
    quizzes = [Quiz.from_dict(quiz) for quiz in database.quizzes.find({"position": {"$gt": 0}, **get_dates_query(start_date, end_date)})]
    games = {category: [] for category in constants.CATEGORIES}
    date2quizzes = defaultdict(list)

    for quiz in quizzes:
        games[quiz.category].append(quiz)
        date2quizzes[(quiz.date.year, quiz.date.month)].append(quiz)

    for category, category_games in games.items():
        games[category] = sorted(category_games, key=lambda quiz: (-quiz.position, quiz.date, quiz.time), reverse=True)

    months_data = []

    for (year, month), month_quizzes in date2quizzes.items():
        months_data.append({
            "date": {"year": year, "month": month},
            **get_analytics_data(month_quizzes)
        })

    return {
        "total": get_analytics_data(quizzes),
        "games": games,
        "months_data": sorted(months_data, key=lambda info: (info["date"]["year"], info["date"]["month"])),
    }


def get_schedule(schedule_date: datetime) -> dict:
    start_weekday, num_days = calendar.monthrange(schedule_date.year, schedule_date.month)
    start_date = datetime(schedule_date.year, schedule_date.month, 1)
    end_date = datetime(schedule_date.year, schedule_date.month, num_days)
    prev_date = start_date + timedelta(days=-1)
    next_date = end_date + timedelta(days=1)

    quizzes = list(database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}))
    statistics = get_analytics_data([Quiz.from_dict(quiz) for quiz in quizzes if quiz["position"] != 0], only_main=True)

    date_quizzes = get_date2quizzes(quizzes)
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
        "places": places,
        "statistics": statistics
    }


def get_places() -> Dict[str, dict]:
    places = {place["name"]: place for place in database.places.find({}, {"_id": 0})}
    return places


def get_month_dates(date: datetime) -> Tuple[datetime, datetime]:
    _, num_days = calendar.monthrange(date.year, date.month)
    start_date = datetime(date.year, date.month, 1, 0, 0, 0)
    end_date = start_date + timedelta(days=num_days)
    return start_date, end_date
