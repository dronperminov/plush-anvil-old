from pymongo import ASCENDING, MongoClient

from src import constants


class MongoManager:
    client: MongoClient = None
    users = None
    settings = None
    places = None
    organizers = None
    quizzes = None
    photos = None
    metro_stations = None

    def connect(self) -> None:
        self.client = MongoClient(constants.MONGO_URL)

        database = self.client[constants.MONGO_DATABASE]
        self.users = database[constants.MONGO_USERS_COLLECTION]
        self.settings = database[constants.MONGO_SETTINGS_COLLECTION]
        self.places = database[constants.MONGO_PLACES_COLLECTION]
        self.organizers = database[constants.MONGO_ORGANIZERS_COLLECTION]
        self.quizzes = database[constants.MONGO_QUIZZES_COLLECTION]
        self.photos = database[constants.MONGO_PHOTOS_COLLECTION]
        self.metro_stations = database[constants.MONGO_METRO_STATIONS_COLLECTION]

        self.users.create_index([("username", ASCENDING)], unique=True)
        self.quizzes.create_index([("date", ASCENDING), ("name", ASCENDING), ("place", ASCENDING)], unique=True)
        self.places.create_index([("name", ASCENDING)], unique=True)
        self.organizers.create_index([("name", ASCENDING)], unique=True)
        self.metro_stations.create_index([("name", ASCENDING)])

    def close(self) -> None:
        self.client.close()
