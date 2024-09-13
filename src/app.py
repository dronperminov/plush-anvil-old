import os
from contextlib import asynccontextmanager
from typing import AsyncContextManager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn.config import LOGGING_CONFIG

from src.api.achievements import router as achievements_router
from src.api.api import router as api_router
from src.api.auth import router as auth_router
from src.api.organizers import router as organizers_router
from src.api.participants import router as participants_router
from src.api.photos import router as photos_router
from src.api.places import router as places_router
from src.api.profile import router as profile_router
from src.api.quizzes import router as quizzes_router
from src.database import database


def init_routers():
    app.include_router(api_router)
    app.include_router(auth_router)
    app.include_router(profile_router)
    app.include_router(places_router)
    app.include_router(organizers_router)
    app.include_router(quizzes_router)
    app.include_router(participants_router)
    app.include_router(achievements_router)
    app.include_router(photos_router)


def init_static_files():
    app.mount("/styles", StaticFiles(directory="web/styles"))
    app.mount("/js", StaticFiles(directory="web/js"))
    app.mount("/fonts", StaticFiles(directory="web/fonts"))
    app.mount("/images", StaticFiles(directory="web/images"))
    app.mount("/profile-images", StaticFiles(directory="web/images/profiles"))


def init_logging_config():
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    database.connect()
    yield
    database.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=500)

init_routers()
init_static_files()
init_logging_config()
