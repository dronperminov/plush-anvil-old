from collections import defaultdict
from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz


class ThereHereAchievement(Achievement):
    def __init__(self) -> None:
        self.name = "И там и тут"
        self.description = "посетить две и более игры в одно и то же время"

    def analyze(self, quizzes: List[Quiz]) -> None:
        date2count = defaultdict(int)

        for quiz in quizzes:
            date2count[(quiz.date, quiz.time)] += 1

        for (date, _), count in date2count.items():
            if count != 1:
                self.increment(date)
