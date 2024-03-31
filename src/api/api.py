from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import templates
from src.database import database
from src.utils.auth import get_current_user
from src.utils.common import get_analytics, get_places, get_schedule, get_smuzi_rating, get_static_hash, parse_date, quiz_to_datetime

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
        "places": get_places()
    })


@router.get("/schedule")
def schedule_get() -> HTMLResponse:
    parsed_date = parse_date("")
    template = templates.get_template("pages/schedule.html")
    curr_schedule = get_schedule(parsed_date)
    places = {place["name"]: place for place in database.places.find({}, {"_id": 0})}
    content = template.render(user=None, version=get_static_hash(), schedule=curr_schedule, places=places)
    return HTMLResponse(content=content)


@router.get("/analytics")
def analytics(user: Optional[dict] = Depends(get_current_user), start_date: str = Query(""), end_date: str = Query("")) -> Response:
    start_date = None if start_date == "" else parse_date(start_date)
    end_date = None if end_date == "" else parse_date(end_date)
    analytics_data = get_analytics(start_date, end_date)

    today = datetime.now()
    dates = {
        "last-year": [datetime(today.year - 1, 1, 1).strftime("%Y-%m-%d"), datetime(today.year - 1, 12, 31).strftime("%Y-%m-%d")],
        "year": [datetime(today.year, 1, 1).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")],
        "month": [datetime(today.year, today.month, 1).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")]
    }

    template = templates.get_template("pages/analytics.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        start_date=start_date,
        end_date=end_date,
        data=analytics_data,
        dates=dates,
        categories=constants.CATEGORIES,
        month2rus=constants.MONTH_TO_RUS
    )
    return HTMLResponse(content=content)
