"""Tests for the reusable logic behind the command-line projects."""

import random
import tempfile
import unittest
from pathlib import Path

from Number_guessing import GuessingRound
from Rock_paper_scissors import Choice, Scoreboard, determine_winner
from game import DiceExpression, parse_expression, roll
from number_guesser import DIFFICULTIES, GuessingGame, SessionStats
from task_tracker.task_tracker import Task, TaskStore


class QuickGuessTests(unittest.TestCase):
    def test_feedback_and_attempt_count(self):
        game = GuessingRound(secret=50, attempts_allowed=4)
        self.assertEqual(game.submit(10), "too low")
        self.assertEqual(game.submit(47), "very close")
        self.assertEqual(game.attempts_left, 2)

    def test_correct_guess_finishes_round(self):
        game = GuessingRound(secret=25)
        self.assertEqual(game.submit(25), "correct")
        self.assertTrue(game.is_over)


class NumberChallengeTests(unittest.TestCase):
    def test_game_tracks_unique_guesses(self):
        game = GuessingGame(DIFFICULTIES["medium"], secret_number=70)
        result = game.submit_guess(20)
        self.assertEqual(result.feedback, "Too low")
        with self.assertRaises(ValueError):
            game.submit_guess(20)

    def test_session_stats_records_a_win(self):
        game = GuessingGame(DIFFICULTIES["easy"], secret_number=10)
        game.submit_guess(4)
        game.submit_guess(10)
        stats = SessionStats()
        stats.record(game)
        self.assertEqual(stats.games_won, 1)
        self.assertEqual(stats.best_score, 2)


class DiceLabTests(unittest.TestCase):
    def test_parse_dice_expression(self):
        self.assertEqual(parse_expression("2d8+3"), DiceExpression(2, 8, 3))
        self.assertEqual(parse_expression("d20"), DiceExpression(1, 20, 0))

    def test_roll_uses_expression_and_modifier(self):
        dice, total = roll(DiceExpression(3, 6, 2), random.Random(7))
        self.assertEqual(len(dice), 3)
        self.assertEqual(total, sum(dice) + 2)
        self.assertTrue(all(1 <= value <= 6 for value in dice))

    def test_rejects_invalid_notation(self):
        with self.assertRaises(ValueError):
            parse_expression("two dice")


class RockPaperScissorsTests(unittest.TestCase):
    def test_all_player_winning_pairs(self):
        self.assertEqual(determine_winner(Choice.PAPER, Choice.ROCK), "player")
        self.assertEqual(determine_winner(Choice.ROCK, Choice.SCISSORS), "player")
        self.assertEqual(determine_winner(Choice.SCISSORS, Choice.PAPER), "player")

    def test_scoreboard_knows_when_match_is_over(self):
        scoreboard = Scoreboard(target_wins=2, player_wins=2)
        self.assertTrue(scoreboard.match_over)


class TaskTrackerTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(
            dir=Path(__file__).parent
        )
        self.store = TaskStore(Path(self.temporary_directory.name) / "tasks.json")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_tasks_persist_between_store_instances(self):
        self.store.add(Task.create("Write project README", priority="high"))
        reloaded = TaskStore(self.store.path)
        self.assertEqual(reloaded.tasks[0].title, "Write project README")
        self.assertEqual(reloaded.tasks[0].priority, "high")

    def test_filter_toggle_and_delete(self):
        task = Task.create("Practice Python", category="learning")
        self.store.add(task)
        self.assertEqual(self.store.filtered(search="learn"), [task])
        self.store.toggle_complete(task.id)
        self.assertEqual(self.store.summary()["completed"], 1)
        self.store.delete(task.id)
        self.assertEqual(self.store.summary()["total"], 0)


if __name__ == "__main__":
    unittest.main()
