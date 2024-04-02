from collections import defaultdict
from typing import Dict

from src.database import database


def get_markup_users() -> Dict[str, dict]:
    user2count = defaultdict(int)
    for album in database.photo_albums.find({}):
        for photo in album["photos"]:
            for markup in photo["markup"]:
                user2count[markup["username"]] += 1

    users = sorted(database.users.find({}, {"username": 1, "fullname": 1, "image_src": 1, "_id": 0}), key=lambda user: -user2count[user["username"]])
    return {user["username"]: user for user in users}


def get_participant_users() -> Dict[str, dict]:
    user2count = defaultdict(int)
    for quiz in database.quizzes.find({"participants": {"$exists": True}}):
        for participant in quiz["participants"]:
            user2count[participant["username"]] += 1

    users = sorted(database.users.find({}, {"username": 1, "fullname": 1, "image_src": 1, "_id": 0}), key=lambda user: -user2count[user["username"]])
    return {user["username"]: user for user in users}
