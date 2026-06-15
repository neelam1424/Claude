import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic, APIError, BadRequestError

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODELS = {
    "Haiku": "claude-haiku-4-5",
    "Sonnet": "claude-sonnet-4-6",
    "Opus": "claude-opus-4-8",
}


def ask_claude(model_name: str, model_id: str, topic: str) -> dict:
    prompt = f"""
Explain {topic} in simple beginner-friendly language.

Your answer should include:
1. Simple explanation
2. Real-life example
3. Why it matters
Keep the answer under 200 words.
"""

    start_time = time.time()

    response = client.messages.create(
        model=model_id,
        max_tokens=500,
        system="You are a beginner-friendly AI learning coach.",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    end_time = time.time()
    response_time = round(end_time - start_time, 2)

    output_text = response.content[0].text

    return {
        "model_name": model_name,
        "model_id": model_id,
        "response": output_text,
        "response_time": response_time,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }


def print_result(result: dict):
    print("\n" + "=" * 70)
    print(f"MODEL: {result['model_name']} ({result['model_id']})")
    print("=" * 70)

    print("\nClaude Response:\n")
    print(result["response"])

    print("\nPerformance:")
    print(f"Response Speed: {result['response_time']} seconds")
    print(f"Input Tokens: {result['input_tokens']}")
    print(f"Output Tokens: {result['output_tokens']}")
    print(f"Total Tokens: {result['total_tokens']}")


def compare_models(topic: str):
    results = []

    for model_name, model_id in MODELS.items():
        try:
            print(f"\nRunning {model_name}...")
            result = ask_claude(model_name, model_id, topic)
            results.append(result)
            print_result(result)

        except BadRequestError as error:
            print(f"\n{model_name} failed.")
            print("Reason:", error)

        except APIError as error:
            print(f"\nAPI error while running {model_name}.")
            print("Reason:", error)

        except Exception as error:
            print(f"\nUnexpected error while running {model_name}.")
            print("Reason:", error)

    if results:
        print_summary(results)


def print_summary(results: list):
    print("\n" + "#" * 70)
    print("MODEL COMPARISON SUMMARY")
    print("#" * 70)

    fastest = min(results, key=lambda x: x["response_time"])
    cheapest_tokens = min(results, key=lambda x: x["total_tokens"])
    longest_answer = max(results, key=lambda x: x["output_tokens"])

    print(f"\nFastest Model: {fastest['model_name']} - {fastest['response_time']} seconds")
    print(f"Lowest Token Usage: {cheapest_tokens['model_name']} - {cheapest_tokens['total_tokens']} tokens")
    print(f"Longest Answer: {longest_answer['model_name']} - {longest_answer['output_tokens']} output tokens")

    print("\nIndustry Meaning:")
    print("Haiku: Best for fast and cheaper simple tasks.")
    print("Sonnet: Best default choice for balanced quality and speed.")
    print("Opus: Best for complex reasoning, deeper explanations, and advanced tasks.")


def main():
    print("Claude Model Comparison Tool")
    print("----------------------------")

    topic = input("Enter a topic to explain: ")

    if not topic.strip():
        print("Please enter a valid topic.")
        return

    compare_models(topic)


if __name__ == "__main__":
    main()