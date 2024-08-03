from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates
from src.database import database
from src.utils.auth import get_current_user
from src.utils.common import get_static_hash
from src.utils.participants import get_participants_info
from src.utils.users import get_participant_users

router = APIRouter()


@dataclass
class QuizParticipantsForm:
    quiz_id: str = Body(..., embed=True)
    participants: List[dict] = Body(..., embed=True)
    ignore_participants: bool = Body(..., embed=True)


@dataclass
class AddParticipantInfoForm:
    date: datetime = Body(..., embed=True)
    participants: List[dict] = Body(..., embed=True)
    action: str = Body(..., embed=True)


@router.get("/quiz-participants")
def quiz_participants(user: Optional[dict] = Depends(get_current_user), quiz_id: str = Query(...)) -> Response:
    if not user:
        return RedirectResponse(url=f"/login?back_url=/quiz-participants%3Fquiz_id={quiz_id}")

    if user["role"] != "owner":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    try:
        quiz = database.quizzes.find_one({"_id": ObjectId(quiz_id)})
    except InvalidId:
        return make_error(message="Указанного квиза не существует.", user=user)

    if quiz is None:
        return make_error(message="Указанного квиза не существует.", user=user)

    template = templates.get_template("pages/quiz_participants.html")
    content = template.render(user=user, page="quiz_participants", version=get_static_hash(), quiz=quiz, users=get_participant_users())

    return HTMLResponse(content=content)


@router.get("/participants-info")
def participants_info(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/participants-info")

    if user["role"] != "owner":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    participants = get_participants_info()
    today = datetime.now()

    template = templates.get_template("admin_pages/participants_info.html")
    content = template.render(user=user, page="participants_info", version=get_static_hash(), participants=participants, users=get_participant_users(), today=today)

    return HTMLResponse(content=content)


@router.post("/update-quiz-participants")
def update_quiz_participants(user: Optional[dict] = Depends(get_current_user), params: QuizParticipantsForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.quizzes.find_one({"_id": ObjectId(params.quiz_id)}):
        return JSONResponse({"status": constants.ERROR, "message": "Указанного квиза не существует, возможно, он был удалён ранее"})

    for participant in params.participants:
        username = participant["username"]

        if database.users.find_one({"username": username}) is None:
            return JSONResponse({"status": constants.ERROR, "message": f'Участник с ником "@{username}" отсутствует в базе'})

        try:
            count = int(participant["count"])
        except ValueError:
            count = 0

        if count < 1 or count > 100:
            return JSONResponse({"status": constants.ERROR, "message": f'Количество проходок участника с ником "@{username}" задано некорректно ({count})'})

    database.quizzes.update_one({"_id": ObjectId(params.quiz_id)}, {"$set": {"participants": params.participants, "ignore_participants": params.ignore_participants}})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/set-participant-info")
def set_participant_info(user: Optional[dict] = Depends(get_current_user), params: AddParticipantInfoForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if params.action not in ["add", "remove"]:
        return JSONResponse({"status": constants.ERROR, "message": 'Поддерживаются только действия "add" и "remove"'})

    for participant in params.participants:
        username, count = participant["username"], participant["count"]

        try:
            count = int(count)
        except ValueError:
            count = 0

        if count < 1 or count > 100:
            return JSONResponse({"status": constants.ERROR, "message": f'Количество проходок участника с ником "@{username}" задано некорректно ({count})'})

        if database.users.find_one({"username": username}) is None:
            return JSONResponse({"status": constants.ERROR, "message": f'Участник с ником "@{username}" отсутствует в базе'})

    for participant in params.participants:
        user = database.users.find_one({"username": participant["username"]}, {"participant_dates": 1})
        participant_dates = user.get("participant_dates", [])

        if params.action == "add":
            participant_dates.extend([params.date] * participant["count"])
        else:
            without_date = [date for date in participant_dates if date != params.date]
            count = max(0, len([date for date in participant_dates if date == params.date]) - participant["count"])
            participant_dates = without_date + [params.date] * count

        database.users.update_one({"username": participant["username"]}, {"$set": {"participant_dates": participant_dates}})

    return JSONResponse({"status": constants.SUCCESS})
