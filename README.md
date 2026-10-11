# Python Mini Projects

A collection of command-line projects I built while learning Python. Each project now goes beyond a basic tutorial exercise with reusable logic, input validation, clearer interfaces, and automated tests.

## Projects

### Number Guessing Challenge

`number_guesser.py` is the full version of the guessing game.

- easy, medium, and hard difficulty profiles
- proximity and warmer/colder feedback
- duplicate-guess prevention and guess history
- win rate, average guesses, and best-score statistics
- replay support without restarting the program

Run it with:

```powershell
python number_guesser.py
```

### Quick Guess

`Number_guessing.py` is a smaller object-oriented version that demonstrates how game logic can be separated from terminal input. It includes limited attempts, proximity hints, replay support, and a session score.

```powershell
python Number_guessing.py
```

### Adaptive Rock Paper Scissors

`Rock_paper_scissors.py` supports best-of matches and keeps a live scoreboard. After enough rounds, the computer sometimes counters the move the player uses most often, which rewards changing strategies.

```powershell
python Rock_paper_scissors.py
```

### Dice Lab

`game.py` understands standard dice notation such as `2d6`, `d20`, and `3d8+2`. It shows individual rolls, totals, theoretical ranges, expected averages, and an optional 10,000-roll probability simulation.

```powershell
python game.py
```

### Persistent Task Tracker

`task_tracker/task_tracker.py` stores tasks in a local JSON file. It supports priorities, categories, due dates, overdue status, filters, search, completion toggles, and guarded deletion.

```powershell
python task_tracker/task_tracker.py
```

The generated `task_tracker/tasks.json` file stays local and is ignored by Git.

## Tests

The projects use only the Python standard library. Run the test suite from the repository root:

```powershell
python -m unittest discover -s tests -v
```

## What I practiced

- functions, classes, dataclasses, and enums
- validation and error handling
- JSON persistence and file operations
- collections, probability, and randomization
- separating application logic from command-line input
- automated testing with `unittest`

## Development note

I created the original project ideas and core Python implementations as learning exercises. I used OpenAI Codex to help restructure and expand the programs, add larger feature sets, improve validation, and introduce automated tests.
