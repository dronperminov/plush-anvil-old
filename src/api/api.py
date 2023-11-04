from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from src.api import templates
from src.database import database
from src.utils.auth import get_current_user
from src.utils.common import get_schedule, get_static_hash

router = APIRouter()


@router.get("/")
def index(user: Optional[dict] = Depends(get_current_user)) -> HTMLResponse:
    template = templates.get_template("pages/index.html")
    schedule = get_schedule()
    place2color = {place["name"]: place["color"] for place in database.places.find({})}
    print(place2color)

    content = template.render(user=user, page="index", version=get_static_hash(), schedule=schedule, place2color=place2color)
    return HTMLResponse(content=content)
