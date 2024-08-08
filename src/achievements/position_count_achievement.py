from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz
from src.utils.common import get_word_form


class PositionCountAchievement(Achievement):
    def __init__(self, name: str, description: str, target_count: int, position: int) -> None:
        self.name = name
        self.description = description
        self.target_count = target_count
        self.position = position

    def analyze(self, quizzes: List[Quiz]) -> None:
        count = 0

        for quiz in quizzes:
            if quiz.position > self.position:
                continue

            count += 1

            if count == self.target_count:
                self.increment(quiz.date)
                count = 0

        if self.count == 0 and count < self.target_count:
            if self.position == 1:
                words = ["побед", "победы", "победа"]
            elif self.position == 3:
                words = ["призовых игр", "призовых игры", "призовая игра"]
            else:
                words = ["игр", "игры", "игра"]

            self.label_date = f"ещё {get_word_form(self.target_count - count, words)}"
