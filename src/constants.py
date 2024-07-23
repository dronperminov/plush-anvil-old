MONGO_URL = "mongodb://localhost:27017/"
MONGO_DATABASE = "quiz"
MONGO_USERS_COLLECTION = "users"
MONGO_SETTINGS_COLLECTION = "settings"
MONGO_PLACES_COLLECTION = "places"
MONGO_ORGANIZERS_COLLECTION = "organizers"
MONGO_QUIZZES_COLLECTION = "quizzes"
MONGO_PHOTO_ALBUMS_COLLECTION = "photo_albums"
MONGO_PHOTOS_COLLECTION = "photos"
MONGO_METRO_STATIONS_COLLECTION = "metro_stations"
MONGO_TG_QUIZ_MESSAGES = "tg_quiz_messages"
MONGO_TG_MESSAGES = "tg_messages"

ERROR = "error"
SUCCESS = "success"

CROP_IMAGE_SIZE = 200
LAST_POLL_OPTION = 9

MONTH_TO_RUS = {
    1: "январь",
    2: "февраль",
    3: "март",
    4: "апрель",
    5: "май",
    6: "июнь",
    7: "июль",
    8: "август",
    9: "сентябрь",
    10: "октябрь",
    11: "ноябрь",
    12: "декабрь",
}

WEEKDAY_TO_RUS = {
    0: "понедельник",
    1: "вторник",
    2: "среду",
    3: "четверг",
    4: "пятницу",
    5: "субботу",
    6: "воскресенье"
}

SMUZI_POSITION_TO_SCORE = {
    1: 100,
    2: 95,
    3: 90,
    4: 85,
    5: 80,
    6: 75,
    7: 70,
    8: 65,
    9: 60,
    10: 58,
    11: 56,
    12: 54,
    13: 53,
    14: 52,
    15: 51
}

SMUZI_RATING_TO_NAME = [
    {"score": 300, "name": "новички", "level": 1, "color_name": "зелёный"},
    {"score": 600, "name": "любители", "level": 2, "color_name": "жёлтый"},
    {"score": 1200, "name": "мастера", "level": 3, "color_name": "оранжевый"},
    {"score": 2500, "name": "профи", "level": 4, "color_name": "красный"},
    {"score": 5000, "name": "эксперты", "level": 5, "color_name": "фиолетовый"},
    {"score": 10000, "name": "гуру", "level": 6, "color_name": "бронзовый"},
    {"score": 15000, "name": "виртуозы", "level": 7, "color_name": "серебряный"},
    {"score": 20000, "name": "чемпионы", "level": 8, "color_name": "золотой"},
    {"score": 30000, "name": "титаны", "level": 9, "color_name": "чёрный"},
    {"score": 50000, "name": "динозавры", "level": 10, "color_name": "смузи"}
]

CATEGORIES = [
    "КМС",
    "медиа-микс",
    "УМ",
    "караоке",
    "музыка",
    "ГП",
    "обо всём",
    "видеоигры",
    "прочее"
]

CATEGORY2COLOR = {
    "КМС": "#ec6b56",
    "УМ": "#ffc154",
    "ГП": "#478bb3",
    "музыка": "#47b39c",
    "караоке": "#6347b3",
    "медиа-микс": "#b347a4",
    "обо всём": "#8bc34a",
    "видеоигры": "#ff5471",
    "прочее": "#cccccc"
}

ANALYTICS_COLORS = {
    "wins": "#ec6b56",
    "prizes": "#ffc154",
    "top3": "#d82e6b",
    "top10": "#47b39c",
    "other": "#cccccc",
    "games": "#478bb3",
    "mean_position": "#478bb3",
    "mean_players": "#47b36b",
    "rating": "#ffc154",
    "position": "#00bcd4"
}

FREE_GAME = "free"
PAID_GAME = "paid"
PASS_GAME = "pass"

HANDLE_ACHIEVEMENTS = [
    {"id": "place", "name": "Топограф", "description": "перепутать место проведения квиза"},
    {"id": "time", "name": "Вне времени", "description": "перепутать время проведения квиза"},
    {"id": "forget", "name": "Забывчивый", "description": "забыть про квиз"}
]
