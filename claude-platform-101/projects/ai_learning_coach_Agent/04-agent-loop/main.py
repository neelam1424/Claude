import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic, APIError, BadRequestError

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

STATE_FILE = "agent_state.json"


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "goal": "",
            "roadmap": [],
            "tasks": [],
            "completed_tasks": []
        }


def save_state(state: dict):
    with open(STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)


def call_claude(prompt: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system="""
You are an AI Study Planner Agent.

Your job is to help students learn complex topics using a clear plan.

You follow this loop:
1. Observe the user's goal or current progress.
2. Think about what the user needs next.
3. Act by creating roadmaps, tasks, or progress feedback.

Keep explanations simple, practical, and beginner-friendly.
""",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return response.content[0].text


def observe_user_goal(user_input: str) -> str:
    print("\nOBSERVE")
    print("Agent is reading the user's goal...")

    prompt = f"""
Observe this user goal:

"{user_input}"

Extract the main learning goal in one short sentence.
"""

    return call_claude(prompt)


def think_create_roadmap(goal: str) -> str:
    print("\nTHINK")
    print("Agent is planning the learning roadmap...")

    prompt = f"""
The user goal is:

"{goal}"

Create a beginner-friendly roadmap with 5 phases.

For each phase, include:
- Phase name
- What the user should learn
- Why it matters

Keep it clear and practical.
"""

    return call_claude(prompt)


def act_generate_tasks(goal: str, roadmap: str) -> str:
    print("\nACT")
    print("Agent is generating study tasks...")

    prompt = f"""
The user wants to achieve this goal:

"{goal}"

Here is the roadmap:

{roadmap}

Create 7 practical study tasks for the user.

Each task should be:
- Specific
- Beginner-friendly
- Actionable
- Useful for GitHub or portfolio building if possible
"""

    return call_claude(prompt)


def observe_progress(state: dict) -> str:
    print("\nOBSERVE")
    print("Agent is checking current progress...")

    total_tasks = len(state["tasks"])
    completed_tasks = len(state["completed_tasks"])

    return f"You have completed {completed_tasks} out of {total_tasks} tasks."


def think_next_step(state: dict) -> str:
    print("\nTHINK")
    print("Agent is deciding the next best step...")

    prompt = f"""
The user's goal is:

{state["goal"]}

Tasks:
{state["tasks"]}

Completed tasks:
{state["completed_tasks"]}

Suggest the next best study step in simple language.
"""

    return call_claude(prompt)


def split_tasks(tasks_text: str) -> list:
    lines = tasks_text.split("\n")
    tasks = []

    for line in lines:
        clean_line = line.strip()

        if clean_line and any(char.isdigit() for char in clean_line[:3]):
            tasks.append(clean_line)

    if not tasks:
        tasks = [tasks_text]

    return tasks


def start_new_plan(state: dict):
    user_input = input("\nWhat do you want to learn? ")

    if not user_input.strip():
        print("Please enter a valid learning goal.")
        return

    goal = observe_user_goal(user_input)
    roadmap = think_create_roadmap(goal)
    tasks_text = act_generate_tasks(goal, roadmap)

    tasks = split_tasks(tasks_text)

    state["goal"] = goal
    state["roadmap"] = roadmap
    state["tasks"] = tasks
    state["completed_tasks"] = []

    save_state(state)

    print("\n" + "=" * 70)
    print("YOUR STUDY PLAN")
    print("=" * 70)

    print("\nGoal:")
    print(goal)

    print("\nRoadmap:")
    print(roadmap)

    print("\nTasks:")
    print(tasks_text)


def show_progress(state: dict):
    if not state["goal"]:
        print("\nNo study plan found. Create a new plan first.")
        return

    progress = observe_progress(state)
    next_step = think_next_step(state)

    print("\n" + "=" * 70)
    print("PROGRESS CHECK")
    print("=" * 70)

    print("\nProgress:")
    print(progress)

    print("\nNext Best Step:")
    print(next_step)


def mark_task_complete(state: dict):
    if not state["tasks"]:
        print("\nNo tasks found. Create a study plan first.")
        return

    print("\nYour Tasks:")
    for index, task in enumerate(state["tasks"], start=1):
        status = "DONE" if task in state["completed_tasks"] else "PENDING"
        print(f"{index}. [{status}] {task}")

    choice = input("\nEnter task number to mark complete: ")

    if not choice.isdigit():
        print("Please enter a valid number.")
        return

    task_index = int(choice) - 1

    if task_index < 0 or task_index >= len(state["tasks"]):
        print("Invalid task number.")
        return

    selected_task = state["tasks"][task_index]

    if selected_task not in state["completed_tasks"]:
        state["completed_tasks"].append(selected_task)
        save_state(state)
        print("\nTask marked as complete.")
    else:
        print("\nTask is already completed.")


def main():
    state = load_state()

    while True:
        print("\nAI Study Planner Agent")
        print("----------------------")
        print("1. Create new study plan")
        print("2. Check progress")
        print("3. Mark task complete")
        print("4. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            start_new_plan(state)
        elif choice == "2":
            show_progress(state)
        elif choice == "3":
            mark_task_complete(state)
        elif choice == "4":
            print("Goodbye. Keep learning!")
            break
        else:
            print("Invalid choice. Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    try:
        main()
    except BadRequestError as error:
        print("Bad request error.")
        print("Reason:", error)
    except APIError as error:
        print("Anthropic API error.")
        print("Reason:", error)
    except Exception as error:
        print("Unexpected error.")
        print("Reason:", error)