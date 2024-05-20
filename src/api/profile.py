import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import templates
from src.database import database
from src.utils.auth import get_current_user
from src.utils.common import crop_image, get_hash, get_static_hash, save_image

router = APIRouter()


@dataclass
class AvatarForm:
    x: float = Form(...)
    y: float = Form(...)
    size: float = Form(...)
    image: UploadFile = File(...)


@router.get("/profile")
def profile(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/profile")

    games = list(database.quizzes.find({"position": {"$ne": 0}, "participants.username": user["username"]}, {"_id": 0}).sort([("date", -1), ("time", -1)]))
    month2games = defaultdict(int)

    for game in games:
        month2games[(game["date"].year, game["date"].month)] += 1

    month2games = sorted([(year, month, games) for (year, month), games in month2games.items()], key=lambda item: (item[0], item[1]))

    template = templates.get_template("pages/profile.html")
    content = template.render(user=user, page="profile", version=get_static_hash(), games=games, month2games=month2games, month2rus=constants.MONTH_TO_RUS)
    return HTMLResponse(content=content)


@router.post("/update-avatar")
async def update_avatar(params: AvatarForm = Depends(), user: Optional[dict] = Depends(get_current_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не залогинен"})

    image_path = save_image(params.image, os.path.join("web", "images", "profiles", f'{user["username"]}.jpg'))
    crop_image(image_path, params.x, params.y, params.size)
    image_hash = get_hash(image_path)
    image_src = f'/profile-images/{user["username"]}.jpg?v={image_hash}'

    database.users.update_one({"username": user["username"]}, {"$set": {"image_src": image_src}}, upsert=True)
    return JSONResponse({"status": constants.SUCCESS, "src": image_src})
