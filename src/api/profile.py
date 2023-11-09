import os
import shutil
import tempfile
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from src import constants
from src.api import templates
from src.database import database
from src.utils.auth import get_current_user
from src.utils.common import get_hash, get_static_hash, save_image

router = APIRouter()


@router.get("/profile")
def profile(user: Optional[dict] = Depends(get_current_user)) -> HTMLResponse:
    template = templates.get_template("pages/profile.html")
    content = template.render(user=user, page="index", version=get_static_hash())
    return HTMLResponse(content=content)


@router.post("/update-avatar")
async def update_avatar(image: UploadFile = File(...), user: Optional[dict] = Depends(get_current_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не залогинен"})

    image_path = save_image(image, os.path.join("web", "images", "profiles", f'{user["username"]}.jpg'))
    image_hash = get_hash(image_path)
    image_src = f'/images/profiles/{user["username"]}.jpg?v={image_hash}'

    database.users.update_one({"username": user["username"]}, {"$set": {"image_src": image_src}}, upsert=True)
    return JSONResponse({"status": constants.SUCCESS, "src": image_src})
