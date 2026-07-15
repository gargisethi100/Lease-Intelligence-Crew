"""Phase 0 smoke test: one real LLM call through the provider-agnostic factory.

Run:  .venv/Scripts/python scripts/hello_provider.py

A successful run does two things:
  1. Prints a model reply below.
  2. Appears as a traced run in your LangSmith project.
"""

import os

from langchain_core.messages import HumanMessage, SystemMessage

from lease_crew.config import get_chat_model


def main():
    print(f"Calling provider: {os.getenv('PROVIDER', 'azure')}")

    model = get_chat_model()
    messages = [
        SystemMessage("You are a concise assistant for a commercial real estate team."),
        HumanMessage("In one sentence, what is a break clause in a commercial lease?"),
    ]
    reply = model.invoke(messages)

    print("\n--- Reply ---")
    print(reply.content)
    print("\nDone. Open your LangSmith project to see this run traced.")


if __name__ == "__main__":
    main()
