import os
import re
import urllib.parse
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Body, Depends, File, Form, Query, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates
from src.database import database
from src.dataclasses.album import Album
from src.utils.auth import get_current_user
from src.utils.common import get_static_hash, preview_image, save_image
from src.utils.users import get_markup_users


@dataclass
class AddMarkupForm:
    album_id: int = Body(..., embed=True)
    photo_url: str = Body(..., embed=True)
    username: str = Body(..., embed=True)
    x: float = Body(..., embed=True)
    y: float = Body(..., embed=True)
    width: float = Body(..., embed=True)
    height: float = Body(..., embed=True)


@dataclass
class RemoveMarkupForm:
    album_id: int = Body(..., embed=True)
    photo_url: str = Body(..., embed=True)
    markup_id: str = Body(..., embed=True)


router = APIRouter()


@router.get("/albums")
def get_albums(user: Optional[dict] = Depends(get_current_user)) -> HTMLResponse:
    albums = list(database.photo_albums.find({"deactivated": {"$ne": True}}).sort("date", -1))
    template = templates.get_template("pages/photos.html")
    content = template.render(user=user, page="albums", version=get_static_hash(), albums=albums, quote=urllib.parse.quote)
    return HTMLResponse(content=content)


@router.get("/albums/{album_id}-{title}")
def get_title_album(album_id: int, title: str, user: Optional[dict] = Depends(get_current_user)) -> HTMLResponse:
    album = database.photo_albums.find_one({"album_id": album_id})

    if not album:
        return make_error(message="Запрашиваемый альбом не найден.", user=user)

    if album.get("deactivated"):
        return make_error(message="Запрашиваемый альбом был удалён.", user=user)

    for photo in album["photos"]:
        photo["caption"] = album["title"]

    users = get_markup_users(album.get("quiz_id", ""))
    template = templates.get_template("pages/album.html")
    content = template.render(user=user, page="album", version=get_static_hash(), album=album, users=users, is_owner=user and user["role"] == "owner")
    return HTMLResponse(content=content)


@router.get("/albums/{album_id}")
def get_album(album_id: int, user: Optional[dict] = Depends(get_current_user)) -> Response:
    album = database.photo_albums.find_one({"album_id": album_id})

    if not album:
        return make_error(message="Запрашиваемый альбом не найден.", user=user)

    album = Album.from_dict(album)
    return RedirectResponse(urllib.parse.quote(album.url, safe="/"))


def render_album(user: Optional[dict], title: str, page_name: str, photos: List[dict], is_owner: bool, usernames: Optional[List[str]], only: bool) -> HTMLResponse:
    photos = sorted(photos, key=lambda photo: photo["date"])
    album = Album(title=title, album_id=0, url=f"/{page_name}", photos=photos, date=datetime.now(), quiz_id="", preview_url="")
    users = get_markup_users()
    template = templates.get_template("pages/album.html")
    content = template.render(user=user, page=page_name, version=get_static_hash(), album=album, users=users, is_owner=is_owner, usernames=usernames, only=only)
    return HTMLResponse(content=content)


def get_photos_with_users(usernames: List[str], only: bool) -> List[dict]:
    query = {"deactivated": {"$ne": True}}
    if usernames:
        query["photos.markup.username"] = {"$regex": f'^({"|".join(usernames)})$', "$options": "i"}

    usernames = {username.lower() for username in usernames}
    photos = []

    for album in database.photo_albums.find(query):
        for photo in album["photos"]:
            photo_users = {markup["username"].lower() for markup in photo["markup"]}

            if only and photo_users != usernames:
                continue

            photo["album_id"] = album["album_id"]
            photo["caption"] = album["title"]
            if usernames and usernames.issubset(photo_users) or not usernames and not photo_users:
                photos.append(photo)

    return photos


@router.get("/photos-with-me")
def get_user_photos(user: Optional[dict] = Depends(get_current_user), only: bool = Query(False)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/photos-with-me")

    return render_album(user, "Фото со мной", "photos-with-me", get_photos_with_users([user["username"]], only), False, None, only)


@router.get("/photos-with-users")
def get_users_photos(user: Optional[dict] = Depends(get_current_user), usernames: List[str] = Query([]), only: bool = Query(False)) -> Response:
    if usernames and not database.users.find({"username": {"$in": usernames}}):
        return make_error(f'Не удалось найти ни одного из пользователей среди "{", ".join(usernames)}"', user=user)

    title = f'Фото с {", ".join(usernames)}' if usernames else "Фото без отметок"
    return render_album(user, title, "photos-with-users", get_photos_with_users(usernames, only), False, [username.lower() for username in usernames], only)


@router.get("/photos")
def get_all_photos(user: Optional[dict] = Depends(get_current_user)) -> HTMLResponse:
    albums = database.photo_albums.find({"deactivated": {"$ne": True}})
    photos = []

    for album in albums:
        for photo in album["photos"]:
            photo["album_id"] = album["album_id"]
            photo["caption"] = album["title"]
            photos.append(photo)

    return render_album(user, "Все фото", "photos", photos, user and user["role"] == "owner", None, False)


@router.post("/add-album")
def add_album(user: Optional[dict] = Depends(get_current_user), title: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    album_id = database.photo_albums.count_documents({}) + 1
    album = Album.from_dict({"title": title, "album_id": album_id, "date": datetime.now()})

    database.photo_albums.insert_one(album.to_dict())
    return JSONResponse({"status": constants.SUCCESS, "url": urllib.parse.quote(album.url, safe="/")})


@router.get("/quiz-album/{quiz_id}")
def add_quiz_album(quiz_id: str, user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return make_error(message="Пользователь не авторизован", user=user)

    if user["role"] != "owner":
        return make_error(message="Пользователь не является администратором", user=user)

    quiz = database.quizzes.find_one({"_id": ObjectId(quiz_id)})

    if not quiz:
        return make_error(message="Запрашиваемый квиз не найден", user=user)

    album = database.photo_albums.find_one({"quiz_id": quiz["_id"]})

    if album:
        if album.get("deactivated"):
            database.photo_albums.update_one({"album_id": album["album_id"]}, {"$set": {"deactivated": False}})
        return RedirectResponse(urllib.parse.quote(album["url"], safe="/"))

    album_id = database.photo_albums.count_documents({}) + 1
    title = f'{quiz["name"]} ({quiz["date"].day:02}.{quiz["date"].month:02}.{quiz["date"].year}) {quiz["time"]} {quiz["place"]}'
    hour, minute = quiz["time"].split(":")
    quiz_date = datetime(quiz["date"].year, quiz["date"].month, quiz["date"].day, int(hour), int(minute))

    album = Album.from_dict({"title": title, "album_id": album_id, "date": quiz_date, "quiz_id": quiz["_id"]})
    database.photo_albums.insert_one(album.to_dict())
    return RedirectResponse(urllib.parse.quote(album.url, safe="/"))


@router.post("/remove-album")
def remove_album(user: Optional[dict] = Depends(get_current_user), album_id: int = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.photo_albums.find_one({"album_id": album_id}):
        return JSONResponse({"status": constants.ERROR, "message": "Фотоальбом не найден"})

    database.photo_albums.update_one({"album_id": album_id}, {"$set": {"deactivated": True}})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/rename-album")
def rename_album(user: Optional[dict] = Depends(get_current_user), album_id: int = Body(..., embed=True), title: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.photo_albums.find_one({"album_id": album_id}):
        return JSONResponse({"status": constants.ERROR, "message": "Фотоальбом не найден"})

    database.photo_albums.update_one({"album_id": album_id}, {"$set": {"title": title}})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/set-album-preview")
def set_album_preview(user: Optional[dict] = Depends(get_current_user), album_id: int = Body(..., embed=True), preview_url: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    if not database.photo_albums.find_one({"album_id": album_id}):
        return JSONResponse({"status": constants.ERROR, "message": "Фотоальбом не найден"})

    database.photo_albums.update_one({"album_id": album_id}, {"$set": {"preview_url": preview_url}})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/upload-photo")
def upload_photo(user: Optional[dict] = Depends(get_current_user), album_id: int = Form(...), image: UploadFile = File(...)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
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
    date = album.date if album.quiz_id else datetime.now()

    if photo_src in {photo["url"] for photo in album.photos}:
        return JSONResponse({"status": constants.SUCCESS, "added": False})

    database.photo_albums.update_one({"album_id": album_id}, {"$push": {"photos": {"url": photo_src, "preview_url": photo_preview_src, "markup": [], "date": date}}})

    if not album.preview_url:
        database.photo_albums.update_one({"album_id": album_id}, {"$set": {"preview_url": photo_preview_src}})

    if not album.quiz_id:
        database.photo_albums.update_one({"album_id": album_id}, {"$set": {"date": date}})

    return JSONResponse({"status": constants.SUCCESS, "added": True, "src": photo_src, "preview_src": photo_preview_src})


@router.post("/remove-photo")
def remove_photo(user: Optional[dict] = Depends(get_current_user), album_id: int = Body(..., embed=True), photo_url: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    album = database.photo_albums.find_one({"album_id": album_id})
    if not album:
        return JSONResponse({"status": constants.ERROR, "message": "Фотоальбом не найден"})

    album_path = os.path.join("web", "images", "albums", f"{album_id}")
    filename = os.path.basename(photo_url)

    if not os.path.exists(os.path.join(album_path, filename)):
        return JSONResponse({"status": constants.ERROR, "message": "Изображение не найдено, возможно оно было удалено"})

    os.remove(os.path.join(album_path, filename))
    os.remove(os.path.join(album_path, f"preview_{filename}"))

    photos = [photo for photo in album["photos"] if photo["url"] != photo_url]
    update_data = {"photos": photos}

    if f"preview_{filename}" == os.path.basename(album["preview_url"]):
        update_data["preview_url"] = photos[0]["preview_url"] if photos else ""

    database.photo_albums.update_one({"album_id": album_id}, {"$set": update_data})
    return JSONResponse({"status": constants.SUCCESS})


@router.post("/add-user-markup")
def add_user_markup(user: Optional[dict] = Depends(get_current_user), markup: AddMarkupForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    album = database.photo_albums.find_one({"album_id": markup.album_id})
    if not album:
        return JSONResponse({"status": constants.ERROR, "message": "Фотоальбом не найден"})

    markup.photo_url = re.sub(r"\?v=.*$", "", markup.photo_url)
    photo = [photo for photo in album["photos"] if photo["url"] == markup.photo_url]

    if len(photo) != 1:
        return JSONResponse({"status": constants.ERROR, "message": "Фото не найдено"})

    if "markup" not in photo[0]:
        photo[0]["markup"] = []

    markup_id = str(uuid.uuid1())
    photo[0]["markup"].append({"username": markup.username, "x": markup.x, "y": markup.y, "width": markup.width, "height": markup.height, "markup_id": markup_id})
    database.photo_albums.update_one({"album_id": markup.album_id}, {"$set": {"photos": album["photos"]}})
    return JSONResponse({"status": constants.SUCCESS, "markup_id": markup_id})


@router.post("/remove-user-markup")
def remove_user_markup(user: Optional[dict] = Depends(get_current_user), markup: RemoveMarkupForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не авторизован"})

    if user["role"] != "owner":
        return JSONResponse({"status": constants.ERROR, "message": "Пользователь не является администратором"})

    album = database.photo_albums.find_one({"album_id": markup.album_id})
    if not album:
        return JSONResponse({"status": constants.ERROR, "message": "Фотоальбом не найден"})

    markup.photo_url = re.sub(r"\?v=.*$", "", markup.photo_url)
    photo = [photo for photo in album["photos"] if photo["url"] == markup.photo_url]

    if len(photo) != 1:
        return JSONResponse({"status": constants.ERROR, "message": "Фото не найдено"})

    photo[0]["markup"] = [photo_markup for photo_markup in photo[0].get("markup", []) if photo_markup["markup_id"] != markup.markup_id]
    database.photo_albums.update_one({"album_id": markup.album_id}, {"$set": {"photos": album["photos"]}})
    return JSONResponse({"status": constants.SUCCESS})
