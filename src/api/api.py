from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import templates
from src.database import database
from src.utils.auth import get_current_user
from src.utils.common import get_schedule, get_smuzi_rating, get_static_hash, parse_date, quiz_to_datetime

router = APIRouter()


@router.get("/")
def index(user: Optional[dict] = Depends(get_current_user), date: str = Query("")) -> Response:
    parsed_date = parse_date(date)
    today = datetime.now()

    if date and parsed_date.year == today.year and parsed_date.month == today.month:
        return RedirectResponse("/")

    quizzes = [quiz for quiz in database.quizzes.find({}) if quiz_to_datetime(quiz) >= today]
    next_quiz1 = min(quizzes, key=lambda quiz: quiz_to_datetime(quiz) - today, default=None)
    next_quiz2 = min([quiz for quiz in quizzes if quiz_to_datetime(quiz) > quiz_to_datetime(next_quiz1)], key=lambda quiz: quiz_to_datetime(quiz) - today, default=None)
    next_quizzes1 = [quiz for quiz in quizzes if quiz_to_datetime(quiz) == quiz_to_datetime(next_quiz1)] if next_quiz1 else []
    next_quizzes2 = [quiz for quiz in quizzes if quiz_to_datetime(quiz) == quiz_to_datetime(next_quiz2)] if next_quiz2 else []

    template = templates.get_template("pages/index.html")
    curr_schedule = get_schedule(parsed_date)
    places = {place["name"]: place for place in database.places.find({}, {"_id": 0})}
    smuzi_rating = get_smuzi_rating()

    content = template.render(
        user=user,
        page="index",
        version=get_static_hash(),
        schedule=curr_schedule,
        places=places,
        smuzi_rating=smuzi_rating,
        next_quizzes1=next_quizzes1,
        next_quizzes2=next_quizzes2
    )
    return HTMLResponse(content=content)


@router.post("/schedule")
def schedule(date: str = Body(..., embed=True)) -> JSONResponse:
    parsed_date = parse_date(date)
    return JSONResponse({
        "status": constants.SUCCESS,
        "schedule": get_schedule(parsed_date),
        "places": {place["name"]: place for place in database.places.find({}, {"_id": 0})}
    })
