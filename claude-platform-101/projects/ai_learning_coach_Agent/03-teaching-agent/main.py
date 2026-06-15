import os
import json
from anthropic import Anthropic, APIError, BadRequestError
from dotenv import load_dotenv



load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PROFILE_FILE = "profile.json"


def load_profile() -> dict:
    with open(PROFILE_FILE, "r") as file:
        profile = json.load(file)

    return profile

def build_system_prompt(profile:dict) -> str:
    level = profile.get("level","beginner")
    goal = profile.get("goal","machine learning")


    if level == "beginner":
        return f""" 
You are a friendly AI learning coach.

The user's level is beginner.
The user's goal is to learn {goal}.

Explain topics using:
- Simple words
- Step-by-step explanation
- Real-life examples
- No heavy technical jargon
- No advanced math unless necessary
"""
    
    elif level == "advanced":
        return f"""
You are an advanced AI learning coach.

The user's level is advanced.
The user's goal is to learn {goal}.

Explain topics using:
- Technical depth
- Correct terminology
- Mathematical intuition when useful
- Industry-level explanation
- Practical implementation details
"""

    else:
        return f"""
You are an AI learning coach.

The user's level is {level}.
The user's goal is to learn {goal}.

Adapt your explanation to the user's level and goal.
"""


def explain_topic(topic: str, profile:dict) -> str:
    system_prompt = build_system_prompt(profile)


    response = client.messages.create(
        model = "claude-sonnet-4-5",
        max_tokens=700,
        system = system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Explain {topic}.",
            }
        ]
    )

    return response.content[0].text

def show_profile(profile:dict):
    print("\n Current User Profile")
    print("--------------------")
    print(f"Level: {profile.get('level')}")
    print(f"Goal: {profile.get('goal')}")

def main():
    print("AI Learning Coach v2 - Teaching Your Agent")
    print("------------------------------------------")


    try:
        profile = load_profile()
        show_profile(profile)

        topic = input("\nEnter a topic you want to learn: ")


        if not topic.strip():
            print("Please enter a valid topic.")
            return
        

        explanation = explain_topic(topic, profile)

        print("\nClaude Explanation:\n")
        print(explanation)

    except FileNotFoundError:
        print("profile.json file not found. Please create profile.json first.")

    except BadRequestError as error:
        print("Bad request error.")
        print("Reason: ", error)

    except APIError as error:
        print("Anthropic API error")
        print("Reason:", error)
    
    except Exception as error:
        print("Unexpected error.")
        print("Reason: ", error)

if __name__ == "__main__":
    main()
