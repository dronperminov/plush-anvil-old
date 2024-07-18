from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz


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
                self.count = -1
                self.first_date = quiz.date
                break
