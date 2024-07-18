from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz


class NarrowCircleAchievement(Achievement):
    def __init__(self) -> None:
        self.name = "Узким кругом"
        self.description = "участвовать в квизе с количеством команд не более 5"

    def analyze(self, quizzes: List[Quiz]) -> None:
        for quiz in quizzes:
            if quiz.teams <= 5:
                self.increment(quiz.date)
