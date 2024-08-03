from datetime import datetime
from typing import List, Optional

from src import constants
from src.database import database
from src.utils.common import get_word_form


def get_last_free_game(games: List[dict]) -> int:
    paid_games = 0

    for game in games[::-1]:
        if game["paid"] == constants.PASS_GAME:
            break

        paid_games += 1

    end_index = len(games) - paid_games - 1

    if paid_games == len(games):
        return -1

    return len(games) if paid_games >= 10 else end_index


def get_paid_games(games: List[dict]) -> int:
    end_index = get_last_free_game(games)

    if end_index == -1:
        return len(games)

    paid_games = 0
    for game in games[:end_index]:
        if game["paid"] == constants.PAID_GAME:
            paid_games += 1
        elif game["paid"] == constants.PASS_GAME:
            paid_games -= 10

    return paid_games


def get_participants_info(target_username: Optional[str] = None) -> List[dict]:
    users = {user["username"]: user for user in database.users.find({} if target_username is None else {"username": target_username})}
    user2games = {username: [{"date": date, "time": "", "paid": constants.PAID_GAME} for date in users[username].get("participant_dates", [])] for username in users}

    query = {
        "organizer": "Смузи",
        "participants": {"$exists": True},
        "date": {"$gte": datetime(2024, 4, 1)},
        "ignore_participants": {"$ne": True}
    }

    if target_username is not None:
        query["participants.username"] = target_username
        query["position"] = {"$gt": 0}

    for quiz in database.quizzes.find(query):
        for participant in quiz["participants"]:
            if participant["username"] not in users or quiz["date"] < users[participant["username"]].get("ignore_paid_before", quiz["date"]):
                continue

            count = participant.get("count", 1) - 1

            if participant["paid"] in [constants.PAID_GAME, constants.PASS_GAME]:
                user2games[participant["username"]].append({"date": quiz["date"], "time": quiz["time"], "paid": participant["paid"]})

            user2games[participant["username"]].extend([{"date": quiz["date"], "time": "", "paid": constants.PAID_GAME}] * count)

    participants = []

    for username, games in user2games.items():
        if len(games) == 0 and target_username is None:
            continue

        games = sorted(games, key=lambda game: (game["date"], game["time"]), reverse=True)
        paid_games = get_paid_games(games)
        participants.append({**users[username], "games": games, "paid_games": paid_games, "paid_games_text": get_word_form(paid_games, ["игр", "игры", "игра"])})

    participants = sorted(participants, key=lambda participant: -participant["paid_games"])
    return participants


def get_user_participant_info(username: str) -> dict:
    info = get_participants_info(target_username=username)[0]
    index = get_last_free_game(info["games"])
    games = info["games"] if index == -1 else info["games"][:index]
    stickers = []

    for game in games[::-1]:
        if game["paid"] != constants.PAID_GAME:
            continue

        if not stickers or len(stickers[-1]["dates"]) == 10:
            stickers.append({"used": None, "dates": []})

        stickers[-1]["dates"].append({"date": game["date"], "time": game["time"]})

    last_used = -1
    for game in games[::-1]:
        if game["paid"] == constants.PASS_GAME:
            last_used += 1
            stickers[last_used]["used"] = game["date"]

    return {"paid_games": info["paid_games"], "paid_games_text": get_word_form(info["paid_games"], ["игр", "игры", "игра"]), "stickers": stickers[::-1]}
