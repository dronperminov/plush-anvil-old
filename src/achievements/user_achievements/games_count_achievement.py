from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz
from src.utils.common import get_word_form


class GamesCountAchievement(Achievement):
    def __init__(self, name: str, description: str, target_count: int) -> None:
        self.name = name
        self.description = description
        self.target_count = target_count

    def analyze(self, quizzes: List[Quiz]) -> None:
        if len(quizzes) < self.target_count:
            self.label_date = f'ещё {get_word_form(self.target_count - len(quizzes), ["игр", "игры", "игра"])}'
            return

        self.count = len(quizzes) // self.target_count
        self.first_date = quizzes[self.target_count - 1].date
