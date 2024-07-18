from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz


class PlayersCountAchievement(Achievement):
    def __init__(self, name: str, description: str, min_count: int, max_count: int) -> None:
        self.name = name
        self.description = description
        self.min_count = min_count
        self.max_count = max_count

    def analyze(self, quizzes: List[Quiz]) -> None:
        for quiz in quizzes:
            if self.min_count <= quiz.players <= self.max_count:
                self.increment(quiz.date)
