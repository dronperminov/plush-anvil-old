from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates, vk_api
from src.database import database
from src.dataclasses.quiz import Quiz
from src.utils.auth import get_current_user
from src.utils.common import get_static_hash, parse_date

router = APIRouter()


@dataclass
class QuizAddForm:
    name: str = Body(..., embed=True)
    short_name: str = Body(..., embed=True)
    date: datetime = Body(..., embed=True)
    time: str = Body(..., embed=True)
    place: str = Body(..., embed=True)
    organizer: str = Body(..., embed=True)
    description: str = Body(..., embed=True)
    cost: int = Body(..., embed=True)
    position: int = Body(0, embed=True)
    teams: int = Body(0, embed=True)
    players: int = Body(0, embed=True)


@dataclass
class QuizUpdateForm(QuizAddForm):
    quiz_id: str = Body(..., embed=True)


@router.get("/quizzes/{date}")
def get_quizzes(date: str, user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url=f"/login?back_url=/quizzes/{date}")

    if user["role"] != "owner":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    date = parse_date(date)
    weekday = constants.WEEKDAY_TO_RUS[date.weekday()]

    template = templates.get_template("pages/quizzes.html")
    places = [place["name"] for place in database.places.find({})]
    organizers = [organizer["name"] for organizer in database.organizers.find({})]
    quizzes = list(database.quizzes.find({"date": date}))

    content = template.render(user=user, page="quizzes", version=get_static_hash(), quizzes=quizzes, places=places, organizers=organizers, date=date, weekday=weekday)
    return HTMLResponse(content=content)


@router.get("/parse-quizzes")
def parse_quizzes(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/parse-quizzes")

    if user["role"] != "owner":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    places = [place["name"] for place in database.places.find({})]
    organizers = [organizer["name"] for organizer in database.organizers.find({})]

    template = templates.get_template("pages/parse_quizzes.html")
    content = template.render(user=user, page="parse_quizzes", version=get_static_hash(), places=places, organizers=organizers, year=datetime.now().year)
    return HTMLResponse(content=content)


@router.post("/add-quiz")
def add_quiz(user: Optional[dict] = Depends(get_current_user), quiz_params: QuizAddForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if database.quizzes.find_one({"date": quiz_params.date, "name": quiz_params.name, "place": quiz_params.place, "time": quiz_params.time}):
        return JSONResponse({"status": constants.ERROR, "message": f'Квиз с названием "{quiz_params.name}" в {quiz_params.place} в {quiz_params.time} уже имеется'})

    if not database.places.find_one({"name": quiz_params.place}):
        return JSONResponse({"status": constants.ERROR, "message": f'Места проведения квиза с названием "{quiz_params.place}" не существует'})

    if not database.organizers.find_one({"name": quiz_params.organizer}):
        return JSONResponse({"status": constants.ERROR, "message": f'Организатора квизов с названием "{quiz_params.organizer}" не существует'})

    if quiz_params.position > quiz_params.teams:
        return JSONResponse({"status": constants.ERROR, "message": "Позиция команды не может быть больше, чем количество команд"})

    if quiz_params.players < 0:
        return JSONResponse({"status": constants.ERROR, "message": "Количество игроков команды не может быть отрицательным"})

    quiz = Quiz.from_dict({
        "name": quiz_params.name,
        "short_name": quiz_params.short_name,
        "date": quiz_params.date,
        "time": quiz_params.time,
        "place": quiz_params.place,
        "organizer": quiz_params.organizer,
        "description": quiz_params.description,
        "cost": quiz_params.cost,
        "position": quiz_params.position,
        "teams": quiz_params.teams,
        "players": quiz_params.players
    })

    database.quizzes.insert_one(quiz.to_dict())
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/delete-quiz")
def delete_quiz(user: Optional[dict] = Depends(get_current_user), quiz_id: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.quizzes.find_one({"_id": ObjectId(quiz_id)}):
        return JSONResponse({"status": constants.ERROR, "message": "Выбранного квиза не существует"})

    database.quizzes.delete_one({"_id": ObjectId(quiz_id)})
    database.photo_albums.update_many({"quiz_id": ObjectId(quiz_id)}, {"$set": {"quiz_id": ""}})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/update-quiz")
def update_quiz(user: Optional[dict] = Depends(get_current_user), quiz_params: QuizUpdateForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.quizzes.find_one({"_id": ObjectId(quiz_params.quiz_id)}):
        return JSONResponse({"status": constants.ERROR, "message": "Указанного квиза не существует, возможно, он был удалён ранее"})

    if not database.places.find_one({"name": quiz_params.place}):
        return JSONResponse({"status": constants.ERROR, "message": f'Места проведения квиза с названием "{quiz_params.place}" не существует'})

    if quiz_params.position > quiz_params.teams:
        return JSONResponse({"status": constants.ERROR, "message": "Позиция команды не может быть больше, чем количество команд"})

    if quiz_params.players < 0:
        return JSONResponse({"status": constants.ERROR, "message": "Количество игроков команды не может быть отрицательным"})

    quiz = Quiz.from_dict({
        "name": quiz_params.name,
        "short_name": quiz_params.short_name,
        "date": quiz_params.date,
        "time": quiz_params.time,
        "place": quiz_params.place,
        "organizer": quiz_params.organizer,
        "description": quiz_params.description,
        "cost": quiz_params.cost,
        "position": quiz_params.position,
        "teams": quiz_params.teams,
        "players": quiz_params.players
    })

    database.quizzes.update_one({"_id": ObjectId(quiz_params.quiz_id)}, {"$set": quiz.to_dict()})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/get-vk-post")
def get_vk_post(user: Optional[dict] = Depends(get_current_user), post_id: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    post_text = vk_api.get_post(post_id)

    if post_text is None:
        return JSONResponse({"status": constants.ERROR, "message": "Не удалось получить текст поста"})

    return JSONResponse({"status": constants.SUCCESS, "text": post_text})
