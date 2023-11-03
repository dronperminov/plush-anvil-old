from pymongo import ASCENDING, MongoClient

from src import constants


class MongoManager:
    client: MongoClient = None
    users = None
    settings = None
    places = None
    quizzes = None
    photos = None

    def connect(self) -> None:
        self.client = MongoClient(constants.MONGO_URL)

        database = self.client[constants.MONGO_DATABASE]
        self.users = database[constants.MONGO_USERS_COLLECTION]
        self.settings = database[constants.MONGO_SETTINGS_COLLECTION]
        self.places = database[constants.MONGO_PLACES_COLLECTION]
        self.quizzes = database[constants.MONGO_QUIZZES_COLLECTION]
        self.photos = database[constants.MONGO_PHOTOS_COLLECTION]

        self.users.create_index([("username", ASCENDING)], unique=True)

    def close(self) -> None:
        self.client.close()
