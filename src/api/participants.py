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
from src.utils.common import get_static_hash, get_word_form
from src.utils.users import get_participant_users

router = APIRouter()


@dataclass
class QuizParticipantsForm:
    quiz_id: str = Body(..., embed=True)
    participants: List[dict] = Body(..., embed=True)


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

    users = {user["username"]: user for user in database.users.find({})}
    user2games = {username: [] for username in users}

    for quiz in database.quizzes.find({"organizer": "Смузи", "participants": {"$exists": True}, "date": {"$gte": datetime(2024, 4, 1)}}):
        for participant in quiz["participants"]:
            if not users[participant["username"]].get("ignore_paid", False):
                user2games[participant["username"]].append({"date": quiz["date"], "time": quiz["time"], "paid": participant["paid"]})

    participants = []

    for username, games in user2games.items():
        if len(games) == 0:
            continue

        games = sorted(games, key=lambda game: (game["date"], game["time"]))
        paid_games = len(games) - 1 - max([i for i, game in enumerate(games) if not game["paid"]], default=-1)
        participants.append({**users[username], "games": games[::-1], "paid_games": paid_games, "paid_games_text": get_word_form(paid_games, ["игр", "игры", "игра"])})

    participants = sorted(participants, key=lambda participant: -participant["paid_games"])

    template = templates.get_template("pages/participants_info.html")
    content = template.render(user=user, page="participants_info", version=get_static_hash(), participants=participants)

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
        if database.users.find_one({"username": participant["username"]}) is None:
            return JSONResponse({"status": constants.ERROR, "message": f'Участник с ником "@{participant["username"]}" отсутствует в базе'})

    database.quizzes.update_one({"_id": ObjectId(params.quiz_id)}, {"$set": {"participants": params.participants}})
    return JSONResponse({"status": constants.SUCCESS})
