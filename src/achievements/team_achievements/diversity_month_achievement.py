from collections import defaultdict
from datetime import datetime
from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz


class DiversityMonthAchievement(Achievement):
    def __init__(self) -> None:
        self.name = "Месяц разнообразия"
        self.description = "посетить игры трёх и более организаторов за месяц"

    def analyze(self, quizzes: List[Quiz]) -> None:
        month2organizers = defaultdict(set)

        for quiz in quizzes:
            month2organizers[(quiz.date.year, quiz.date.month)].add(quiz.organizer)

        for (year, month), organizers in month2organizers.items():
            if len(organizers) >= 3:
                self.increment(datetime(year, month, 1))

    def set_label_date(self) -> None:
        month2text = ["январе", "феврале", "марте", "апреле", "мае", "июне", "июле", "августе", "сентябре", "октябре", "ноябре", "декабре"]
        self.label_date = None if self.first_date is None else f"в {month2text[self.first_date.month - 1]} {self.first_date.year}"
