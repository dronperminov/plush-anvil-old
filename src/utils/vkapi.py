import random
import time
from typing import List, Optional

import requests


class VKApi:
    def __init__(self, tokens: List[str]) -> None:
        self.tokens = tokens

    def __get_request(self, url: str, max_attempts: int = 10) -> Optional[dict]:
        ignore_error2times = {
            "Too many requests per second": 2,
            "Unknown application: could not get application": 0.5,
            "Internal server error: could not check access_token now, check later.": 1
        }

        for _ in range(max_attempts):
            token = random.choice(self.tokens)

            try:
                response = requests.post(f"{url}&access_token={token}", headers={"Content-Type": "multipart/form-data"})
            except requests.exceptions.ConnectionError:
                print("Connection error")  # noqa
                continue

            if response.status_code != 200:
                print(f"Error: status code: {response.status_code}, json: {response.json()}")  # noqa
                continue

            result = response.json()

            if "error" not in result:
                return result["response"]

            error = result["error"]

            if error["error_msg"] in ignore_error2times:
                time.sleep(ignore_error2times[error["error_msg"]])

        return None

    def get_post(self, post_id: str) -> Optional[str]:
        url = f"https://api.vk.com/method/wall.getById?posts={post_id}&v=5.154"
        posts = self.__get_request(url)
        if posts is None:
            return None

        if len(posts["items"]) == 0:
            return None

        assert len(posts["items"]) == 1
        return posts["items"][0]["text"]
