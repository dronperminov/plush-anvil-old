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

admin_usernames = ["dronperminov", "Sobolyulia", "perminova_sd"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

with open("bot_token.txt", "r") as f:
    token = f.read()

bot = Bot(token=token)
dp = Dispatcher()


@dp.message(Command("start"))
async def handle_start(message: types.Message) -> None:
    text = "\n".join([
        "Привет! Я бот Плюшевой наковальни!",
        "",
        "Команды, которые я знаю:",
        "/info - отображение общей информации",
        "/rating - информация о текущем рейтинге Смузи",
        "/remind - напоминание про квиз (необходимо ответить на сообщение с опросом)",
        "",
        "А ещё админы могут создавать опросы про квизы, написав `@plush_anvil_bot poll` и выбрав нужный квиз."
    ])

    await message.reply(text, parse_mode="Markdown")


@dp.message(Command("info"))
async def handle_info(message: types.Message) -> None:
    lines = [
        "<b>Общая информация</b>:",
        '- капитан команды: <a href="https://t.me/Sobolyulia">Борисова Юля</a>',
        '- сайт: <a href="https://plush-anvil.ru">plush-anvil.ru</a>',
        '- фотоальбомы: <a href="https://plush-anvil.ru/albums">plush-anvil.ru/albums</a>',
        "",
        "<b>Тренировки:</b>",
        '- УМ: <a href="https://music-quiz.plush-anvil.ru">music-quiz.plush-anvil.ru</a>',
        '- КМС: <a href="https://movie-quiz.plush-anvil.ru">movie-quiz.plush-anvil.ru</a>'
    ]

    await message.reply("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


@dp.message(Command("rating"))
async def handle_rating(message: types.Message) -> None:
    rating = get_smuzi_rating()
    await message.reply(f"<b>Рейтинг Смузи</b>: {rating}", parse_mode="HTML")


@dp.message(Command("poll"))
async def handle_poll(message: types.Message) -> None:
    logger.info(f"Chat id: {message.chat.id}")
    logger.info(f"Chat title: {message.chat.title}")

    await message.delete()

    if message.from_user.username in admin_usernames:
        title = re.sub(r"^/poll\s*", "", message.text)
        poll = await message.answer_poll(question=title, options=["Пойду", "Не пойду"], is_anonymous=False, allows_multiple_answers=False)
        await poll.pin(disable_notification=True)


def quiz_to_article_result(quiz: dict, places: Dict[str, dict]) -> InlineQueryResultArticle:
    name, short_name = re.sub(r"\.$", "", quiz["name"]), re.sub(r"\n+", " ", quiz["short_name"])
    date, time, place, cost = quiz["date"], quiz["time"], quiz["place"], quiz["cost"]
    weekday = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][date.weekday()]
    weekday_description = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"][date.weekday()]

    header_date = f"{date.day:02d}.{date.month:02d} {weekday} {time}"
    header_place = f'{place} (м. {places[place]["metro_station"]}) {cost} руб.'

    title = f"{date.day:02d}.{date.month:02d} {name}"
    description = f"{weekday_description}, {time}\n{place} {cost} руб."
    poll_title = f"{header_date} {name}. {header_place}"

    if len(poll_title) >= 240:
        poll_title = f"{header_date} {short_name}. {header_place}"

    input_content = InputTextMessageContent(message_text=f"/poll {poll_title}")
    return InlineQueryResultArticle(id=f'{quiz["_id"]}', title=title, description=description, input_message_content=input_content)


@dp.inline_query(F.query == "poll")
async def handle_inline_poll(query: InlineQuery) -> None:
    logger.info(query.from_user.username)
    today = datetime.now()
    quizzes = list(database.quizzes.find({"date": {"$gte": today, "$lte": today + timedelta(days=7)}}))
    places = {place["name"]: place for place in database.places.find({}, {"_id": 0})}

    results = []

    if query.from_user.username in admin_usernames:
        for quiz in quizzes:
            results.append(quiz_to_article_result(quiz, places))

    await query.answer(results, is_personal=False, cache_time=0)


@dp.inline_query(F.query == "info")
async def handle_inline_info(query: InlineQuery) -> None:
    logger.info(query.from_user.username)
    rating = get_smuzi_rating()

    items = [
        {"title": "Сайт", "description": "plush-anvil.ru", "text": "<b>Сайт</b>: plush-anvil.ru"},
        {"title": "Рейтинг смузи", "description": f"{rating}", "text": f"<b>Рейтинг смузи</b>: {rating}"},
        {"title": "УМ тренировки", "description": "music-quiz.plush-anvil.ru", "text": "<b>Сайт для УМ тренировок</b>: music-quiz.plush-anvil.ru"},
        {"title": "КМС тренировки", "description": "movie-quiz.plush-anvil.ru", "text": "<b>Сайт для КМС тренировок</b>: movie-quiz.plush-anvil.ru"}
    ]

    results = []

    for i, item in enumerate(items):
        content = InputTextMessageContent(message_text=item["text"], parse_mode="HTML")
        result = InlineQueryResultArticle(id=f"info_{i}", title=item["title"], description=item["description"], input_message_content=content)
        results.append(result)

    await query.answer(results, is_personal=False, cache_time=0)


@dp.message(Command("remind"))
async def handle_remind(message: types.Message) -> None:
    if not message.reply_to_message or not message.reply_to_message.poll:
        await message.delete()
        await message.answer(text="Для напоминания необходимо ответить на сообщение с опросом")
        return

    poll = message.reply_to_message.poll
    match = re.search(r"^(?P<day>\d+)\.(?P<month>\d+) [ПВСЧ][нтрбс] (?P<time>\d+:\d+) (?P<name>.*)\. (?P<place>.*) \(м\. [^)]+\) (?P<cost>\d+) руб.", poll.question)

    if match is None:
        await message.delete()
        await message.answer(text="Похоже, опрос не соответствует описанию квиза")
        return

    day, month, time, name, place = int(match.group("day")), int(match.group("month")), match.group("time"), match.group("name"), match.group("place")
    today = datetime.now()

    if today.day != day or today.month != month:
        await message.delete()
        await message.answer(text=f'Слишком рано для напоминания. Квиз "{name}" будет не сегодня, а {day:02d}.{month:02d}')
        return

    text = f'Напоминаю, что сегодня квиз "{name}" в <b>{time}</b>.\n<b>Место проведения</b>: {place}'
    await message.delete()
    await message.answer(text=text, parse_mode="HTML", reply_to_message_id=message.reply_to_message.message_id)


async def main() -> None:
    database.connect()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
