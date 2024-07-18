import abc
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from src.dataclasses.quiz import Quiz


@dataclass
class Achievement:
    name: str
    description: str
    count: int = 0
    first_date: Optional[datetime] = None
    label_date: Optional[str] = None

    @abc.abstractmethod
    def analyze(self, quizzes: List[Quiz]) -> None:
        pass

    def set_label_date(self) -> None:
        self.label_date = None if self.first_date is None else f"{self.first_date.day:02}.{self.first_date.month:02}.{self.first_date.year}"

    def increment(self, date: datetime) -> None:
        self.count += 1

        if self.first_date is None or date < self.first_date:
            self.first_date = date
