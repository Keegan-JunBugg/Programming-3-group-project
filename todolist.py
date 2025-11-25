"""
Simple OOP To-Do List
Features:
- Create tasks with title, optional note, priority, assignee
- List tasks (all or only incomplete)
- Mark tasks complete / incomplete
- Edit and remove tasks
- Save / load tasks to a JSON file
- Small CLI for demoing the features
short, readable, easy to explain.
"""

import json
from datetime import datetime
from typing import List, Optional

# ----- Model (represents a Task) -----
class Task:
    """A single to-do item."""
    def __init__(self, title: str, note: str = "", priority: int = 2, assignee: str = "Unassigned"):
        self.title = title                # short title of the task
        self.note = note                  # optional longer description
        self.priority = max(1, min(priority, 3))  # 1=high, 2=medium, 3=low (keeps value between 1 and 3)
        self.assignee = assignee          # who is responsible (useful for group projects)
        self.done = False                 # completion flag
        self.created_at = datetime.now().isoformat()  # timestamp (string) for simplicity

    def mark_done(self):
        """Mark the task as complete."""
        self.done = True

    def mark_undone(self):
        """Mark the task as not complete."""
        self.done = False

    def to_dict(self) -> dict:
        """Convert Task to a JSON-serializable dictionary."""
        return {
            "title": self.title,
            "note": self.note,
            "priority": self.priority,
            "assignee": self.assignee,
            "done": self.done,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Task":
        """Create a Task from a dictionary (used when loading)."""
        t = Task(data["title"], data.get("note", ""), data.get("priority", 2), data.get("assignee", "Unassigned"))
        t.done = data.get("done", False)
        t.created_at = data.get("created_at", datetime.now().isoformat())
        return t

    def __str__(self):
        status = "✓" if self.done else " "
        pr = {1: "High", 2: "Med", 3: "Low"}[self.priority]
        return f"[{status}] {self.title} (Priority: {pr}, Assignee: {self.assignee})"

# ----- Manager (handles a list of Tasks) -----
class ToDoList:
    """A container that manages multiple Task objects."""
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        """Add a Task object to the list."""
        self.tasks.append(task)

    def remove_task(self, index: int) -> bool:
        """Remove a task by index. Returns True if removed, False if index invalid."""
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            return True
        return False

    def get_tasks(self, show_completed: bool = True) -> List[Task]:
        """Return tasks. If show_completed is False, only return incomplete tasks."""
        if show_completed:
            return list(self.tasks)
        return [t for t in self.tasks if not t.done]

    def save(self, filename: str):
        """Save tasks to a file in JSON format."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)

    def load(self, filename: str):
        """Load tasks from a file (replaces current list)."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tasks = [Task.from_dict(d) for d in data]
        except FileNotFoundError:
            # If file does not exist, start with empty list (no error)
            self.tasks = []

    def edit_task(self, index: int, title: Optional[str] = None, note: Optional[str] = None,
                  priority: Optional[int] = None, assignee: Optional[str] = None) -> bool:
        """Edit fields of a task by index. Returns True if successful."""
        if 0 <= index < len(self.tasks):
            t = self.tasks[index]
            if title is not None:
                t.title = title
            if note is not None:
                t.note = note
            if priority is not None:
                t.priority = max(1, min(priority, 3))
            if assignee is not None:
                t.assignee = assignee
            return True
        return False

# ----- Small CLI for demonstration -----
def demo_cli():
    todo = ToDoList()
    filename = "tasks.json"
    todo.load(filename)

    def show_tasks(show_completed=True):
        tasks = todo.get_tasks(show_completed)
        if not tasks:
            print("No tasks to show.")
            return
        for i, t in enumerate(tasks):
            print(f"{i}. {t}")

    while True:
        print("\nCommands: add, list, list_pending, done, undone, edit, remove, save, exit")
        cmd = input("Enter command: ").strip().lower()

        if cmd == "add":
            title = input("Title: ").strip()
            note = input("Note (optional): ").strip()
            pr = input("Priority 1=High, 2=Med, 3=Low (default 2): ").strip() or "2"
            assignee = input("Assignee (default Unassigned): ").strip() or "Unassigned"
            try:
                pr_num = int(pr)
            except ValueError:
                pr_num = 2
            task = Task(title, note, pr_num, assignee)
            todo.add_task(task)
            print("Added:", task)

        elif cmd == "list":
            show_tasks(show_completed=True)

        elif cmd == "list_pending":
            show_tasks(show_completed=False)

        elif cmd == "done":
            idx = input("Index to mark done: ").strip()
            try:
                i = int(idx)
                tasks = todo.get_tasks(True)
                if 0 <= i < len(tasks):
                    # find actual index in master list
                    master_index = todo.tasks.index(tasks[i])
                    todo.tasks[master_index].mark_done()
                    print("Marked done:", todo.tasks[master_index])
                else:
                    print("Invalid index.")
            except ValueError:
                print("Please enter a number.")

        elif cmd == "undone":
            idx = input("Index to mark undone: ").strip()
            try:
                i = int(idx)
                tasks = todo.get_tasks(True)
                if 0 <= i < len(tasks):
                    master_index = todo.tasks.index(tasks[i])
                    todo.tasks[master_index].mark_undone()
                    print("Marked undone:", todo.tasks[master_index])
                else:
                    print("Invalid index.")
            except ValueError:
                print("Please enter a number.")

        elif cmd == "edit":
            idx = input("Index to edit: ").strip()
            try:
                i = int(idx)
                tasks = todo.get_tasks(True)
                if 0 <= i < len(tasks):
                    master_index = todo.tasks.index(tasks[i])
                    title = input("New title (leave blank to keep): ")
                    note = input("New note (leave blank to keep): ")
                    pr = input("New priority 1-3 (leave blank to keep): ")
                    assignee = input("New assignee (leave blank to keep): ")
                    todo.edit_task(master_index,
                                   title if title else None,
                                   note if note else None,
                                   int(pr) if pr else None,
                                   assignee if assignee else None)
                    print("Edited:", todo.tasks[master_index])
                else:
                    print("Invalid index.")
            except ValueError:
                print("Please enter numbers for index/priority when required.")

        elif cmd == "remove":
            idx = input("Index to remove: ").strip()
            try:
                i = int(idx)
                tasks = todo.get_tasks(True)
                if 0 <= i < len(tasks):
                    master_index = todo.tasks.index(tasks[i])
                    removed = todo.tasks[master_index]
                    todo.remove_task(master_index)
                    print("Removed:", removed)
                else:
                    print("Invalid index.")
            except ValueError:
                print("Please enter a number.")

        elif cmd == "save":
            todo.save(filename)
            print(f"Saved to {filename}.")

        elif cmd == "exit":
            todo.save(filename)
            print("Saved and exiting. Bye!")
            break

        else:
            print("Unknown command. Try again.")

if __name__ == "__main__":
    demo_cli(
