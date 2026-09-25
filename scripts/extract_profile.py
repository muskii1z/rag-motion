"""Step 6 demo: coach's plain English -> structured client profile.

Run from the project folder:
    uv run python scripts/extract_profile.py
    uv run python scripts/extract_profile.py "Your own client description here"
"""

import sys

import openai

from ragmotion.llm import extract_profile

# The example from the project brief. Fictional client.
DEFAULT_TEXT = (
    "I have a 42-year-old recreational runner. They can train three times per week "
    "for 30 minutes. They have dumbbells and resistance bands. Their goal is general strength."
)


def main() -> None:
    text = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEXT
    print(f"INPUT:\n  {text}\n")

    try:
        profile, usage = extract_profile(text)
    except openai.AuthenticationError:
        raise SystemExit("OpenRouter rejected the API key. Check OPENROUTER_API_KEY in .env.")
    except openai.RateLimitError:
        raise SystemExit("Rate limited or out of credit. Wait a moment or check your OpenRouter limit.")
    except openai.APIConnectionError as e:
        raise SystemExit(f"Could not reach OpenRouter: {e}")
    except openai.APIStatusError as e:
        raise SystemExit(f"OpenRouter returned HTTP {e.status_code}: {e.message}")

    print("PROFILE (validated by Pydantic):")
    print(profile.model_dump_json(indent=2))
    print(f"\nMISSING (computed in Python, not by the LLM): {profile.missing_fields() or 'none'}")

    cost = f"${usage.cost_usd:.6f}" if usage.cost_usd is not None else "not reported"
    print(f"\nUSAGE: model={usage.model}  input={usage.prompt_tokens} tokens  "
          f"output={usage.completion_tokens} tokens  cost={cost}")


if __name__ == "__main__":
    main()
