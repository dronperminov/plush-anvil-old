import os
from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates
from src.database import database
from src.dataclasses.album import Album
from src.utils.auth import get_current_user
from src.utils.common import get_static_hash, is_landscape_image, preview_image, save_image

router = APIRouter()


@router.get("/photos")
def get_photos(user: Optional[dict] = Depends(get_current_user)) -> HTMLResponse:
    albums = list(database.photo_albums.find({}).sort("datetime", -1))
    template = templates.get_template("pages/photos.html")
    content = template.render(user=user, page="photos", version=get_static_hash(), albums=albums)
    return HTMLResponse(content=content)


@router.get("/albums/{album_id}-{title:path}")
def get_album(album_id: int, title: str, user: Optional[dict] = Depends(get_current_user)) -> HTMLResponse:
    album = database.photo_albums.find_one({"album_id": album_id})

    if not album:
        return make_error(message="Запрашиваемый альбом не найден.", user=user)

    template = templates.get_template("pages/album.html")
    content = template.render(user=user, page="album", version=get_static_hash(), album=album)
    return HTMLResponse(content=content)


@router.post("/add-album")
def add_album(user: Optional[dict] = Depends(get_current_user), title: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "admin":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if database.photo_albums.find_one({"title": title}):
        return JSONResponse({"status": constants.ERROR, "message": f'Фотоальбом с названием "{title}" уже имеется'})

    album_id = database.photo_albums.count_documents({}) + 1
    album = Album.from_dict({"title": title, "album_id": album_id, "datetime": datetime.now()})

    database.photo_albums.insert_one(album.to_dict())
    return JSONResponse({"status": constants.SUCCESS, "url": album.url})


@router.get("/quiz-album/{quiz_id}")
def add_quiz_album(quiz_id: str, user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return make_error(message="Пользователь не авторизован", user=user)

    if user["role"] != "admin":
        return make_error(message="Пользователь не является администратором", user=user)

    quiz = database.quizzes.find_one({"_id": ObjectId(quiz_id)})

    if not quiz:
        return make_error(message="Запрашиваемый квиз не найден", user=user)

    album = database.photo_albums.find_one({"quiz_id": quiz["_id"]})

    if album:
        return RedirectResponse(album["url"])

    album_id = database.photo_albums.count_documents({}) + 1
    title = f'{quiz["name"]} ({quiz["date"].day:02}.{quiz["date"].month:02}.{quiz["date"].year}) {quiz["time"]} {quiz["place"]}'
    album = Album.from_dict({"title": title, "album_id": album_id, "datetime": datetime.now(), "quiz_id": quiz["_id"]})

    database.photo_albums.insert_one(album.to_dict())
    return RedirectResponse(album.url)


@router.post("/upload-photo")
def upload_photo(user: Optional[dict] = Depends(get_current_user), album_id: int = Form(...), image: UploadFile = File(...)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "admin":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    album = database.photo_albums.find_one({"album_id": album_id})

    if not album:
        return JSONResponse({"status": constants.ERROR, "message": "Запрашиваемый альбом не найден"})

    album = Album.from_dict(album)
    album_path = os.path.join("web", "images", "albums", f"{album_id}")
    os.makedirs(album_path, exist_ok=True)

    photo_path = save_image(image, album_path)
    preview_image(photo_path, os.path.join(album_path, f"preview_{os.path.basename(photo_path)}"))

    photo_src = f"/images/albums/{album_id}/{os.path.basename(photo_path)}"
    photo_preview_src = f"/images/albums/{album_id}/preview_{os.path.basename(photo_path)}"

    if photo_src in {photo["url"] for photo in album.photos}:
        return JSONResponse({"status": constants.SUCCESS, "added": False})

    database.photo_albums.update_one({"album_id": album_id}, {"$push": {"photos": {"url": photo_src, "preview_url": photo_preview_src}}})

    if not album.preview_url and is_landscape_image(photo_path):
        database.photo_albums.update_one({"album_id": album_id}, {"$set": {"preview_url": photo_preview_src}})

    return JSONResponse({"status": constants.SUCCESS, "added": True, "src": photo_src, "preview_src": photo_preview_src})
