from dataclasses import dataclass
from typing import List


@dataclass
class Place:
    name: str
    metro_station: str
    address: str
    color: str
    photos: List[str]
    yandex_map_link: str

    @classmethod
    def from_dict(cls: "Place", data: dict) -> "Place":
        name = data["name"]
        metro_station = data["metro_station"]
        address = data["address"]
        color = data["color"]
        photos = data.get("photos", [])
        yandex_map_link = data["yandex_map_link"]

        return cls(name, metro_station, address, color, photos, yandex_map_link)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "metro_station": self.metro_station,
            "address": self.address,
            "color": self.color,
            "photos": self.photos,
            "yandex_map_link": self.yandex_map_link
        }
