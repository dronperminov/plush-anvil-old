from pymongo import ASCENDING, DESCENDING, MongoClient

from src import constants


class MongoManager:
    client: MongoClient = None
    users = None
    settings = None
    places = None
    organizers = None
    quizzes = None
    photo_albums = None
    photos = None
    metro_stations = None
    tg_quiz_messages = None

    def connect(self) -> None:
        self.client = MongoClient(constants.MONGO_URL)

        database = self.client[constants.MONGO_DATABASE]
        self.users = database[constants.MONGO_USERS_COLLECTION]
        self.settings = database[constants.MONGO_SETTINGS_COLLECTION]
        self.places = database[constants.MONGO_PLACES_COLLECTION]
        self.organizers = database[constants.MONGO_ORGANIZERS_COLLECTION]
        self.quizzes = database[constants.MONGO_QUIZZES_COLLECTION]
        self.photo_albums = database[constants.MONGO_PHOTO_ALBUMS_COLLECTION]
        self.photos = database[constants.MONGO_PHOTOS_COLLECTION]
        self.metro_stations = database[constants.MONGO_METRO_STATIONS_COLLECTION]
        self.tg_quiz_messages = database[constants.MONGO_TG_QUIZ_MESSAGES]

        self.users.create_index([("username", ASCENDING)], unique=True)
        self.quizzes.create_index([("date", ASCENDING), ("name", ASCENDING), ("place", ASCENDING)], unique=True)
        self.places.create_index([("name", ASCENDING)], unique=True)
        self.organizers.create_index([("name", ASCENDING)], unique=True)
        self.photo_albums.create_index([("name", ASCENDING)])
        self.photo_albums.create_index([("album_id", DESCENDING)])
        self.metro_stations.create_index([("name", ASCENDING)])
        self.tg_quiz_messages.create_index([("quiz_id", ASCENDING)], unique=True)

    def close(self) -> None:
        self.client.close()
