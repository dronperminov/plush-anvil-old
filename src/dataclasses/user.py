from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    username: str
    password_hash: str
    fullname: str
    role: str = "user"
    image_src: str = "/profile-images/default.png"
    birthdate: Optional[dict] = None

    @classmethod
    def from_dict(cls: "User", data: dict) -> "User":
        return User(
            username=data["username"],
            password_hash=data["password_hash"],
            fullname=data["fullname"],
            role=data["role"],
            image_src=data["image_src"],
            birthdate=data.get("birthdate", None)
        )
