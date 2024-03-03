import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.database import database
from src.utils.common import get_smuzi_rating

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

with open("bot_token.txt", "r") as f:
    token = f.read()

bot = Bot(token=token)
dp = Dispatcher()


@dp.message(Command("start"))
async def handle_start(message: types.Message):
    await message.reply("Привет! Я бот Плюшевой наковальни!")


@dp.message(Command("info"))
async def handle_info(message: types.Message):
    lines = [
        "<b>Общая информация</b>:",
        '- капитан команды: <a href="https://t.me/Sobolyulia">Борисова Юля</a>',
        '- сайт: <a href="https://plush-anvil.ru">plush-anvil.ru</a>',
        '- альбомы с фотографиями: <a href="https://plush-anvil.ru/albums">plush-anvil.ru/albums</a>',
        "",
        "<b>Тренировки:</b>",
        '- сайт с тренировками по УМ: <a href="https://music-quiz.plush-anvil.ru">music-quiz.plush-anvil.ru</a>',
        '- сайт с тренировками по КМС: <a href="https://movie-quiz.plush-anvil.ru">movie-quiz.plush-anvil.ru</a>'
    ]

    await message.reply("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


@dp.message(Command("rating"))
async def handle_rating(message: types.Message):
    rating = get_smuzi_rating()
    await message.reply(f"<b>Рейтинг Смузи</b>: {rating}", parse_mode="HTML")


@dp.message(Command("poll"))
async def handle_poll(message: types.Message):
    logger.info(f"Chat id: {message.chat.id}")
    logger.info(f"Chat title: {message.chat.title}")

    text = re.sub(r"^/poll\s*", "", message.text)
    await message.delete()
    await message.answer_poll(question=text, options=["Пойду", "Не пойду"], is_anonymous=False, allows_multiple_answers=False)


def quiz_to_article_result(quiz: dict, places: Dict[str, dict]) -> InlineQueryResultArticle:
    name, short_name = re.sub(r"\.$", "", quiz["name"]), re.sub(r"\n+", " ", quiz["short_name"])
    date, time, place, cost = quiz["date"], quiz["time"], quiz["place"], quiz["cost"]
    weekday = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][date.weekday()]
    weekday_description = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"][date.weekday()]

    header_date = f"{date.day:02d}.{date.month:02d} {weekday} {time}"
    header_place = f'{place} (м. {places[place]["metro_station"]}) {cost} руб.'

    title = f"{date.day:02d}.{date.month:02d} {name}"
    description = f'{weekday_description}, {time}\n{place} {cost} руб.'
    poll_title = f"{header_date} {name}. {header_place}"

    if len(poll_title) >= 240:
        poll_title = f"{header_date} {short_name}. {header_place}"

    input_content = InputTextMessageContent(message_text=f"/poll {poll_title}")
    return InlineQueryResultArticle(id=f'{quiz["_id"]}', title=title, description=description, input_message_content=input_content)


@dp.inline_query(F.query == "poll")
async def handle_inline(query: InlineQuery):
    logger.info(query.from_user.username)
    today = datetime.now()
    quizzes = list(database.quizzes.find({"date": {"$gte": today, "$lte": today + timedelta(days=7)}}))
    places = {place["name"]: place for place in database.places.find({}, {"_id": 0})}

    results = []

    if query.from_user.username in ["dronperminov", "Sobolyulia", "perminova_sd"]:
        for quiz in quizzes:
            results.append(quiz_to_article_result(quiz, places))

    await query.answer(results, is_personal=False, cache_time=0)


async def main():
    database.connect()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
