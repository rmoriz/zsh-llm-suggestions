#!/usr/bin/env python3

import sys
import os

MISSING_PREREQUISITES = "zsh-llm-suggestions missing prerequisites:"


def highlight_explanation(explanation):
    try:
        import pygments
        from pygments.lexers import MarkdownLexer
        from pygments.formatters import TerminalFormatter

        return pygments.highlight(
            explanation, MarkdownLexer(), TerminalFormatter(style="material")
        )
    except ImportError:
        return explanation


def main():
    mode = sys.argv[1]
    if mode != "generate" and mode != "explain":
        print(
            "ERROR: something went wrong in zsh-llm-suggestions, please report a bug. Got unknown mode: "
            + mode
        )
        return

    try:
        import openai
    except ImportError:
        print(
            f'echo "{MISSING_PREREQUISITES} Install OpenAI Python API." && pip3 install openai'
        )
        return

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        print(
            f'echo "{MISSING_PREREQUISITES} OPENROUTER_API_KEY is not set." && export OPENROUTER_API_KEY="<copy from https://openrouter.ai/keys>"'
        )
        return

    base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-haiku:beta")

    client = openai.Client(
        api_key=api_key,
        base_url=base_url,
    )

    buffer = sys.stdin.read()
    system_message = """You are a zsh shell expert, please write a ZSH command that solves my problem.
You should only output the completed command, no need to include any other explanation."""
    if mode == "explain":
        system_message = """You are a zsh shell expert, please briefly explain how the given command works. Be as concise as possible. Use Markdown syntax for formatting."""
    message = [
        {
            "role": "system",
            "content": system_message,
        },
        {"role": "user", "content": buffer},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=message,
        temperature=0.2,
        max_tokens=1000,
        frequency_penalty=0.0,
    )
    result = response.choices[0].message.content
    if result is None:
        print("ERROR: No response from OpenRouter API")
        return
    result = result.strip()
    if mode == "generate":
        result = result.replace("```zsh", "").replace("```", "").strip()
        print(result)
    if mode == "explain":
        print(highlight_explanation(result))


if __name__ == "__main__":
    main()
