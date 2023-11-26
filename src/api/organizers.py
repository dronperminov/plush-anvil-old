from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates
from src.database import database
from src.dataclasses.organizer import Organizer
from src.utils.auth import get_current_user
from src.utils.common import get_static_hash

router = APIRouter()


@dataclass
class OrganizerAddForm:
    name: str = Body(..., embed=True)
    description: str = Body(..., embed=True)


@dataclass
class OrganizerUpdateForm(OrganizerAddForm):
    original_name: str = Body(..., embed=True)


@router.get("/organizers")
def get_organizers(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/organizers")

    if user["role"] != "owner":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    template = templates.get_template("pages/organizers.html")
    organizers = list(database.organizers.find({}))
    content = template.render(user=user, page="organizers", version=get_static_hash(), organizers=organizers)
    return HTMLResponse(content=content)


@router.post("/add-organizer")
def add_organizer(user: Optional[dict] = Depends(get_current_user), organizer_params: OrganizerAddForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if database.organizers.find_one({"name": organizer_params.name}):
        return JSONResponse({"status": constants.ERROR, "message": f'Организатор с названием "{organizer_params.name}" уже имеется'})

    organizer = Organizer.from_dict({"name": organizer_params.name, "description": organizer_params.description})
    database.organizers.insert_one(organizer.to_dict())
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/delete-organizer")
def delete_organizer(user: Optional[dict] = Depends(get_current_user), name: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.organizers.find_one({"name": name}):
        return JSONResponse({"status": constants.ERROR, "message": f'Организатора с названием "{name}" не существует'})

    if database.quizzes.find_one({"organizer": name}):
        return JSONResponse({"status": constants.ERROR, "message": f'Организатор с названием "{name}" используется в квизах'})

    database.organizers.delete_one({"name": name})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/update-organizer")
def update_organizer(user: Optional[dict] = Depends(get_current_user), organizer_params: OrganizerUpdateForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.organizers.find_one({"name": organizer_params.original_name}):
        return JSONResponse({"status": constants.ERROR, "message": f'Организатора с названием "{organizer_params.original_name}" не существует'})

    if organizer_params.original_name != organizer_params.name and database.organizers.find_one({"name": organizer_params.name}):
        return JSONResponse({"status": constants.ERROR, "message": f'Организатор с названием "{organizer_params.name}" уже имеется'})

    organizer = Organizer.from_dict({"name": organizer_params.name, "description": organizer_params.description})
    database.organizers.update_one({"name": organizer_params.original_name}, {"$set": organizer.to_dict()})
    database.quizzes.update_many({"organizer": organizer_params.original_name}, {"$set": {"organizer": organizer_params.name}})
    return JSONResponse({"status": constants.SUCCESS})
