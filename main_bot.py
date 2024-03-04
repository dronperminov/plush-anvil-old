import asyncio
import json
import logging
import os
import re
import tempfile
import urllib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

import cv2
import numpy as np
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from bson import ObjectId
from bson.errors import InvalidId

from src.database import database
from src.dataclasses.quiz import Quiz
from src.utils.common import get_places, get_smuzi_rating

admin_usernames = ["dronperminov", "Sobolyulia", "perminova_sd"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

with open("bot_config.json", "r") as f:
    config = json.load(f)

target_group_id = config["group_id"]
bot = Bot(token=config["token"])
dp = Dispatcher()


def parse_quiz_from_id(quiz_id: str) -> Optional[Quiz]:
    try:
        quiz = database.quizzes.find_one({"_id": ObjectId(quiz_id)})
        return None if quiz is None else Quiz.from_dict(quiz)
    except InvalidId:
        return None


async def send_error(message: types.Message, text: str, delete_message: bool = False, **kwargs: dict) -> None:
    if delete_message:
        await message.delete()

    error = await message.answer(text, **kwargs)
    await asyncio.sleep(5)
    await error.delete()


@dp.message(Command("get_id"))
async def log(message: types.Message) -> None:
    logger.info(f"Chat id: {message.chat.id}")
    logger.info(f"Chat title: {message.chat.title}")
    logger.info(f"Chat type: {message.chat.type}")
    await message.delete()


@dp.message(Command("start"))
async def handle_start(message: types.Message) -> None:
    text = "\n".join([
        "Привет! Я бот Плюшевой наковальни!",
        "",
        "Команды, которые я знаю:",
        "/info - отображение общей информации",
        "/rating - информация о текущем рейтинге Смузи",
        "/remind - напоминание про квиз (если в этот день есть квизы)",
        "",
        "А ещё админы могут:",
        "- создавать опросы про квизы, написав `@plush_anvil_bot poll` и выбрав нужный квиз"
        "- создавать картинки с описанием для сториз, написав `@plush_anvil_bot story` и выбрав нужный квиз"
    ])

    await message.delete()
    await message.answer(text, parse_mode="Markdown")


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

    await message.delete()
    await message.answer("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


@dp.message(Command("rating"))
async def handle_rating(message: types.Message) -> None:
    rating = get_smuzi_rating()
    await message.delete()
    await message.answer(f"<b>Рейтинг Смузи</b>: {rating}", parse_mode="HTML")


@dp.message(Command("poll"))
async def handle_poll(message: types.Message) -> None:
    if message.chat.id != target_group_id:
        return await send_error(message, "Команда poll недоступна для этого чата", delete_message=True)

    if message.from_user.username not in admin_usernames:
        return await send_error(message, f"Команда poll недоступна для пользователя @{message.from_user.username}", delete_message=True)

    quiz_id = re.sub(r"^/poll\s*", "", message.text)
    quiz = parse_quiz_from_id(quiz_id)

    if quiz is None:
        return await send_error(message, f'Не удалось найти заданный квиз ("{quiz_id}")', delete_message=True)

    if tg_message := database.tg_quiz_messages.find_one({"quiz_id": ObjectId(quiz_id)}):
        return await send_error(message, "Опрос с этим квизом уже создан", delete_message=True, reply_to_message_id=tg_message["message_id"])

    await message.delete()
    places = get_places()
    poll = await message.answer_poll(question=quiz.to_poll_title(places), options=["Пойду", "Не пойду"], is_anonymous=False, allows_multiple_answers=False)
    poll_url = poll.get_url()

    if poll_url and re.fullmatch(r"https://t.me/c/\d+/\d+", poll_url):
        database.tg_quiz_messages.insert_one({"quiz_id": ObjectId(quiz_id), "message_id": int(poll_url.split("/")[-1]), "url": poll_url})

    await poll.pin(disable_notification=True)


@dp.message(Command("story"))
async def handle_story(message: types.Message) -> None:
    if message.chat.id != target_group_id:
        return await send_error(message, "Команда story недоступна для этого чата", delete_message=True)

    quiz_ids = re.split(r",\s+", re.sub(r"^/story\s*", "", message.text))
    quizzes = [parse_quiz_from_id(quiz_id) for quiz_id in quiz_ids]

    if none_quizzes := [f'"{quiz_id}"' for quiz_id, quiz in zip(quiz_ids, quizzes) if quiz is None]:
        return await send_error(message, f'Не удалось найти некоторые квизы ({", ".join(none_quizzes)})', delete_message=True)

    quiz_ids = [ObjectId(quiz_id) for quiz_id in quiz_ids]
    tg_messages = {tg_info["quiz_id"]: tg_info for tg_info in database.tg_quiz_messages.find({"quiz_id": {"$in": quiz_ids}})}

    if none_messages := [f'- "{quiz.to_inline_title()}"' for quiz_id, quiz in zip(quiz_ids, quizzes) if quiz_id not in tg_messages]:
        none_text = "\n".join(none_messages)
        return await send_error(message, f"Не удалось найти опросы для следующих квизов:\n{none_text}", delete_message=True)

    caption = "\n".join([f'{quiz.name}: {tg_messages[quiz_id]["url"]}' for quiz_id, quiz in zip(quiz_ids, quizzes)])

    # TODO: generate image for quizzes
    image = np.zeros((1920, 1080, 3), dtype=np.uint8)
    cv2.rectangle(image, (40, 40), (800, 800), (0, 0, 255), 10)
    cv2.rectangle(image, (280, 80), (1040, 840), (255, 0, 0), 10)

    with tempfile.TemporaryDirectory() as tmp_dir:
        cv2.imwrite(os.path.join(tmp_dir, "story.png"), image)
        photo_file = FSInputFile(os.path.join(tmp_dir, "story.png"))

        await message.delete()
        await bot.send_document(chat_id=message.from_user.id, document=photo_file, caption=caption)


@dp.message(Command("remind"))
async def handle_remind(message: types.Message) -> None:
    if message.chat.id != target_group_id:
        return await send_error(message, "Команда remind недоступна для этого чата", delete_message=True)

    today = datetime.now()
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59)
    quizzes = list(database.quizzes.find({"date": {"$gte": today, "$lte": end_date}}))

    if not quizzes:
        return await send_error(message, "Слишком рано для напоминания, сегодня нет никаких квизов", delete_message=True)

    messages = {message["quiz_id"]: message for message in database.tg_quiz_messages.find({"quiz_id": {"$in": [quiz["_id"] for quiz in quizzes]}})}
    await message.delete()

    if len(quizzes) == 1:
        quiz = quizzes[0]
        lines = [
            f'Напоминаю, что сегодня квиз "{quiz["name"]}" в <b>{quiz["time"]}</b>',
            f'<b>Место проведения</b>: {quiz["place"]}',
            f'<b>Стоимость</b>: {quiz["cost"]} руб\n',
            "Если ваши планы изменились, переголосуйте, пожалуйста"
        ]

        kwargs = {"reply_to_message_id": messages[quiz["_id"]]["message_id"]} if quiz["_id"] in messages else {}
        await message.answer(text="\n".join(lines), parse_mode="HTML", **kwargs)
    else:
        lines = ["Напоминаю, что сегодня проходят следующие квизы:\n"]
        for quiz in quizzes:
            name = f'<a href="{messages[quiz["_id"]]["url"]}">{quiz["name"]}</a>' if quiz["_id"] in messages else quiz["name"]
            lines.append(f'- {name} в <b>{quiz["time"]}</b>\n<b>Место проведения</b>: {quiz["place"]}\n<b>Стоимость</b>: {quiz["cost"]} руб\n')

        lines.append("Если ваши планы изменились, переголосуйте, пожалуйста")
        await message.answer(text="\n".join(lines), parse_mode="HTML")


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


@dp.inline_query(F.query == "poll")
async def handle_inline_poll(query: InlineQuery) -> None:
    logger.info(query.from_user.username)

    if query.from_user.username not in admin_usernames:
        return

    today = datetime.now()
    start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_date = start_date + timedelta(days=7)
    results = []

    quizzes = list(database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}))
    created_ids = {message["quiz_id"] for message in database.tg_quiz_messages.find({"quiz_id": {"$in": [quiz["_id"] for quiz in quizzes]}})}

    for quiz in quizzes:
        if quiz["_id"] in created_ids:
            continue

        quiz_id = str(quiz["_id"])
        quiz = Quiz.from_dict(quiz)

        results.append(InlineQueryResultArticle(
            id=quiz_id,
            title=quiz.to_inline_title(),
            description=quiz.to_inline_description(),
            input_message_content=InputTextMessageContent(message_text=f"/poll {quiz_id}"),
            thumbnail_url=f"https://plush-anvil.ru/images/organizers/{urllib.parse.quote(quiz.organizer)}.png",
            thumbnail_height=180,
            thumbnail_width=180
        ))

    await query.answer(results, is_personal=False, cache_time=0)


@dp.inline_query(F.query == "story")
async def handle_inline_story(query: InlineQuery) -> None:
    logger.info(query.from_user.username)
    today = datetime.now()
    start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59) + timedelta(days=7)
    results = []

    date2quizzes = defaultdict(list)

    for quiz in database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}):
        date2quizzes[f'{quiz["date"].day:02d}.{quiz["date"].month:02d}'].append(quiz)

    for i, (date, date_quizzes) in enumerate(date2quizzes.items()):
        quiz_ids = ", ".join([str(quiz["_id"]) for quiz in date_quizzes])
        date_quizzes = [Quiz.from_dict(quiz) for quiz in date_quizzes]
        description = "\n".join(f"{quiz.name} ({quiz.place}, {quiz.time})" for quiz in date_quizzes)

        input_content = InputTextMessageContent(message_text=f"/story {quiz_ids}")
        results.append(InlineQueryResultArticle(id=f"story_{i}", title=date, description=description, input_message_content=input_content))

    await query.answer(results, is_personal=False, cache_time=0)


async def main() -> None:
    database.connect()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
