from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from src.database import database
from src.dataclasses.place import Place


def get_places_list() -> List[Place]:
    today = datetime.now()
    place2score = defaultdict(float)

    for quiz in database.quizzes.find({"position": {"$gt": 0}}):
        place2score[quiz["place"]] += 0.98 ** (today - quiz["date"]).days

    places = [Place.from_dict(place) for place in database.places.find({})]
    return sorted(places, key=lambda place: -place2score[place.name])


def get_place_names() -> List[str]:
    return [place.name for place in get_places_list()]


def get_places_dict() -> Dict[str, dict]:
    return {place["name"]: place for place in database.places.find({}, {"_id": 0})}
