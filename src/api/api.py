from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from src.api import templates
from src.database import database
from src.utils.auth import get_current_user
from src.utils.common import get_schedule, get_static_hash, parse_date, quiz_to_datetime

router = APIRouter()


@router.get("/")
def index(user: Optional[dict] = Depends(get_current_user), date: str = Query("")) -> Response:
    parsed_date = parse_date(date)
    today = datetime.now()

    if date and parsed_date.year == today.year and parsed_date.month == today.month:
        return RedirectResponse("/")

    prev_quiz = min([quiz for quiz in database.quizzes.find({}) if quiz_to_datetime(quiz) <= today], key=lambda quiz: today - quiz_to_datetime(quiz))
    next_quiz = min([quiz for quiz in database.quizzes.find({}) if quiz_to_datetime(quiz) >= today], key=lambda quiz: quiz_to_datetime(quiz) - today)

    template = templates.get_template("pages/index.html")
    schedule = get_schedule(parsed_date)
    places = {place["name"]: place for place in database.places.find({})}

    content = template.render(user=user, page="index", version=get_static_hash(), schedule=schedule, places=places, prev_quiz=prev_quiz, next_quiz=next_quiz)
    return HTMLResponse(content=content)
