from dataclasses import dataclass


@dataclass
class User:
    username: str
    password_hash: str
    fullname: str
    role: str = "user"
    image_src: str = "/profile-images/default.png"
