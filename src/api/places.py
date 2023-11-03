from typing import Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates
from src.database import database
from src.dataclasses.place import Place
from src.forms.place import PlaceForm
from src.utils.auth import get_current_user
from src.utils.common import get_static_hash

router = APIRouter()


@router.get("/places")
def get_places(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/logout")

    if user["role"] != "admin":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    template = templates.get_template("pages/places.html")
    places = [Place.from_dict(place) for place in database.places.find({})]
    metro_stations = list({station["name"] for station in database.metro_stations.find({})})

    content = template.render(user=user, page="places", version=get_static_hash(), places=places, metro_stations=metro_stations)
    return HTMLResponse(content=content)


@router.post("/add-place")
def add_place(user: Optional[dict] = Depends(get_current_user), place_params: PlaceForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "admin":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if database.places.find_one({"name": place_params.name}):
        return JSONResponse({"status": constants.ERROR, "message": "Место с таким названием уже имеется"})

    place = Place.from_dict({
        "name": place_params.name,
        "metro_station": place_params.metro_station,
        "address": place_params.address,
        "color": place_params.color,
        "photos": place_params.photos
    })

    database.places.insert_one(place.to_dict())
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/remove-place")
def remove_place(user: Optional[dict] = Depends(get_current_user), name: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "admin":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.places.find_one({"name": name}):
        return JSONResponse({"status": constants.ERROR, "message": f'Места с названием "{name}" не существует'})

    database.places.delete_one({"name": name})
    return JSONResponse({"status": constants.SUCCESS})
