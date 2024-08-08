from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates
from src.database import database
from src.utils.achievements import get_handle_user_achievements
from src.utils.auth import get_current_user
from src.utils.common import get_static_hash
from src.utils.users import get_participant_users

router = APIRouter()


@dataclass
class AddAchievementForm:
    date: datetime = Body(..., embed=True)
    achievement_id: str = Body(..., embed=True)
    usernames: List[str] = Body(..., embed=True)
    action: str = Body(..., embed=True)


@router.get("/achievements-info")
def achievements_info(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/achievements-info")

    if user["role"] != "owner":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    user_achievements = []

    for user_achievement in database.users.find({"achievements.0": {"$exists": True}}):
        user_achievement["achievements"] = get_handle_user_achievements(username=user_achievement["username"])
        user_achievements.append(user_achievement)

    template = templates.get_template("admin_pages/achievements.html")
    content = template.render(
        user=user,
        page="achievements",
        version=get_static_hash(),
        user_achievements=user_achievements,
        achievements=constants.HANDLE_ACHIEVEMENTS,
        users=get_participant_users(),
        today=datetime.now()
    )

    return HTMLResponse(content=content)


@router.post("/set-achievements")
def set_achievements(user: Optional[dict] = Depends(get_current_user), params: AddAchievementForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if params.action not in ["add", "remove"]:
        return JSONResponse({"status": constants.ERROR, "message": 'Поддерживаются только действия "add" и "remove"'})

    if params.achievement_id not in {achievement["id"] for achievement in constants.HANDLE_ACHIEVEMENTS}:
        return JSONResponse({"status": constants.ERROR, "message": f'Неизвестный тип достижения "{params.achievement_id}"'})

    for username in params.usernames:
        if database.users.find_one({"username": username}) is None:
            return JSONResponse({"status": constants.ERROR, "message": f'Участник с ником "@{username}" отсутствует в базе'})

    for username in params.usernames:
        user = database.users.find_one({"username": username}, {"achievements": 1})
        achievements = user.get("achievements", [])

        if params.action == "add":
            achievements.append({"achievement_id": params.achievement_id, "date": params.date})
        else:
            achievements = [achievement for achievement in achievements if achievement["achievement_id"] != params.achievement_id or achievement["date"] != params.date]

        database.users.update_one({"username": username}, {"$set": {"achievements": achievements}})

    return JSONResponse({"status": constants.SUCCESS})
