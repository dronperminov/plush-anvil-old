import calendar
import hashlib
import os
import re
import shutil
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import bson
import cv2
from fastapi import UploadFile

from src import constants
from src.achievements.achievement import Achievement
from src.achievements.hardy_achievement import HardyAchievement
from src.achievements.position_count_achievement import PositionCountAchievement
from src.achievements.position_days_achievement import PositionDaysAchievement
from src.achievements.solo_achievement import SoloAchievement
from src.achievements.team_achievements.diversity_month_achievement import DiversityMonthAchievement
from src.achievements.team_achievements.narrow_circle_achievement import NarrowCircleAchievement
from src.achievements.team_achievements.there_here_achievement import ThereHereAchievement
from src.achievements.user_achievements.games_count_achievement import GamesCountAchievement
from src.achievements.user_achievements.players_count_achievement import PlayersCountAchievement
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


def get_word_form(count: int, word_forms: List[str], only_form: bool = False) -> str:
    index = 2

    if abs(count) % 10 in {0, 5, 6, 7, 8, 9} or abs(count) % 100 in {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}:
        index = 0
    elif abs(count) % 10 in {2, 3, 4}:
        index = 1

    return word_forms[index] if only_form else f"{count} {word_forms[index]}"


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
        today = datetime.now()
        count = round((SMUZI_RATING_TO_NAME[level + 1]["score"] - rating) / mean_rating + 0.5)
        days = (today - quizzes[0]["date"]).days
        last_days = round(days / len(quizzes) * count + 0.5)
        end_date = today + timedelta(days=last_days)

        next_level = {
            "count": get_word_form(count, ["игр", "игры", "игра"]),
            "score": get_word_form(SMUZI_RATING_TO_NAME[level + 1]["score"] - rating, ["баллов", "балла", "балл"]),
            "days": get_word_form(last_days, ["дней", "дня", "день"]),
            "end_date": f"{end_date.day:02}.{end_date.month:02}.{end_date.year}",
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


def get_activity_score(quizzes: List[Quiz], end_date: datetime, alpha: float) -> float:
    return sum(alpha ** (end_date - quiz.date).days for quiz in quizzes)


def get_top_players(quizzes: List[Quiz], alpha: float = 0.98) -> List[dict]:
    username2quizzes = defaultdict(list)

    for quiz in quizzes:
        for participant in quiz.participants:
            username2quizzes[participant["username"]].append(quiz)

    end_date = max([quiz.date for quiz in quizzes], default=datetime.now())
    usernames = [username for username in username2quizzes]
    users = {user["username"]: user for user in database.users.find({"username": {"$in": usernames}}, {"_id": 0})}
    top_players = []

    for username, user_quizzes in username2quizzes.items():
        categories = [(category, count) for category, count in get_categories_count(user_quizzes).items() if count > 0]

        top_players.append({
            **users[username],
            "score": get_activity_score(user_quizzes, end_date, alpha),
            "count": len(user_quizzes),
            "count_text": get_word_form(len(user_quizzes), ["игр", "игры", "игра"]),
            "categories": sorted(categories, key=lambda category: -category[1])
        })

    return sorted(top_players, key=lambda player: (-player["score"], -player["count"], player["fullname"]))


def get_analytics_data(quizzes: List[Quiz], only_main: bool = False) -> dict:
    data = {
        "games": len(quizzes),
        "wins": len([quiz for quiz in quizzes if quiz.is_win()]),
        "prizes": len([quiz for quiz in quizzes if quiz.is_prize()]),
        "top10": len([quiz for quiz in quizzes if quiz.is_top10()]),
        "rating": sum(quiz.smuzi_rating() for quiz in quizzes),
        "mean_position": sum(quiz.position for quiz in quizzes) / max(1, len(quizzes)),
        "mean_players": sum(quiz.players for quiz in quizzes) / max(1, len(quizzes))
    }

    data["top3"] = data["wins"] + data["prizes"]

    if only_main:
        return data

    positions = {i: 0 for i in range(1, 17)}
    category_positions = {category: {i: 0 for i in range(1, 17)} for category in constants.CATEGORIES}
    category2positions = {category: [] for category in constants.CATEGORIES}
    categories = get_categories_count(quizzes)
    categories_wins = {category: 0 for category in constants.CATEGORIES}
    categories_prizes = {category: 0 for category in constants.CATEGORIES}

    for quiz in quizzes:
        positions[min(quiz.position, 16)] += 1
        category_positions[quiz.category][min(quiz.position, 16)] += 1
        category2positions[quiz.category].append(quiz.position)

        if quiz.is_win():
            categories_wins[quiz.category] += 1

        if quiz.is_prize():
            categories_prizes[quiz.category] += 1

    for category, cat_positions in category_positions.items():
        cat_positions["mean"] = sum(category2positions[category]) / max(1, len(category2positions[category]))

    data["positions"] = positions
    data["category_positions"] = category_positions
    data["categories"] = sorted([{"name": name, "value": count} for name, count in categories.items()], key=lambda info: (info["name"] == "прочее", -info["value"]))
    data["categories_wins"] = categories_wins
    data["categories_prizes"] = categories_prizes

    return data


def get_analytics(start_date: Optional[datetime], end_date: Optional[datetime], only_main: bool = False) -> dict:
    quizzes = [Quiz.from_dict(quiz) for quiz in database.quizzes.find({"position": {"$gt": 0}, **get_dates_query(start_date, end_date)})]

    if only_main:
        return get_analytics_data(quizzes, only_main=False)

    date2quizzes = defaultdict(list)
    organizers = defaultdict(int)
    categories = defaultdict(int)
    places = defaultdict(int)

    for quiz in quizzes:
        date2quizzes[(quiz.date.year, quiz.date.month)].append(quiz)
        categories[quiz.category] += 1
        organizers[quiz.organizer] += 1
        places[quiz.place] += 1

    months_data = []

    for (year, month), month_quizzes in date2quizzes.items():
        months_data.append({
            "date": {"year": year, "month": month},
            **get_analytics_data(month_quizzes),
            "top_players": get_top_players(month_quizzes)
        })

    return {
        "total": get_analytics_data(quizzes),
        "top_players": get_top_players(quizzes),
        "games": sorted(quizzes, key=lambda quiz: (quiz.date, quiz.time, -quiz.position), reverse=True),
        "categories": sorted([(count, name) for name, count in categories.items()], reverse=True),
        "organizers": sorted([(count, name) for name, count in organizers.items()], reverse=True),
        "places": sorted([(count, name) for name, count in places.items()], reverse=True),
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


def get_handle_user_achievements(username: str) -> List[Achievement]:
    user = database.users.find_one({"username": username}, {"achievements": 1})
    achievements = {achievement["id"]: Achievement(achievement["name"], achievement["description"]) for achievement in constants.HANDLE_ACHIEVEMENTS}

    for achievement in user.get("achievements", []):
        achievements[achievement["achievement_id"]].increment(achievement["date"])

    for achievement in achievements.values():
        achievement.set_label_date()

    return [achievements[achievement["id"]] for achievement in constants.HANDLE_ACHIEVEMENTS]


def get_photos_achievement(username: str, quiz_ids: List[bson.ObjectId]) -> Achievement:
    achievement = Achievement(name="Невидимка", description="не попасть на фото с игры")

    for album in database.photo_albums.find({"quiz_id": {"$in": quiz_ids}}):
        album_usernames = {markup["username"] for photo in album["photos"] for markup in photo["markup"]}
        if username not in album_usernames:
            achievement.increment(album["date"].date())

    achievement.set_label_date()
    return achievement


def get_team_achievements() -> List[Achievement]:
    quizzes = [Quiz.from_dict(quiz) for quiz in database.quizzes.find({"position": {"$gt": 0}}).sort("date")]
    achievements = [
        ThereHereAchievement(),
        HardyAchievement(name="Выносливые", description="посетить две и более игры в один день", min_count=2, max_count=100),
        SoloAchievement(name="Соло", description="сыграть командой из одного человека"),
        DiversityMonthAchievement(),
        NarrowCircleAchievement(),
        PositionDaysAchievement(name="7 дней призов", description="7 дней подряд входить в тройку", target_count=7, position=3),
        PositionDaysAchievement(name="7 дней побед", description="7 дней подряд одержать победу", target_count=7, position=1),
        PositionDaysAchievement(name="7 дней игр", description="7 дней подряд ходить на квизы", target_count=7, position=100),
        PositionDaysAchievement(name="15 дней игр", description="15 дней подряд ходить на квизы", target_count=15, position=100),
        PositionDaysAchievement(name="30 дней игр", description="30 дней подряд ходить на квизы", target_count=30, position=100),

        PositionCountAchievement(name="50 призов", description="войти в тройку в 50 квизах", target_count=50, position=3),
        PositionCountAchievement(name="100 призов", description="войти в тройку в 100 квизах", target_count=100, position=3),
        PositionCountAchievement(name="250 призов", description="войти в тройку в 250 квизах", target_count=250, position=3),

        PositionCountAchievement(name="50 побед", description="победить в 50 квизах", target_count=50, position=1),
        PositionCountAchievement(name="100 побед", description="победить в 100 квизах", target_count=100, position=1),
        PositionCountAchievement(name="250 побед", description="победить в 250 квизах", target_count=250, position=1)
    ]

    for achievement in achievements:
        achievement.analyze(quizzes)
        achievement.set_label_date()

    return sorted(achievements, key=lambda achievement: achievement.count == 0)


def get_user_achievements(username: str) -> List[Achievement]:
    achievements = [
        SoloAchievement(name="Одиночка", description="участвовать в соло"),
        GamesCountAchievement(name="Частый гость", description="посетить 100 игр", target_count=100),
        GamesCountAchievement(name="Преданный фанат", description="посетить 1000 игр", target_count=1000),
        PlayersCountAchievement(name="Суперкоманда", description="участвовать в команде, состоящей из 10 и более игроков", min_count=10, max_count=12),
        PlayersCountAchievement(name="Узким кругом", description="участвовать в команде, состоящей из 5 и менее игроков", min_count=1, max_count=5),
        HardyAchievement(name="Выносливый", description="участвовать в двух играх в один день", min_count=2, max_count=2),
        HardyAchievement(name="Очень выносливый", description="участвовать в трёх и более играх в один день", min_count=3, max_count=100),
        PositionDaysAchievement(name="7 дней игр", description="участвовать в играх 7 дней подряд", target_count=7, position=100),

        PositionCountAchievement(name="Призёр", description="посетить игру и войти в тройку", target_count=1, position=3),
        PositionCountAchievement(name="Призёр-50", description="посетить 50 игр и войти в тройку", target_count=50, position=3),
        PositionCountAchievement(name="Победитель", description="посетить победную игру", target_count=1, position=1),
        PositionCountAchievement(name="Победитель-50", description="посетить 50 победных игр", target_count=50, position=1),
    ]

    quizzes = list(database.quizzes.find({"position": {"$gt": 0}, "participants.username": username}).sort("date"))
    quiz_ids = [quiz["_id"] for quiz in quizzes]
    quizzes = [Quiz.from_dict(quiz) for quiz in quizzes]

    for achievement in achievements:
        achievement.analyze(quizzes)
        achievement.set_label_date()

    achievements.append(get_photos_achievement(username, quiz_ids))
    achievements.extend(get_handle_user_achievements(username))
    return sorted(achievements, key=lambda achievement: achievement.count == 0)
