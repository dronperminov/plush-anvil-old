from dataclasses import dataclass
from typing import List

from fastapi import Body


@dataclass
class PlaceForm:
    name: str = Body(..., embed=True)
    metro_station: str = Body(..., embed=True)
    address: str = Body(..., embed=True)
    color: str = Body(..., embed=True)
    photos: List[str] = Body(..., embed=True)
