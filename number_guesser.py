"""A configurable number guessing game with hints and session statistics."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Difficulty:
    name: str
    maximum: int
    attempts: int


DIFFICULTIES = {
    "easy": Difficulty("easy", maximum=50, attempts=10),
    "medium": Difficulty("medium", maximum=100, attempts=8),
    "hard": Difficulty("hard", maximum=250, attempts=7),
}


@dataclass
class GuessResult:
    guess: int
    feedback: str
    distance: int
    attempts_left: int
    is_correct: bool


@dataclass
class GuessingGame:
    difficulty: Difficulty
    secret_number: int
    guesses: list[int] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        difficulty: Difficulty,
        rng: random.Random | None = None,
    ) -> "GuessingGame":
        generator = rng or random.Random()
        secret = generator.randint(1, difficulty.maximum)
        return cls(difficulty=difficulty, secret_number=secret)

    @property
    def attempts_left(self) -> int:
        return self.difficulty.attempts - len(self.guesses)

    @property
    def has_won(self) -> bool:
        return bool(self.guesses and self.guesses[-1] == self.secret_number)

    @property
    def is_finished(self) -> bool:
        return self.has_won or self.attempts_left == 0

    def submit_guess(self, guess: int) -> GuessResult:
        """Record a guess and return structured feedback."""

        if self.is_finished:
            raise RuntimeError("The game has already finished.")
        if not 1 <= guess <= self.difficulty.maximum:
            raise ValueError(f"Enter a number from 1 to {self.difficulty.maximum}.")
        if guess in self.guesses:
            raise ValueError("You already tried that number.")

        self.guesses.append(guess)
        distance = abs(self.secret_number - guess)
        correct = distance == 0

        if correct:
            feedback = "Correct"
        elif distance <= max(2, self.difficulty.maximum // 50):
            feedback = "Burning hot"
        elif distance <= self.difficulty.maximum // 10:
            feedback = "Warm"
        elif guess < self.secret_number:
            feedback = "Too low"
        else:
            feedback = "Too high"

        return GuessResult(
            guess=guess,
            feedback=feedback,
            distance=distance,
            attempts_left=self.attempts_left,
            is_correct=correct,
        )

    def history_summary(self) -> str:
        if not self.guesses:
            return "No guesses yet."
        return "Previous guesses: " + ", ".join(str(guess) for guess in self.guesses)


@dataclass
class SessionStats:
    games_played: int = 0
    games_won: int = 0
    total_guesses: int = 0
    best_score: int | None = None

    def record(self, game: GuessingGame) -> None:
        self.games_played += 1
        self.total_guesses += len(game.guesses)
        if game.has_won:
            self.games_won += 1
            score = len(game.guesses)
            if self.best_score is None or score < self.best_score:
                self.best_score = score

    def summary(self) -> str:
        if not self.games_played:
            return "No games played."

        win_rate = self.games_won / self.games_played
        average = self.total_guesses / self.games_played
        best = self.best_score if self.best_score is not None else "—"
        return (
            f"Games: {self.games_played} | Wins: {self.games_won} "
            f"({win_rate:.0%}) | Average guesses: {average:.1f} | Best: {best}"
        )


def choose_difficulty() -> Difficulty:
    print("\nDifficulty options:")
    for profile in DIFFICULTIES.values():
        print(
            f"  {profile.name:<6} — 1 to {profile.maximum}, "
            f"{profile.attempts} attempts"
        )

    while True:
        choice = input("Choose easy, medium, or hard: ").strip().lower()
        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]
        print("Please choose one of the listed difficulties.")


def read_guess(game: GuessingGame) -> int:
    while True:
        raw_value = input(
            f"Guess 1–{game.difficulty.maximum} "
            "('history' to review): "
        ).strip().lower()

        if raw_value in {"history", "h"}:
            print(game.history_summary())
            continue

        try:
            guess = int(raw_value)
        except ValueError:
            print("Please enter a whole number or 'history'.")
            continue

        if not 1 <= guess <= game.difficulty.maximum:
            print(f"The valid range is 1 to {game.difficulty.maximum}.")
            continue
        if guess in game.guesses:
            print("You already tried that number.")
            continue
        return guess


def play_game(difficulty: Difficulty) -> GuessingGame:
    game = GuessingGame.create(difficulty)
    print(
        f"\nI picked a number from 1 to {difficulty.maximum}. "
        f"You have {difficulty.attempts} attempts."
    )

    while not game.is_finished:
        result = game.submit_guess(read_guess(game))
        if result.is_correct:
            print(
                f"Correct! The number was {game.secret_number}. "
                f"You used {len(game.guesses)} guess(es)."
            )
            break

        print(f"{result.feedback}. {result.attempts_left} attempt(s) remaining.")
        if len(game.guesses) >= 2:
            previous_distance = abs(game.secret_number - game.guesses[-2])
            trend = "closer" if result.distance < previous_distance else "farther away"
            print(f"That guess was {trend} than your previous guess.")

    if not game.has_won:
        print(f"No attempts left. The secret number was {game.secret_number}.")
    return game


def ask_to_continue() -> bool:
    while True:
        answer = input("\nPlay another game? (y/n): ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer y or n.")


def main() -> None:
    print("=" * 42)
    print("        NUMBER GUESSING CHALLENGE")
    print("=" * 42)
    stats = SessionStats()

    while True:
        game = play_game(choose_difficulty())
        stats.record(game)
        print("\nSession stats")
        print(stats.summary())
        if not ask_to_continue():
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
