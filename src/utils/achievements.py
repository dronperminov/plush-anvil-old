from typing import List

import bson

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
from src.database import database
from src.dataclasses.quiz import Quiz


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
        PositionDaysAchievement(name="14 дней игр", description="участвовать в играх 14 дней подряд", target_count=14, position=100),

        PositionCountAchievement(name="Призёр", description="посетить игру и войти в тройку", target_count=1, position=3),
        PositionCountAchievement(name="Призёр-50", description="посетить 50 игр и войти в тройку", target_count=50, position=3),
        PositionCountAchievement(name="Победитель", description="посетить победную игру", target_count=1, position=1),
        PositionCountAchievement(name="Победитель-50", description="посетить 50 победных игр", target_count=50, position=1),
    ]

    quizzes = list(database.quizzes.find({"position": {"$gt": 0}, "participants.username": username}).sort("date"))
    quiz_ids = [quiz["_id"] for quiz in quizzes]
    quizzes = [Quiz.from_dict(quiz) for quiz in quizzes]

    for achievement in achievements:
        if quizzes:
            achievement.analyze(quizzes)

        achievement.set_label_date()

    achievements.append(get_photos_achievement(username, quiz_ids))
    achievements.extend(get_handle_user_achievements(username))
    return sorted(achievements, key=lambda achievement: achievement.count == 0)
