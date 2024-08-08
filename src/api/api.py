from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import templates
from src.database import database
from src.utils.achievements import get_team_achievements
from src.utils.auth import get_current_user
from src.utils.common import get_analytics, get_schedule, get_smuzi_rating, get_static_hash, get_word_form, parse_date, quiz_to_datetime
from src.utils.place_utils import get_places_dict

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
    smuzi_rating = get_smuzi_rating()
    albums = list(database.photo_albums.find({"deactivated": {"$ne": True}, "quiz_id": {"$ne": ""}, "photos.2": {"$exists": True}}).sort("date", -1).limit(8))

    total_analytics = get_analytics(start_date=None, end_date=None, only_main=True)
    total_analytics["games_text"] = get_word_form(total_analytics["games"], ["игр", "игры", "игру"], only_form=True)
    total_analytics["wins_text"] = get_word_form(total_analytics["wins"], ["раз", "раза", "раз"], only_form=True)
    total_analytics["prizes_text"] = get_word_form(total_analytics["prizes"], ["раз", "раза", "раз"], only_form=True)
    total_analytics["top3_text"] = get_word_form(total_analytics["top3"], ["раз", "раза", "раз"], only_form=True)

    content = template.render(
        user=user,
        page="index",
        version=get_static_hash(),
        schedule=curr_schedule,
        places=get_places_dict(),
        smuzi_rating=smuzi_rating,
        next_quizzes1=next_quizzes1,
        next_quizzes2=next_quizzes2,
        analytics=total_analytics,
        albums=albums
    )
    return HTMLResponse(content=content)


@router.post("/schedule")
def schedule(date: str = Body(..., embed=True)) -> JSONResponse:
    parsed_date = parse_date(date)
    return JSONResponse({
        "status": constants.SUCCESS,
        "schedule": get_schedule(parsed_date),
        "places": get_places_dict()
    })


@router.get("/schedule")
def schedule_get(date: str = Query("")) -> HTMLResponse:
    parsed_date = parse_date(date)
    template = templates.get_template("pages/schedule.html")
    curr_schedule = get_schedule(parsed_date)
    places = get_places_dict()
    content = template.render(user=None, version=get_static_hash(), schedule=curr_schedule, places=places)
    return HTMLResponse(content=content)


@router.get("/analytics")
def analytics(user: Optional[dict] = Depends(get_current_user), start_date: str = Query(""), end_date: str = Query("")) -> Response:
    start_date = None if start_date == "" else parse_date(start_date)
    end_date = None if end_date == "" else parse_date(end_date)

    if start_date and end_date and start_date > end_date:
        start_date, end_date = end_date, start_date

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
        month2rus=constants.MONTH_TO_RUS,
        category2color=constants.CATEGORY2COLOR,
        colors=constants.ANALYTICS_COLORS
    )
    return HTMLResponse(content=content)


@router.get("/achievements")
def achievements(user: Optional[dict] = Depends(get_current_user)) -> Response:
    template = templates.get_template("pages/achievements.html")
    content = template.render(user=user, version=get_static_hash(), achievements=get_team_achievements())
    return HTMLResponse(content=content)
