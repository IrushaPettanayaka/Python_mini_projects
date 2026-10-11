"""Dice roller and probability summary tool."""

from __future__ import annotations

import random
import re
from collections import Counter
from dataclasses import dataclass


DICE_PATTERN = re.compile(r"^(?P<count>\d*)d(?P<sides>\d+)(?P<modifier>[+-]\d+)?$", re.I)


@dataclass(frozen=True)
class DiceExpression:
    count: int
    sides: int
    modifier: int = 0

    @property
    def minimum(self) -> int:
        return self.count + self.modifier

    @property
    def maximum(self) -> int:
        return self.count * self.sides + self.modifier

    @property
    def average(self) -> float:
        return self.count * (self.sides + 1) / 2 + self.modifier

    def label(self) -> str:
        suffix = f"{self.modifier:+d}" if self.modifier else ""
        return f"{self.count}d{self.sides}{suffix}"


def parse_expression(value: str) -> DiceExpression:
    """Parse notation such as 2d6, d20, or 3d8+2."""

    match = DICE_PATTERN.fullmatch(value.strip())
    if not match:
        raise ValueError("Use dice notation such as 2d6, d20, or 3d8+2.")

    count = int(match.group("count") or 1)
    sides = int(match.group("sides"))
    modifier = int(match.group("modifier") or 0)

    if not 1 <= count <= 100:
        raise ValueError("The number of dice must be between 1 and 100.")
    if not 2 <= sides <= 1000:
        raise ValueError("Each die must have between 2 and 1000 sides.")

    return DiceExpression(count, sides, modifier)


def roll(expression: DiceExpression, rng: random.Random | None = None) -> tuple[list[int], int]:
    """Roll an expression and return individual dice plus the adjusted total."""

    generator = rng or random.Random()
    dice = [generator.randint(1, expression.sides) for _ in range(expression.count)]
    return dice, sum(dice) + expression.modifier


def print_result(expression: DiceExpression, dice: list[int], total: int) -> None:
    values = ", ".join(str(value) for value in dice)
    print(f"\n{expression.label()}: [{values}]")
    if expression.modifier:
        print(f"Modifier: {expression.modifier:+d}")
    print(f"Total: {total}")


def run_simulation(expression: DiceExpression, trials: int = 10_000) -> None:
    """Estimate the result distribution and show the five common totals."""

    totals = Counter(roll(expression)[1] for _ in range(trials))
    measured_average = sum(total * count for total, count in totals.items()) / trials

    print(f"\nSimulation: {trials:,} rolls of {expression.label()}")
    print(f"Possible range: {expression.minimum} to {expression.maximum}")
    print(f"Expected average: {expression.average:.2f}")
    print(f"Simulated average: {measured_average:.2f}")
    print("Most common totals:")
    for total, count in totals.most_common(5):
        print(f"  {total:>4}: {count / trials:>6.1%}")


def read_expression() -> DiceExpression | None:
    while True:
        raw_value = input("\nDice (for example 2d6, 'help', or 'quit'): ").strip()
        if raw_value.lower() in {"q", "quit", "exit"}:
            return None
        if raw_value.lower() == "help":
            print("NdS rolls N dice with S sides. Add a modifier, such as 2d8+3.")
            continue
        try:
            return parse_expression(raw_value)
        except ValueError as error:
            print(error)


def main() -> None:
    print("Dice Lab")
    print("Roll standard or custom dice and inspect their probabilities.")

    while expression := read_expression():
        dice, total = roll(expression)
        print_result(expression, dice, total)

        simulate = input("Run a 10,000-roll simulation? (y/n): ").strip().lower()
        if simulate in {"y", "yes"}:
            run_simulation(expression)

    print("Thanks for using Dice Lab!")


if __name__ == "__main__":
    main()
