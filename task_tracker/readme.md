# Persistent Task Tracker

A standard-library command-line task manager that saves its data between sessions.

## Features

- add tasks with a title, category, priority, and optional due date
- view all, pending, or completed tasks
- automatically identify overdue tasks
- search by title or category
- mark tasks complete or reopen them
- confirm before deleting a task
- store data in a readable local JSON file
- recover safely if the data file becomes invalid

## Run

From the repository root:

```powershell
python task_tracker/task_tracker.py
```

Task data is stored in `task_tracker/tasks.json`. That file is ignored by Git so personal tasks are not committed.
