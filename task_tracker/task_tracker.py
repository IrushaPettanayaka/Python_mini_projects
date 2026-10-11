"""A persistent command-line task manager built with the Python standard library."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4


DATA_FILE = Path(__file__).with_name("tasks.json")
PRIORITIES = ("low", "medium", "high")


@dataclass
class Task:
    id: str
    title: str
    priority: str = "medium"
    category: str = "general"
    due_date: str | None = None
    completed: bool = False
    created_at: str = ""

    @classmethod
    def create(
        cls,
        title: str,
        priority: str = "medium",
        category: str = "general",
        due_date: str | None = None,
    ) -> "Task":
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Task title cannot be empty.")
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}.")
        if due_date:
            parse_date(due_date)

        return cls(
            id=uuid4().hex[:8],
            title=clean_title,
            priority=priority,
            category=category.strip() or "general",
            due_date=due_date,
            created_at=datetime.now().isoformat(timespec="seconds"),
        )

    @property
    def is_overdue(self) -> bool:
        return bool(
            self.due_date
            and not self.completed
            and parse_date(self.due_date) < date.today()
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Task":
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            priority=str(data.get("priority", "medium")),
            category=str(data.get("category", "general")),
            due_date=str(data["due_date"]) if data.get("due_date") else None,
            completed=bool(data.get("completed", False)),
            created_at=str(data.get("created_at", "")),
        )


class TaskStore:
    """Manage tasks and save every mutation to a JSON file."""

    def __init__(self, path: Path = DATA_FILE) -> None:
        self.path = path
        self.tasks: list[Task] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.tasks = []
            return

        try:
            raw_tasks = json.loads(self.path.read_text(encoding="utf-8"))
            self.tasks = [Task.from_dict(item) for item in raw_tasks]
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            backup = self.path.with_suffix(".invalid.json")
            self.path.replace(backup)
            self.tasks = []
            print(f"Could not read task data ({error}). Moved it to {backup.name}.")

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(task) for task in self.tasks]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add(self, task: Task) -> None:
        self.tasks.append(task)
        self.save()

    def delete(self, task_id: str) -> Task:
        task = self.get(task_id)
        self.tasks.remove(task)
        self.save()
        return task

    def toggle_complete(self, task_id: str) -> Task:
        task = self.get(task_id)
        task.completed = not task.completed
        self.save()
        return task

    def get(self, task_id: str) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise LookupError("Task not found.")

    def filtered(
        self,
        status: str = "all",
        search: str = "",
    ) -> list[Task]:
        matches = self.tasks
        if status == "pending":
            matches = [task for task in matches if not task.completed]
        elif status == "completed":
            matches = [task for task in matches if task.completed]

        query = search.casefold().strip()
        if query:
            matches = [
                task
                for task in matches
                if query in task.title.casefold() or query in task.category.casefold()
            ]

        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            matches,
            key=lambda task: (
                task.completed,
                task.due_date or "9999-12-31",
                priority_order.get(task.priority, 3),
                task.title.casefold(),
            ),
        )

    def summary(self) -> dict[str, int]:
        completed = sum(task.completed for task in self.tasks)
        overdue = sum(task.is_overdue for task in self.tasks)
        return {
            "total": len(self.tasks),
            "pending": len(self.tasks) - completed,
            "completed": completed,
            "overdue": overdue,
        }


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Use a date in YYYY-MM-DD format.") from error


def shorten(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    return value[: width - 1] + "…"


def print_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("\nNo matching tasks.")
        return

    print("\n #  Status  Priority  Due date    Category       Task")
    print("-" * 76)
    for number, task in enumerate(tasks, start=1):
        status = "Done" if task.completed else "Late" if task.is_overdue else "Open"
        due_date = task.due_date or "—"
        print(
            f"{number:>2}  {status:<6}  {task.priority.title():<8}  "
            f"{due_date:<10}  {shorten(task.category, 12):<12}  "
            f"{shorten(task.title, 30)}"
        )


def choose_task(tasks: list[Task], action: str) -> Task | None:
    print_tasks(tasks)
    if not tasks:
        return None

    while True:
        raw_value = input(f"Task number to {action} (blank to cancel): ").strip()
        if not raw_value:
            return None
        try:
            number = int(raw_value)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if 1 <= number <= len(tasks):
            return tasks[number - 1]
        print("That task number is not in the list.")


def read_priority() -> str:
    while True:
        value = input("Priority — low, medium, or high [medium]: ").strip().lower()
        if not value:
            return "medium"
        if value in PRIORITIES:
            return value
        print("Choose low, medium, or high.")


def read_due_date() -> str | None:
    while True:
        value = input("Due date in YYYY-MM-DD (optional): ").strip()
        if not value:
            return None
        try:
            parse_date(value)
            return value
        except ValueError as error:
            print(error)


def add_task(store: TaskStore) -> None:
    title = input("Task title: ").strip()
    if not title:
        print("Task title cannot be empty.")
        return

    category = input("Category [general]: ").strip() or "general"
    task = Task.create(
        title=title,
        category=category,
        priority=read_priority(),
        due_date=read_due_date(),
    )
    store.add(task)
    print(f"Added '{task.title}'.")


def show_filtered_tasks(store: TaskStore) -> None:
    print("\nView: 1) all  2) pending  3) completed")
    choice = input("Choose a view [1]: ").strip() or "1"
    statuses = {"1": "all", "2": "pending", "3": "completed"}
    status = statuses.get(choice)
    if status is None:
        print("Unknown view.")
        return
    print_tasks(store.filtered(status=status))


def search_tasks(store: TaskStore) -> None:
    query = input("Search title or category: ").strip()
    print_tasks(store.filtered(search=query))


def toggle_task(store: TaskStore) -> None:
    tasks = store.filtered()
    task = choose_task(tasks, "toggle")
    if task is None:
        return
    updated = store.toggle_complete(task.id)
    state = "completed" if updated.completed else "pending"
    print(f"'{updated.title}' is now {state}.")


def delete_task(store: TaskStore) -> None:
    tasks = store.filtered()
    task = choose_task(tasks, "delete")
    if task is None:
        return

    confirmation = input(f"Delete '{task.title}'? (y/n): ").strip().lower()
    if confirmation in {"y", "yes"}:
        store.delete(task.id)
        print("Task deleted.")
    else:
        print("Deletion cancelled.")


def print_dashboard(store: TaskStore) -> None:
    summary = store.summary()
    print("\n" + "=" * 52)
    print("TASK TRACKER")
    print(
        f"{summary['pending']} pending  |  {summary['completed']} completed  "
        f"|  {summary['overdue']} overdue"
    )
    print("=" * 52)


def display_menu() -> None:
    store = TaskStore()
    actions = {
        "1": show_filtered_tasks,
        "2": add_task,
        "3": toggle_task,
        "4": delete_task,
        "5": search_tasks,
    }

    while True:
        print_dashboard(store)
        print("1. View tasks")
        print("2. Add task")
        print("3. Complete or reopen task")
        print("4. Delete task")
        print("5. Search tasks")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "6":
            print("Your tasks are saved. Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("Choose a number from 1 to 6.")
            continue
        action(store)


if __name__ == "__main__":
    display_menu()
