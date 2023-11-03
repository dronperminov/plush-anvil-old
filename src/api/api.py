from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from src.api import templates
from src.utils.auth import get_current_user
from src.utils.common import get_calendar, get_static_hash

router = APIRouter()


@router.get("/")
def index(user: Optional[dict] = Depends(get_current_user)) -> HTMLResponse:
    template = templates.get_template("pages/index.html")
    calendar = get_calendar()

    content = template.render(user=user, page="index", version=get_static_hash(), calendar=calendar)
    return HTMLResponse(content=content)
