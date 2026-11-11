"""Deterministic interactive counting activity for Emma."""

import re
from dataclasses import dataclass
from typing import Dict, Optional


NUMBER_WORDS: Dict[int, set] = {
    1: {"one", "1", "wan", "ek"},
    2: {"two", "2", "to", "too", "do"},
    3: {"three", "3", "tree", "teen"},
    4: {"four", "4", "for", "char"},
    5: {"five", "5", "paanch", "panch"},
    6: {"six", "6", "cheh", "chhe"},
    7: {"seven", "7", "saat"},
    8: {"eight", "8", "ate", "aath", "ath"},
    9: {"nine", "9", "nau", "nav"},
    10: {"ten", "10", "das"},
}


@dataclass
class CountingStep:
    message: str
    finished: bool = False
    stopped: bool = False
    success: bool = False


class InteractiveCounting:
    """State machine for counting from one through ten."""

    def __init__(self, target_number: int = 10, max_retries: int = 2):
        self.current_number = 1
        self.target_number = target_number
        self.retry_count = 0
        self.max_retries = max_retries
        self.awaiting_response = True

    @property
    def current_word(self) -> str:
        return self._english_word(self.current_number)

    def opening(self) -> str:
        return "Let's learn counting together!"

    def prompt(self) -> str:
        return f"Now say... {self.current_word}."

    def handle(self, response: str) -> CountingStep:
        """Handle one child response and advance only after success or retries."""
        normalized = re.sub(r"[^a-z0-9 ]", " ", response.casefold()).strip()
        if re.search(r"\b(stop|enough|finished|done|cancel)\b", normalized):
            self.awaiting_response = False
            return CountingStep("Okay, we can stop counting.", stopped=True)

        if re.search(r"\b(again|more|once more)\b", normalized):
            self.retry_count = 0
            return CountingStep("Of course! Let's try that number again.")

        if self._matches_current(normalized):
            completed_number = self.current_number
            self.current_number += 1
            self.retry_count = 0
            if completed_number >= self.target_number:
                self.awaiting_response = False
                return CountingStep(
                    "Ten! Very good! You counted all the way to ten! High five!",
                    finished=True,
                    success=True,
                )
            return CountingStep(
                "Very good!"
            )

        self.retry_count += 1
        if self.retry_count <= self.max_retries:
            return CountingStep(
                f"Good try! We are saying {self.current_word}. "
                "Let's try it again."
            )

        skipped_number = self.current_number
        self.current_number += 1
        self.retry_count = 0
        if skipped_number >= self.target_number:
            self.awaiting_response = False
            return CountingStep(
                "Ten! Very good! You counted all the way to ten! High five!",
                finished=True,
            )
        return CountingStep(
            "That's okay. Let's try the next number."
        )

    def _matches_current(self, response: str) -> bool:
        return any(
            re.search(rf"\b{re.escape(alias)}\b", response)
            for alias in NUMBER_WORDS[self.current_number]
        )

    @staticmethod
    def _english_word(number: int) -> str:
        return {
            1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
            6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
        }[number]
