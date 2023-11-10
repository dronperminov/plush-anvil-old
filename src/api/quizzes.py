from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates
from src.database import database
from src.dataclasses.quiz import Quiz
from src.utils.auth import get_current_user
from src.utils.common import get_static_hash, parse_date

router = APIRouter()


@dataclass
class QuizAddForm:
    name: str = Body(..., embed=True)
    date: datetime = Body(..., embed=True)
    time: str = Body(..., embed=True)
    place: str = Body(..., embed=True)
    organizer: str = Body(..., embed=True)
    description: str = Body(..., embed=True)
    cost: int = Body(..., embed=True)


@dataclass
class QuizDeleteForm:
    name: str = Body(..., embed=True)
    date: datetime = Body(..., embed=True)
    place: str = Body(..., embed=True)


@dataclass
class QuizUpdateForm(QuizAddForm):
    original_name: str = Body(..., embed=True)
    original_place: str = Body(..., embed=True)


@router.get("/quizzes/{date}")
def get_quizzes(date: str, user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url=f"/login?back_url=/quizzes/{date}")

    if user["role"] != "admin":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    date = parse_date(date)
    weekday = constants.WEEKDAY_TO_RUS[date.weekday()]

    template = templates.get_template("pages/quizzes.html")
    places = [place["name"] for place in database.places.find({})]
    organizers = [organizer["name"] for organizer in database.organizers.find({})]
    quizzes = [Quiz.from_dict(quiz) for quiz in database.quizzes.find({"date": date})]

    content = template.render(user=user, page="quizzes", version=get_static_hash(), quizzes=quizzes, places=places, organizers=organizers, date=date, weekday=weekday)
    return HTMLResponse(content=content)


@router.get("/parse-quizzes")
def parse_quizzes(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/parse-quizzes")

    if user["role"] != "admin":
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

    if user["role"] != "admin":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if database.quizzes.find_one({"date": quiz_params.date, "name": quiz_params.name, "place": quiz_params.place}):
        return JSONResponse({"status": constants.ERROR, "message": f'Квиз с названием "{quiz_params.name}" в {quiz_params.place} уже имеется'})

    if not database.places.find_one({"name": quiz_params.place}):
        return JSONResponse({"status": constants.ERROR, "message": f'Места проведения квиза с названием "{quiz_params.place}" не существует'})

    if not database.organizers.find_one({"name": quiz_params.organizer}):
        return JSONResponse({"status": constants.ERROR, "message": f'Организатора квизов с названием "{quiz_params.place}" не существует'})

    quiz = Quiz.from_dict({
        "name": quiz_params.name,
        "date": quiz_params.date,
        "time": quiz_params.time,
        "place": quiz_params.place,
        "organizer": quiz_params.organizer,
        "description": quiz_params.description,
        "cost": quiz_params.cost
    })

    database.quizzes.insert_one(quiz.to_dict())
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/delete-quiz")
def delete_quiz(user: Optional[dict] = Depends(get_current_user), quiz_params: QuizDeleteForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "admin":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.quizzes.find_one({"date": quiz_params.date, "name": quiz_params.name, "place": quiz_params.place}):
        return JSONResponse({"status": constants.ERROR, "message": f'Квиза с названием "{quiz_params.name}" в {quiz_params.place} не существует'})

    # TODO: возможно, нужно будет удалять что-то ещё, например, фотки?
    database.quizzes.delete_one({"date": quiz_params.date, "name": quiz_params.name, "place": quiz_params.place})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/update-quiz")
def update_quiz(user: Optional[dict] = Depends(get_current_user), quiz_params: QuizUpdateForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "admin":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.quizzes.find_one({"date": quiz_params.date, "name": quiz_params.original_name, "place": quiz_params.original_place}):
        return JSONResponse({"status": constants.ERROR, "message": f'Квиза с названием "{quiz_params.original_name}" в {quiz_params.original_place} нет'})

    if not database.places.find_one({"name": quiz_params.place}):
        return JSONResponse({"status": constants.ERROR, "message": f'Места проведения квиза с названием "{quiz_params.place}" не существует'})

    quiz = Quiz.from_dict({
        "name": quiz_params.name,
        "date": quiz_params.date,
        "time": quiz_params.time,
        "place": quiz_params.place,
        "organizer": quiz_params.organizer,
        "description": quiz_params.description,
        "cost": quiz_params.cost
    })

    database.quizzes.update_one({"date": quiz_params.date, "name": quiz_params.original_name, "place": quiz_params.original_place}, {"$set": quiz.to_dict()})
    return JSONResponse({"status": constants.SUCCESS})
