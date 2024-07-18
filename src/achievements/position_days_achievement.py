from datetime import timedelta
from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz


class PositionDaysAchievement(Achievement):
    def __init__(self, name: str, description: str, target_count: int, position: int) -> None:
        self.name = name
        self.description = description
        self.target_count = target_count
        self.position = position

    def analyze(self, quizzes: List[Quiz]) -> None:
        dates = sorted({quiz.date.date() for quiz in quizzes if quiz.position <= self.position})
        prev_date = dates[0]
        count = 0

        for date in dates:
            count = count + 1 if (date - prev_date).days <= 1 else 1
            prev_date = date

            if count == self.target_count:
                self.increment(date)

    def set_label_date(self) -> None:
        if self.first_date is None:
            self.label_date = None
            return

        start = self.first_date - timedelta(days=self.target_count - 1)
        self.label_date = f"с {start.day:02}.{start.month:02}.{start.year} по {self.first_date.day:02}.{self.first_date.month:02}.{self.first_date.year}"
