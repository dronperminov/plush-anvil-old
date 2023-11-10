from dataclasses import dataclass


@dataclass
class Organizer:
    name: str
    description: str

    @classmethod
    def from_dict(cls: "Organizer", data: dict) -> "Organizer":
        name = data["name"]
        description = data.get("description", [])

        return cls(name, description)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description
        }
