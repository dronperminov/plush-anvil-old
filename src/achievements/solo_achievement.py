from typing import List

from src.achievements.achievement import Achievement
from src.dataclasses.quiz import Quiz


class SoloAchievement(Achievement):
    def analyze(self, quizzes: List[Quiz]) -> None:
        for quiz in quizzes:
            if quiz.players == 1:
                self.increment(quiz.date)
