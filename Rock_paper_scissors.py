"""Best-of Rock Paper Scissors with an adaptive computer opponent."""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum


class Choice(str, Enum):
    ROCK = "r"
    PAPER = "p"
    SCISSORS = "s"


EMOJIS = {
    Choice.ROCK: "🪨",
    Choice.PAPER: "📄",
    Choice.SCISSORS: "✂️",
}
NAMES = {choice: choice.name.title() for choice in Choice}
WINNING_RESPONSE = {
    Choice.ROCK: Choice.PAPER,
    Choice.PAPER: Choice.SCISSORS,
    Choice.SCISSORS: Choice.ROCK,
}


@dataclass
class Scoreboard:
    target_wins: int
    player_wins: int = 0
    computer_wins: int = 0
    ties: int = 0
    player_history: list[Choice] = field(default_factory=list)

    @property
    def match_over(self) -> bool:
        return self.player_wins >= self.target_wins or self.computer_wins >= self.target_wins

    def display(self) -> str:
        return (
            f"You {self.player_wins} — {self.computer_wins} Computer "
            f"| Ties {self.ties} | First to {self.target_wins}"
        )


def determine_winner(player: Choice, computer: Choice) -> str:
    if player == computer:
        return "tie"
    if WINNING_RESPONSE[computer] == player:
        return "player"
    return "computer"


def choose_computer_move(
    player_history: list[Choice],
    rng: random.Random | None = None,
) -> Choice:
    """Counter the player's common move 65% of the time after three rounds."""

    generator = rng or random.Random()
    if len(player_history) >= 3 and generator.random() < 0.65:
        most_common_move = Counter(player_history).most_common(1)[0][0]
        return WINNING_RESPONSE[most_common_move]
    return generator.choice(list(Choice))


def parse_choice(value: str) -> Choice | None:
    normalized = value.strip().lower()
    aliases = {
        "r": Choice.ROCK,
        "rock": Choice.ROCK,
        "p": Choice.PAPER,
        "paper": Choice.PAPER,
        "s": Choice.SCISSORS,
        "scissors": Choice.SCISSORS,
    }
    return aliases.get(normalized)


def get_user_choice() -> Choice:
    while True:
        value = input("Rock, paper, or scissors? (r/p/s): ")
        choice = parse_choice(value)
        if choice is not None:
            return choice
        print("Enter r, p, s, or the full choice name.")


def get_target_wins() -> int:
    while True:
        raw_value = input("Play first to how many wins? [3]: ").strip()
        if not raw_value:
            return 3
        try:
            target = int(raw_value)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if 1 <= target <= 10:
            return target
        print("Choose a target from 1 to 10.")


def display_choices(player: Choice, computer: Choice) -> None:
    print(f"You chose {EMOJIS[player]}  {NAMES[player]}")
    print(f"Computer chose {EMOJIS[computer]}  {NAMES[computer]}")


def play_round(scoreboard: Scoreboard) -> None:
    player = get_user_choice()
    computer = choose_computer_move(scoreboard.player_history)
    scoreboard.player_history.append(player)
    display_choices(player, computer)

    winner = determine_winner(player, computer)
    if winner == "player":
        scoreboard.player_wins += 1
        print("You win this round!")
    elif winner == "computer":
        scoreboard.computer_wins += 1
        print("Computer wins this round.")
    else:
        scoreboard.ties += 1
        print("This round is a tie.")

    print(scoreboard.display())


def play_match() -> Scoreboard:
    scoreboard = Scoreboard(target_wins=get_target_wins())
    print("\nThe computer adapts if you repeat the same move too often.")

    while not scoreboard.match_over:
        print("\n" + "-" * 48)
        play_round(scoreboard)

    if scoreboard.player_wins > scoreboard.computer_wins:
        print("\nYou won the match! 🏆")
    else:
        print("\nThe computer won the match. Try changing your pattern!")
    return scoreboard


def wants_rematch() -> bool:
    while True:
        answer = input("Rematch? (y/n): ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer y or n.")


def main() -> None:
    print("=" * 48)
    print("       ADAPTIVE ROCK PAPER SCISSORS")
    print("=" * 48)

    while True:
        play_match()
        if not wants_rematch():
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
