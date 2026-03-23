import os
import anthropic


def call_claude(model, system_prompt, user_prompt, max_tokens=4096, extended_thinking=False, thinking_budget=10000):
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        if extended_thinking:
            kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget,
            }

        response = client.messages.create(**kwargs)

        for block in response.content:
            if block.type == "text":
                return block.text

        return None

    except Exception as e:
        print(f"Error calling Claude: {e}")
        return None


if __name__ == "__main__":
    result = call_claude(
        model="claude-haiku-4-5-20251001",
        system_prompt="You are a helpful assistant.",
        user_prompt="Say hello.",
    )
    if result:
        print(f"Response: {result}")
    else:
        print("Failed to get a response. Check your ANTHROPIC_API_KEY.")
