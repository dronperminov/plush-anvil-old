import asyncio
import json
import logging
import os
import re
import tempfile
import urllib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional

import aioschedule as aioschedule
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile, InlineQuery, InlineQueryResultArticle, InputMediaPhoto, InputTextMessageContent
from bson import ObjectId
from bson.errors import InvalidId
from html2image import Html2Image

from src.api import templates
from src.constants import SMUZI_RATING_TO_NAME
from src.database import database
from src.dataclasses.quiz import Quiz
from src.utils.common import get_places, get_smuzi_rating, get_word_form

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

    quiz_ids = [quiz["_id"] for quiz in database.quizzes.find({"_id": {"$in": tg_quiz_ids}, "date": {"$lt": end_date}}, {"_id": 1})]

    for tg_message in tg_messages:
        if tg_message["quiz_id"] in quiz_ids:
            await bot.unpin_chat_message(target_group_id, tg_message["message_id"])

    database.tg_quiz_messages.delete_many({"quiz_id": {"$in": quiz_ids}})


def get_remind_quizzes() -> List[dict]:
    today = datetime.now()
    start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59)
    return list(database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}))


async def send_remind(quizzes: List[dict]) -> None:
    if not quizzes:
        return

    messages = {tg_message["quiz_id"]: tg_message for tg_message in database.tg_quiz_messages.find({"quiz_id": {"$in": [quiz["_id"] for quiz in quizzes]}})}

    if len(quizzes) == 1:
        quiz = quizzes[0]
        lines = [
            f'Напоминаю, что сегодня квиз "{quiz["name"]}" в <b>{quiz["time"]}</b>',
            f'<b>Место проведения</b>: {quiz["place"]}',
            f'<b>Стоимость</b>: {quiz["cost"]} руб\n',
            'Если ваши планы изменились, переголосуйте, пожалуйста, и напишите об этом <a href="https://t.me/Sobolyulia">Юле</a>'
        ]

        kwargs = {"reply_to_message_id": messages[quiz["_id"]]["message_id"]} if quiz["_id"] in messages else {}
        await bot.send_message(target_group_id, text="\n".join(lines), parse_mode="HTML", disable_web_page_preview=True, **kwargs)
    else:
        lines = ["Напоминаю, что сегодня проходят следующие квизы:\n"]
        for quiz in quizzes:
            name = f'<a href="{messages[quiz["_id"]]["url"]}">{quiz["name"]}</a>' if quiz["_id"] in messages else quiz["name"]
            lines.append(f'- {name} в <b>{quiz["time"]}</b>\n<b>Место проведения</b>: {quiz["place"]}\n<b>Стоимость</b>: {quiz["cost"]} руб\n')

        lines.append('Если ваши планы изменились, переголосуйте, пожалуйста, и напишите об этом <a href="https://t.me/Sobolyulia">Юле</a>')
        await bot.send_message(target_group_id, text="\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


async def send_story(quizzes: List[Quiz], quiz_ids: List[ObjectId], chat_ids: List[int]) -> None:
    if not quizzes or not chat_ids:
        return

    tg_messages = {tg_message["quiz_id"]: tg_message for tg_message in database.tg_quiz_messages.find({"quiz_id": {"$in": quiz_ids}})}
    caption = "\n".join([f'{quiz.name}: {tg_messages[quiz_id]["url"] if quiz_id in tg_messages else ""}' for quiz_id, quiz in zip(quiz_ids, quizzes)])

    date = quizzes[0].date
    weekday = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][date.weekday()]
    month = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"][date.month - 1]

    template = templates.get_template("pages/story.html")
    html = template.render(weekday=weekday, date=f"{date.day} {month}", quizzes=quizzes, places=get_places())

    with tempfile.TemporaryDirectory() as tmp_dir:
        filename = f"story_{date.day}_{month}.png"
        hti = Html2Image(custom_flags=["--headless", "--no-sandbox"], size=(1080, 1920), output_path=tmp_dir)
        hti.screenshot(html_str=html, save_as=filename)
        photo_file = FSInputFile(os.path.join(tmp_dir, filename))

        for chat_id in chat_ids:
            await bot.send_document(chat_id=chat_id, document=photo_file, caption=caption)


def make_schedule_picture(output_path: str) -> str:
    hti = Html2Image(custom_flags=["--headless", "--no-sandbox"], size=(1280, 1020), output_path=output_path)
    hti.screenshot(url="https://plush-anvil.ru/schedule", save_as="schedule.png")
    hti.screenshot(url="https://plush-anvil.ru/schedule", save_as="schedule.png")
    return os.path.join(output_path, "schedule.png")


def get_rating_text(rating: dict) -> str:
    history = []

    for i, info in enumerate(rating["history"]):
        level = SMUZI_RATING_TO_NAME[i]["name"]
        date = f'{info["date"].day:02d}.{info["date"].month:02d}.{info["date"].year}'
        games = get_word_form(len(info["players"]), ["игр", "игры", "игра"])
        history.append(f'- <b>{level}</b>: достигли {date} с рейтингом {info["score"]} за {games}, игроков в среднем: {info["mean_players"]:.1f}')

    lines = [f'<b>Рейтинг смузи</b>: {rating["score"]} ({rating["info"]["level"]} уровень, {rating["info"]["name"]})']

    if rating["players"]:
        lines.append(f'<b>Среднее количество игроков</b>: {rating["mean_players"]:.1f} ({get_word_form(len(rating["players"]), ["игр", "игры", "игра"])})')

    lines.append("\n<b>История получения уровней</b>:")
    lines.extend(history)
    lines.append("\nПост с информацией про рейтинг: https://vk.com/smuzi_msk?w=wall-164592450_73696")
    return "\n".join(lines)


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
        "/rating - информация о текущем рейтинге Смузи",
        "/schedule - получение актуального расписания",
        "/remind - напоминание про квиз (если в этот день есть квизы)",
        "",
        "А ещё админы могут:",
        "- создавать опросы про квизы, написав `@plush_anvil_bot poll` и выбрав нужный квиз",
        "- создавать картинки с описанием для сториз, написав `@plush_anvil_bot story` и выбрав нужный квиз"
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


@dp.message(Command("rating"))
async def handle_rating(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    await message.delete()
    await message.answer(get_rating_text(get_smuzi_rating()), parse_mode="HTML", disable_web_page_preview=True)


@dp.message(Command("poll"))
async def handle_poll(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    if message.chat.id != target_group_id:
        return await send_error(message, "Команда poll недоступна для этого чата", delete_message=True)

    if message.from_user.username not in config["admin_usernames"]:
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


@dp.message(Command("remind"))
async def handle_remind(message: types.Message) -> None:
    logger.info(f"Command {message.text} from user {message.from_user.username} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id})")

    if message.chat.id != target_group_id:
        return await send_error(message, "Команда remind недоступна для этого чата", delete_message=True)

    quizzes = get_remind_quizzes()

    if not quizzes:
        return await send_error(message, "Слишком рано для напоминания, сегодня нет никаких квизов", delete_message=True)

    await message.delete()
    await send_remind(quizzes)


@dp.inline_query(F.query == "info")
async def handle_inline_info(query: InlineQuery) -> None:
    logger.info(f"Inline command info from user {query.from_user.username} ({query.from_user.id})")

    rating = get_smuzi_rating()

    items = [
        {"title": "Сайт", "description": "plush-anvil.ru", "text": "<b>Сайт</b>: plush-anvil.ru"},
        {"title": "Рейтинг смузи", "description": f'{rating["score"]} ({rating["info"]["name"]})', "text": get_rating_text(rating)},
        {"title": "УМ тренировки", "description": "music-quiz.plush-anvil.ru", "text": "<b>Сайт для УМ тренировок</b>: music-quiz.plush-anvil.ru"},
        {"title": "КМС тренировки", "description": "movie-quiz.plush-anvil.ru", "text": "<b>Сайт для КМС тренировок</b>: movie-quiz.plush-anvil.ru"}
    ]

    results = []

    for i, item in enumerate(items):
        content = InputTextMessageContent(message_text=item["text"], parse_mode="HTML", disable_web_page_preview=True)
        result = InlineQueryResultArticle(id=f"info_{i}", title=item["title"], description=item["description"], input_message_content=content)
        results.append(result)

    await query.answer(results, is_personal=False, cache_time=0)


@dp.inline_query(F.query == "poll")
async def handle_inline_poll(query: InlineQuery) -> None:
    logger.info(f"Inline command poll from user {query.from_user.username} ({query.from_user.id})")

    if query.from_user.username not in config["admin_usernames"]:
        return

    today = datetime.now()
    start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59) + timedelta(days=7)

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
            thumbnail_height=142,
            thumbnail_width=142
        ))

    await query.answer(results, is_personal=False, cache_time=0)


@dp.inline_query(F.query == "story")
async def handle_inline_story(query: InlineQuery) -> None:
    logger.info(f"Inline command story from user {query.from_user.username} ({query.from_user.id})")

    today = datetime.now()
    start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59) + timedelta(days=7)

    date2quizzes = defaultdict(list)
    for quiz in database.quizzes.find({"date": {"$gte": start_date, "$lte": end_date}}):
        date2quizzes[f'{quiz["date"].day:02d}.{quiz["date"].month:02d}'].append(quiz)

    results = []
    for i, (date, date_quizzes) in enumerate(date2quizzes.items()):
        quiz_ids = ", ".join([str(quiz["_id"]) for quiz in date_quizzes])
        date_quizzes = [Quiz.from_dict(quiz) for quiz in date_quizzes]
        description = "\n".join(f"{quiz.name} ({quiz.place}, {quiz.time})" for quiz in date_quizzes)

        input_content = InputTextMessageContent(message_text=f"/story {quiz_ids}")
        results.append(InlineQueryResultArticle(id=f"story_{i}", title=date, description=description, input_message_content=input_content))

    await query.answer(results, is_personal=False, cache_time=0)


async def scheduled_send_remind() -> None:
    quizzes = get_remind_quizzes()
    await send_remind(quizzes)


async def scheduled_send_story() -> None:
    quizzes = get_remind_quizzes()
    await send_story([Quiz.from_dict(quiz) for quiz in quizzes], [quiz["_id"] for quiz in quizzes], config.get("story_user_ids", []))
    await unpin_old_polls()


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
