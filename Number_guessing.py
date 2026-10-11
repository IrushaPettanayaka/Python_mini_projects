"""A compact number guessing game with reusable, testable game logic."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


MINIMUM = 1
MAXIMUM = 100
MAX_ATTEMPTS = 7


@dataclass
class GuessingRound:
    """Track one round and calculate feedback for every valid guess."""

    secret: int
    attempts_allowed: int = MAX_ATTEMPTS
    guesses: list[int] = field(default_factory=list)

    @property
    def attempts_left(self) -> int:
        return self.attempts_allowed - len(self.guesses)

    @property
    def is_over(self) -> bool:
        return self.secret in self.guesses or self.attempts_left == 0

    def submit(self, guess: int) -> str:
        if self.is_over:
            raise RuntimeError("This round has already finished.")
        if not MINIMUM <= guess <= MAXIMUM:
            raise ValueError(f"Guess must be between {MINIMUM} and {MAXIMUM}.")

        self.guesses.append(guess)
        distance = abs(self.secret - guess)

        if guess == self.secret:
            return "correct"
        if distance <= 5:
            return "very close"
        if distance <= 15:
            return "close"
        return "too low" if guess < self.secret else "too high"


def read_guess(prompt: str = "Your guess: ") -> int:
    """Keep asking until the player enters an integer in range."""

    while True:
        raw_value = input(prompt).strip()
        try:
            guess = int(raw_value)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if MINIMUM <= guess <= MAXIMUM:
            return guess
        print(f"Choose a number from {MINIMUM} to {MAXIMUM}.")


def play_round(secret: int | None = None) -> bool:
    """Play one round and return True when the player wins."""

    round_state = GuessingRound(secret or random.randint(MINIMUM, MAXIMUM))
    print(f"\nI picked a number from {MINIMUM} to {MAXIMUM}.")
    print(f"You have {round_state.attempts_allowed} attempts.")

    while not round_state.is_over:
        guess = read_guess()
        feedback = round_state.submit(guess)

        if feedback == "correct":
            print(f"Correct! You solved it in {len(round_state.guesses)} attempts.")
            return True

        print(f"{guess} is {feedback}.")
        if round_state.attempts_left:
            print(f"Attempts left: {round_state.attempts_left}")

    print(f"Out of attempts. The number was {round_state.secret}.")
    return False


def wants_to_play_again() -> bool:
    while True:
        answer = input("Play again? (y/n): ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer y or n.")


def main() -> None:
    print("Welcome to Quick Guess!")
    wins = 0
    rounds = 0

    while True:
        rounds += 1
        wins += int(play_round())
        print(f"Score: {wins} win(s) from {rounds} round(s).")
        if not wants_to_play_again():
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
