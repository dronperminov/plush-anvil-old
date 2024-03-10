import re
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Album:
    title: str
    album_id: int
    url: str
    photos: List[dict]
    date: datetime
    quiz_id: str
    preview_url: str

    @classmethod
    def from_dict(cls: "Album", data: dict) -> "Album":
        title = data["title"]
        album_id = data["album_id"]
        photos = data.get("photos", [])
        date = data["date"]
        cleared_title = re.sub(r"[ \-/]", "_", title)
        url = data.get("url", f"/albums/{album_id}-{cleared_title}")
        quiz_id = data.get("quiz_id", "")
        preview_url = data.get("preview_url", "")
        return cls(title, album_id, url, photos, date, quiz_id, preview_url)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "album_id": self.album_id,
            "url": self.url,
            "photos": self.photos,
            "date": self.date,
            "quiz_id": self.quiz_id,
            "preview_url": self.preview_url
        }
