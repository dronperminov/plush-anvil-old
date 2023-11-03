from dataclasses import dataclass
from typing import List


@dataclass
class Place:
    name: str
    metro_station: str
    address: str
    color: str
    photos: List[str]

    @classmethod
    def from_dict(cls: "Place", data: dict) -> "Place":
        name = data["name"]
        metro_station = data["metro_station"]
        address = data["address"]
        color = data["color"]
        photos = data.get("photos", [])

        return cls(name, metro_station, address, color, photos)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "metro_station": self.metro_station,
            "address": self.address,
            "color": self.color,
            "photos": self.photos
        }
