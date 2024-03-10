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

SMUZI_RATING_TO_NAME = {
    300: {"name": "новички", "level": 1, "color_name": "зелёный"},
    600: {"name": "любители", "level": 2, "color_name": "жёлтый"},
    1200: {"name": "мастера", "level": 3, "color_name": "оранжевый"},
    2500: {"name": "профи", "level": 4, "color_name": "красный"},
    5000: {"name": "эксперты", "level": 5, "color_name": "фиолетовый"},
    10000: {"name": "гуру", "level": 6, "color_name": "бронзовый"},
    15000: {"name": "виртуозы", "level": 7, "color_name": "серебряный"},
    20000: {"name": "чемпионы", "level": 8, "color_name": "золотой"},
    30000: {"name": "титаны", "level": 9, "color_name": "чёрный"},
    50000: {"name": "динозавры", "level": 10, "color_name": "смузи"}
}
