from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates
from src.database import database
from src.dataclasses.place import Place
from src.utils.auth import get_current_user
from src.utils.common import get_static_hash
from src.utils.place_utils import get_places_list

router = APIRouter()


@dataclass
class PlaceForm:
    name: str = Body(..., embed=True)
    metro_station: str = Body(..., embed=True)
    address: str = Body(..., embed=True)
    color: str = Body(..., embed=True)
    photos: List[str] = Body(..., embed=True)
    yandex_map_link: str = Body(..., embed=True)


@router.get("/places")
def get_places(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/places")

    if user["role"] != "owner":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    template = templates.get_template("admin_pages/places.html")
    metro_stations = list({station["name"] for station in database.metro_stations.find({})})

    content = template.render(user=user, page="places", version=get_static_hash(), places=get_places_list(), metro_stations=metro_stations)
    return HTMLResponse(content=content)


@router.post("/add-place")
def add_place(user: Optional[dict] = Depends(get_current_user), place_params: PlaceForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if database.places.find_one({"name": place_params.name}):
        return JSONResponse({"status": constants.ERROR, "message": "Место с таким названием уже имеется"})

    place = Place.from_dict({
        "name": place_params.name,
        "metro_station": place_params.metro_station,
        "address": place_params.address,
        "color": place_params.color,
        "photos": place_params.photos,
        "yandex_map_link": place_params.yandex_map_link
    })

    database.places.insert_one(place.to_dict())
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/delete-place")
def delete_place(user: Optional[dict] = Depends(get_current_user), name: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.places.find_one({"name": name}):
        return JSONResponse({"status": constants.ERROR, "message": f'Места с названием "{name}" не существует'})

    if database.quizzes.find_one({"place": name}):
        return JSONResponse({"status": constants.ERROR, "message": f'Место с названием "{name}" используется в квизах'})

    database.places.delete_one({"name": name})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/change-place-color")
def change_place_color(user: Optional[dict] = Depends(get_current_user), name: str = Body(..., embed=True), color: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.places.find_one({"name": name}):
        return JSONResponse({"status": constants.ERROR, "message": f'Места с названием "{name}" не существует'})

    database.places.update_one({"name": name}, {"$set": {"color": color}})
    return JSONResponse({"status": constants.SUCCESS})
