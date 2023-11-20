import os
from typing import Optional

from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from src.database import database
from src.utils.common import get_static_hash
from src.utils.vkapi import VKApi

templates = Environment(loader=FileSystemLoader("web/templates"), cache_size=0)


with open(os.path.join(os.path.dirname(__file__), "..", "..", "vk_tokens.txt"), "r") as f:
    vk_api = VKApi(f.read().splitlines())


def make_error(message: str, user: Optional[dict], title: str = "Произошла ошибка") -> HTMLResponse:
    template = templates.get_template("pages/error.html")
    settings = database.settings.find_one({"username": user["username"]}) if user else None
    content = template.render(user=user, settings=settings, page="error", error_title=title, message=message, version=get_static_hash())
    return HTMLResponse(content=content)
