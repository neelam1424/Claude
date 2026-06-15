import os
from dotenv import load_dotenv
from anthropic import Anthropic



load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def explain_topic(topic:str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=800,
        system= "You are a friendly AI learning coach. Explain topics in simple beginner language with examples.",
        messages=[{
            "role":"user",
            "content": f"Explain {topic} in simple language with one real-life example."
        }
        ],
    )

    return response.content[0].text


def main():
    print("AI Learning Coach v1")
    topic = input("Enter a topic you want to learn: ")


    if not topic.strip():
        print("Please enter a valid topic.")
        return
    
    explanation = explain_topic(topic)


    print("\n Claude Explanation: \n")
    print(explanation)


if __name__ == "__main__":
    main()