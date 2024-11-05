import asyncio
import calendar
import json
import logging
import os
import re
import tempfile
import urllib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import aioschedule as aioschedule
import cv2
import numpy as np
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile, InlineQuery, InlineQueryResultArticle, InputMediaPhoto, InputTextMessageContent
from bson import ObjectId
from bson.errors import InvalidId
from html2image import Html2Image

from src import constants
from src.api import templates
from src.database import database
from src.dataclasses.quiz import Quiz
from src.utils.common import get_month_dates, get_smuzi_rating, get_word_form
from src.utils.place_utils import get_places_dict

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


async def unpin_old_polls() -> None:
    tg_messages = list(database.tg_quiz_messages.find({}))
    tg_quiz_ids = [tg_message["quiz_id"] for tg_message in tg_messages]
    today = datetime.now()
    end_date = datetime(today.year, today.month, today.day, 0, 0, 0)

    safe_quiz_ids = [quiz["_id"] for quiz in database.quizzes.find({"_id": {"$in": tg_quiz_ids}, "date": {"$gte": end_date}}, {"_id": 1})]
    logger.info(f"Start unpin polls (save quiz with date >= {end_date.day:02d}.{end_date.month:02d}.{end_date.year}): {len(safe_quiz_ids)} quizzes")

    remind_ids = set()

    for tg_message in tg_messages:
        if tg_message["quiz_id"] in safe_quiz_ids:
            continue

        if "remind_message_id" in tg_message:
            remind_ids.add(tg_message["remind_message_id"])

        try:
            result = await bot.unpin_chat_message(target_group_id, tg_message["message_id"])
            logger.info(f'{"Successfully" if result else "Unable to"} unpin message {tg_message["message_id"]} for quiz {tg_message["quiz_id"]}')
        except Exception as error:
            logger.info(f"Raised exception during unpin old polls: {error}")

    for message_id in remind_ids:
        try:
            result = await bot.delete_message(target_group_id, message_id)
            logger.info(f'{"Successfully" if result else "Unable to"} remove remind message {message_id}')
        except Exception as error:
            logger.info(f"Raised exception during remove remind message: {error}")

    database.tg_quiz_messages.delete_many({"quiz_id": {"$nin": safe_quiz_ids}})


def get_remind_quizzes() -> List[dict]:
    today = datetime.now()
    start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59)
    return list(database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}).sort([("date", 1), ("time", 1)]))


def get_pred_quizzes() -> Tuple[str, List[dict]]:
    today = datetime.now()

    if today.day <= 10:
        start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    else:
        _, num_days = calendar.monthrange(today.year, today.month)
        start_date = datetime(today.year, today.month, 1, 0, 0, 0) + timedelta(days=num_days)

    _, num_days = calendar.monthrange(start_date.year, start_date.month)
    end_date = datetime(start_date.year, start_date.month, num_days, 23, 59, 59)

    return constants.MONTH_TO_RUS[start_date.month], list(database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}).sort([("date", 1), ("time", 1)]))


async def send_remind(quizzes: List[dict]) -> None:
    if not quizzes:
        return

    messages = {tg_message["quiz_id"]: tg_message for tg_message in database.tg_quiz_messages.find({"quiz_id": {"$in": [quiz["_id"] for quiz in quizzes]}})}
    if datetime(2024, 10, 12, 0, 0, 0) <= datetime.now() <= datetime(2024, 10, 21, 23, 59, 59):
        name = '<a href="https://t.me/dronperminov">Андрею</a>'
    else:
        name = '<a href="https://t.me/Sobolyulia">Юле</a>'

    final_line = f"Если ваши планы изменились, переголосуйте, пожалуйста, и напишите об этом {name}"
    places = get_places_dict()

    if len(quizzes) == 1:
        quiz = quizzes[0]
        place = places[quiz["place"]]
        lines = [
            f'Напоминаю, что сегодня квиз "{quiz["name"]}" в <b>{quiz["time"]}</b>',
            f'<b>Место проведения</b>: <a href="{place["yandex_map_link"]}">{quiz["place"]}</a> (м. {place["metro_station"]})',
            f'<b>Организатор</b>: {quiz["organizer"]}',
            f'<b>Стоимость</b>: {quiz["cost"]} руб\n',
            final_line
        ]

        if (existed_message := database.tg_quiz_messages.find_one({"quiz_id": quiz["_id"], "remind_message_id": {"$exists": True}})) is not None:
            await bot.edit_message_text("\n".join(lines), target_group_id, existed_message["remind_message_id"], parse_mode="HTML", disable_web_page_preview=True)
            return

        kwargs = {"reply_to_message_id": messages[quiz["_id"]]["message_id"]} if quiz["_id"] in messages else {}
        message = await bot.send_message(target_group_id, text="\n".join(lines), parse_mode="HTML", disable_web_page_preview=True, **kwargs)
    else:
        lines = ["Напоминаю, что сегодня проходят следующие квизы:\n"]
        for quiz in quizzes:
            place = places[quiz["place"]]
            name = f'<a href="{messages[quiz["_id"]]["url"]}">{quiz["name"]}</a>' if quiz["_id"] in messages else quiz["name"]
            lines.append(f'- {name} в <b>{quiz["time"]}</b>')
            lines.append(f'<b>Место проведения</b>: <a href="{place["yandex_map_link"]}">{quiz["place"]}</a> (м. {place["metro_station"]})')
            lines.append(f'<b>Организатор</b>: {quiz["organizer"]}')
            lines.append(f'<b>Стоимость</b>: {quiz["cost"]} руб\n')

        lines.append(final_line)
        message = await bot.send_message(target_group_id, text="\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)

    for quiz in quizzes:
        database.tg_quiz_messages.update_one({"quiz_id": quiz["_id"]}, {"$set": {"remind_message_id": message.message_id}})


async def send_story(quizzes: List[Quiz], quiz_ids: List[ObjectId], chat_ids: List[int]) -> None:
    if not quizzes or not chat_ids:
        return

    tg_messages = {tg_message["quiz_id"]: tg_message for tg_message in database.tg_quiz_messages.find({"quiz_id": {"$in": quiz_ids}})}
    caption = "\n".join([f'{quiz.name}:\n{tg_messages[quiz_id]["url"] if quiz_id in tg_messages else ""}' for quiz_id, quiz in zip(quiz_ids, quizzes)])

    date = quizzes[0].date
    weekday = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][date.weekday()]
    month = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"][date.month - 1]

    template = templates.get_template("pages/story.html")
    html = template.render(weekday=weekday, date=f"{date.day} {month}", quizzes=quizzes, places=get_places_dict())

    with tempfile.TemporaryDirectory() as tmp_dir:
        filename = f"story_{date.day}_{month}.png"
        hti = Html2Image(custom_flags=["--headless", "--no-sandbox"], size=(1080, 1920), output_path=tmp_dir)
        hti.screenshot(html_str=html, save_as=filename)
        photo_file = FSInputFile(os.path.join(tmp_dir, filename))

        for chat_id in chat_ids:
            await bot.send_document(chat_id=chat_id, document=photo_file, caption=caption)


def make_schedule_picture(output_path: str, date: str = "") -> str:
    hti = Html2Image(custom_flags=["--headless", "--no-sandbox"], size=(1280, 1210), output_path=output_path)
    hti.screenshot(url=f"https://plush-anvil.ru/schedule?date={date}", save_as="schedule.png")
    hti.screenshot(url=f"https://plush-anvil.ru/schedule?date={date}", save_as="schedule.png")

    today = datetime.now()
    next_date = today + timedelta(days=6)

    if date == "" and next_date.month != today.month and database.quizzes.find_one({"date": {"$gte": datetime(next_date.year, next_date.month, 1)}}):
        date = f"{constants.MONTH_TO_RUS[next_date.month]}-{next_date.year}"
        hti.screenshot(url=f"https://plush-anvil.ru/schedule?date={date}", save_as="schedule_next.png")
        hti.screenshot(url=f"https://plush-anvil.ru/schedule?date={date}", save_as="schedule_next.png")

        img1 = cv2.imread(os.path.join(output_path, "schedule.png"))
        img2 = cv2.imread(os.path.join(output_path, "schedule_next.png"))
        divider = np.ones((img1.shape[0], 80, 3), dtype=np.uint8) * 255
        cv2.imwrite(os.path.join(output_path, "schedule.png"), np.concatenate((img1, divider, img2), axis=1))

    return os.path.join(output_path, "schedule.png")


@dp.message(Command("get_id"))
async def log(message: types.Message) -> None:
    logger.info(f"Chat id: {message.chat.id}")
    logger.info(f"Chat title: {message.chat.title}")
    logger.info(f"Chat type: {message.chat.type}")
    await message.delete()


@dp.message(Command("start"))
async def handle_start(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    text = "\n".join([
        "Привет! Я бот Плюшевой наковальни!",
        "",
        "Команды, которые я знаю:",
        "/info - отображение общей информации",
        "/schedule - получение актуального расписания",
    ])

    await message.delete()
    await message.answer(text, parse_mode="Markdown")


@dp.message(Command("info"))
async def handle_info(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

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


async def make_quiz_poll(quiz_id: str, message: types.Message) -> None:
    quiz = parse_quiz_from_id(quiz_id)

    if quiz is None:
        return await send_error(message, f'Не удалось найти заданный квиз ("{quiz_id}")', delete_message=True)

    if tg_message := database.tg_quiz_messages.find_one({"quiz_id": ObjectId(quiz_id)}):
        return await send_error(message, "Опрос с этим квизом уже создан", delete_message=True, reply_to_message_id=tg_message["message_id"])

    places = get_places_dict()
    poll = await message.answer_poll(question=quiz.to_poll_title(places), options=["Пойду", "Не пойду"], is_anonymous=False, allows_multiple_answers=False)
    poll_url = poll.get_url()

    if poll_url and re.fullmatch(r"https://t.me/c/\d+/\d+", poll_url):
        database.tg_quiz_messages.insert_one({"quiz_id": ObjectId(quiz_id), "message_id": int(poll_url.split("/")[-1]), "url": poll_url})

    await poll.pin(disable_notification=True)


@dp.message(Command("poll"))
async def handle_poll(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    if message.chat.id != target_group_id:
        return await send_error(message, "Команда poll недоступна для этого чата", delete_message=True)

    if message.from_user.username not in config["admin_usernames"]:
        return await send_error(message, f"Команда poll недоступна для пользователя @{message.from_user.username}", delete_message=True)

    quiz_ids = re.split(r"\s+", re.sub(r"^/poll\s*", "", message.text))

    for quiz_id in quiz_ids:
        try:
            await make_quiz_poll(quiz_id, message)
        except Exception as error:
            logger.info(f"Unable to make poll for quiz {quiz_id} - {error}")

    await message.delete()
    await unpin_old_polls()


@dp.message(Command("story"))
async def handle_story(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    if message.chat.id not in [target_group_id, message.from_user.id]:
        return await send_error(message, "Команда story недоступна для этого чата", delete_message=True)

    quiz_ids = re.split(r",\s+", re.sub(r"^/story\s*", "", message.text))
    quizzes = [parse_quiz_from_id(quiz_id) for quiz_id in quiz_ids]

    if none_quizzes := [f'"{quiz_id}"' for quiz_id, quiz in zip(quiz_ids, quizzes) if quiz is None]:
        return await send_error(message, f'Не удалось найти некоторые квизы ({", ".join(none_quizzes)})', delete_message=True)

    await message.delete()
    await send_story(quizzes, [ObjectId(quiz_id) for quiz_id in quiz_ids], [message.from_user.id])


@dp.message(Command("remind"))
async def handle_remind(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    if message.chat.id != target_group_id:
        return await send_error(message, "Команда remind недоступна для этого чата", delete_message=True)

    try:
        await message.delete()
        await send_remind(get_remind_quizzes())
    except Exception as error:
        logger.info(f"Raised exception during remind: {error}")


@dp.message(Command("schedule"))
async def handle_schedule(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    if message.chat.id not in [target_group_id, message.from_user.id]:
        return await send_error(message, "Команда schedule недоступна для этого чата", delete_message=True)

    await message.delete()

    if message.chat.id == target_group_id:
        return await scheduled_update_schedule()

    with tempfile.TemporaryDirectory() as tmp_dir:
        await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile(make_schedule_picture(tmp_dir)), caption="Актуальное расписание")


@dp.message(Command("schedule_next"))
async def handle_schedule_next(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    if message.chat.id not in [target_group_id, message.from_user.id]:
        return await send_error(message, "Команда pred-schedule недоступна для этого чата", delete_message=True)

    await message.delete()
    today = datetime.now()
    month, year = (today.month + 1, today.year) if today.month < 12 else (1, today.year + 1)

    with tempfile.TemporaryDirectory() as tmp_dir:
        picture = make_schedule_picture(tmp_dir, f"{constants.MONTH_TO_RUS[month]}-{year}")
        message = await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile(picture), caption=f"Предварительное расписание на {constants.MONTH_TO_RUS[month]}")
        await message.pin(disable_notification=True)


@dp.message(Command("pred_poll"))
async def handle_pred_poll(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    if message.chat.id not in [target_group_id, message.from_user.id]:
        return await send_error(message, "Команда pred_poll недоступна для этого чата", delete_message=True)

    if message.from_user.username not in config["admin_usernames"]:
        return await send_error(message, f"Команда pred_poll недоступна для пользователя @{message.from_user.username}", delete_message=True)

    month, quizzes = get_pred_quizzes()

    if not quizzes:
        return await send_error(message, f"Квизы для формирования предварительных опросов на {month} отсутствуют", delete_message=True)

    await message.delete()

    places = get_places_dict()
    parts = (len(quizzes) + constants.LAST_POLL_OPTION - 1) // constants.LAST_POLL_OPTION

    for part in range(parts):
        parts_text = f". Часть {part + 1} / {parts}" if parts > 1 else ""
        question = f"{month.title()}, голосуем за те квизы, куда хотели бы пойти{parts_text}"
        partial_quizzes = [Quiz.from_dict(quiz) for quiz in quizzes[part * constants.LAST_POLL_OPTION:(part + 1) * constants.LAST_POLL_OPTION]]
        options = [quiz.to_poll_option(places) for quiz in partial_quizzes] + ["Никуда"]

        poll = await message.answer_poll(question=question, options=options, is_anonymous=False, allows_multiple_answers=True)
        await poll.pin(disable_notification=True)


@dp.inline_query(F.query == "poll")
async def handle_inline_poll(query: InlineQuery) -> None:
    logger.info(f"Inline command poll from user {query.from_user.username} ({query.from_user.id})")

    if query.from_user.username not in config["admin_usernames"]:
        return

    today = datetime.now()
    delta = 13 - today.weekday() if today.weekday() >= 2 else 6 - today.weekday()
    start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59) + timedelta(days=delta)

    results = []

    quizzes = list(database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}).sort([("date", 1), ("time", 1)]))
    created_ids = {message["quiz_id"] for message in database.tg_quiz_messages.find({"quiz_id": {"$in": [quiz["_id"] for quiz in quizzes]}})}
    lost_quiz_ids = []

    for quiz in quizzes:
        if quiz["_id"] in created_ids:
            continue

        quiz_id = str(quiz["_id"])
        quiz = Quiz.from_dict(quiz)
        lost_quiz_ids.append(quiz_id)

        results.append(InlineQueryResultArticle(
            id=quiz_id,
            title=quiz.to_inline_title(),
            description=quiz.to_inline_description(),
            input_message_content=InputTextMessageContent(message_text=f"/poll {quiz_id}"),
            thumbnail_url=f"https://plush-anvil.ru/images/organizers/{urllib.parse.quote(quiz.organizer)}.png?v=3",
            thumbnail_height=142,
            thumbnail_width=142
        ))

    if len(lost_quiz_ids) > 1:
        result = InlineQueryResultArticle(
            id="all_quizzes",
            title=f'Все {get_word_form(len(lost_quiz_ids), ["квизов", "квиза", "квиз"])} до {end_date.day:02d}.{end_date.month:02d}.{end_date.year}',
            description="",
            input_message_content=InputTextMessageContent(message_text=f'/poll {" ".join(lost_quiz_ids)}')
        )

        results = [result] + results

    await query.answer(results, is_personal=False, cache_time=0)


@dp.inline_query(F.query == "story")
async def handle_inline_story(query: InlineQuery) -> None:
    logger.info(f"Inline command story from user {query.from_user.username} ({query.from_user.id})")

    today = datetime.now()
    start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59) + timedelta(days=7)

    date2quizzes = defaultdict(list)
    for quiz in database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}).sort([("date", 1), ("time", 1)]):
        date2quizzes[f'{quiz["date"].day:02d}.{quiz["date"].month:02d}'].append(quiz)

    results = []
    for i, (date, date_quizzes) in enumerate(date2quizzes.items()):
        quiz_ids = ", ".join([str(quiz["_id"]) for quiz in date_quizzes])
        date_quizzes = [Quiz.from_dict(quiz) for quiz in date_quizzes]
        description = "\n".join(f"{quiz.name} ({quiz.place}, {quiz.time})" for quiz in date_quizzes)

        input_content = InputTextMessageContent(message_text=f"/story {quiz_ids}")
        results.append(InlineQueryResultArticle(id=f"story_{i}", title=date, description=description, input_message_content=input_content))

    await query.answer(results, is_personal=False, cache_time=0)


@dp.inline_query(F.query == "list")
async def handle_inline_list(query: InlineQuery) -> None:
    today = datetime.now()
    curr_start, curr_end = get_month_dates(today)

    dates = [
        (datetime(today.year, today.month, today.day, 0, 0, 0), curr_end),
        get_month_dates(curr_end + timedelta(days=1))
    ]

    results = []
    for start_date, end_date in dates:
        quizzes = [Quiz.from_dict(quiz) for quiz in database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}).sort([("date", 1), ("time", 1)])]
        if not quizzes:
            continue

        month = constants.MONTH_TO_RUS[start_date.month]
        title = f"Список квизов на {month}"
        description = get_word_form(len(quizzes), ["квизов", "квиза", "квиз"])
        content = "\n".join(quiz.to_inline_title() for quiz in quizzes)
        input_content = InputTextMessageContent(message_text=f"{title}\n```\n{content}\n```", parse_mode="MarkdownV2")
        results.append(InlineQueryResultArticle(id=f"list_{month}_{start_date.year}", title=title, description=description, input_message_content=input_content))

    await query.answer(results, is_personal=False, cache_time=0)


def get_rating_text(rating: dict) -> str:
    history = []

    for i, info in enumerate(rating["history"]):
        level = constants.SMUZI_RATING_TO_NAME[i]["name"]
        date = f'{info["date"].day:02d}.{info["date"].month:02d}.{info["date"].year}'
        games = get_word_form(len(info["players"]), ["игр", "игры", "игру"])
        history.append(f'- <b>{level}</b>: достигли {date} с рейтингом {info["score"]} за {games}, игроков в среднем: {info["mean_players"]:.1f}')

    lines = [f'<b>Рейтинг смузи</b>: {rating["score"]} ({rating["info"]["level"]} уровень, {rating["info"]["name"]})']

    if rating["players"]:
        lines.append(f'<b>Среднее количество игроков</b>: {rating["mean_players"]:.1f} ({get_word_form(len(rating["players"]), ["игр", "игры", "игра"])})')

    lines.append("\n<b>История получения уровней</b>:")
    lines.extend(history)
    lines.append("\nПост с информацией про рейтинг: https://vk.com/smuzi_msk?w=wall-164592450_73696")
    return "\n".join(lines)


@dp.message(Command("rating"))
async def handle_rating(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    await message.delete()
    await message.answer(get_rating_text(get_smuzi_rating()), parse_mode="HTML", disable_web_page_preview=True)


async def scheduled_send_remind() -> None:
    quizzes = get_remind_quizzes()
    await send_remind(quizzes)


async def scheduled_send_story() -> None:
    quizzes = get_remind_quizzes()
    await send_story([Quiz.from_dict(quiz) for quiz in quizzes], [quiz["_id"] for quiz in quizzes], config.get("story_user_ids", []))
    await unpin_old_polls()


async def scheduled_send_birthday() -> None:
    users = [user for user in database.get_birthday_users() if database.get_days_to_birthday(user.birthdate) == 7]
    if not users:
        return

    user_links = ", ".join([f'<a href="https://plush-anvil.ru/profile?username={user.username}">{user.fullname}</a>' for user in users])
    lines = [
        f'Напоминаю, что у пользовател{"я" if len(users) == 1 else "ей"} {user_links} день рождения через 7 дней.',
        "А ещё напоминаю, что ты супер умничка!"
    ]

    try:
        for chat_id in config.get("birthday_user_ids", []):
            await bot.send_message(chat_id=chat_id, text="\n".join(lines), parse_mode="HTML")
    except Exception as error:
        logger.info(f"Unable send birthday for {users[0].fullname}: {error}")


async def scheduled_update_schedule() -> None:
    today = datetime.now()
    caption = f"Расписание (обновлено {today.day:02}.{today.month:02d}.{today.year} в {today.hour:02d}:{today.minute:02d})"
    tg_message = database.tg_messages.find_one({"name": "schedule"})

    with tempfile.TemporaryDirectory() as tmp_dir:
        photo = FSInputFile(make_schedule_picture(tmp_dir))

        if tg_message:
            try:
                await bot.edit_message_media(InputMediaPhoto(media=photo, caption=caption), chat_id=target_group_id, message_id=tg_message["message_id"])
            except Exception as e:
                if "message to edit not found" in str(e):
                    tg_message = None
                    database.tg_messages.delete_one({"name": "schedule"})

        if not tg_message:
            message = await bot.send_photo(chat_id=target_group_id, photo=photo, caption=caption)
            await message.pin()
            database.tg_messages.insert_one({"name": "schedule", "message_id": message.message_id})


async def scheduler() -> None:
    scheduled_time = config["schedule_time"]
    aioschedule.every().day.at(scheduled_time["remind"]).do(scheduled_send_remind)
    aioschedule.every().day.at(scheduled_time["birthday"]).do(scheduled_send_birthday)
    aioschedule.every().day.at(scheduled_time["story"]).do(scheduled_send_story)
    aioschedule.every().day.at(scheduled_time["schedule"]).do(scheduled_update_schedule)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def run_scheduler() -> None:
    asyncio.create_task(scheduler())


async def main() -> None:
    database.connect()

    loop = asyncio.get_event_loop()
    loop.create_task(run_scheduler())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
