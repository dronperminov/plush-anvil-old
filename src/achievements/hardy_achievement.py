from collections import defaultdict
from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz


class HardyAchievement(Achievement):
    def __init__(self, name: str, description: str, min_count: int, max_count: int) -> None:
        self.name = name
        self.description = description
        self.min_count = min_count
        self.max_count = max_count

    def analyze(self, quizzes: List[Quiz]) -> None:
        date2count = defaultdict(int)

        for quiz in quizzes:
            date2count[quiz.date] += 1

        self.first_date = None

        for date, count in date2count.items():
            if self.min_count <= count <= self.max_count:
                self.increment(date)
