"""Chat with the Lease Intelligence Crew.

Persistent memory via the SQLite checkpointer + a thread_id (pass one as an
argument to resume that conversation later). The Analyst pauses for your
approval before running any code.

Run:  .venv/Scripts/python -m lease_crew.cli [thread_id]
"""

import sys

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from lease_crew.graph import build_graph

DB = "checkpoints.sqlite"


def run_turn(graph, user_text: str, config: dict) -> None:
    payload = {"messages": [{"role": "user", "content": user_text}]}
    while True:
        result = graph.invoke(payload, config)
        interrupts = result.get("__interrupt__")
        if not interrupts:
            print("\nAssistant:", result["messages"][-1].content)
            return
        # The Analyst paused for approval. Show the code and ask.
        data = interrupts[0].value
        print("\n[APPROVAL NEEDED] The analyst wants to run this code:\n")
        print(data.get("code", data))
        payload = Command(resume=input("\nApprove? (yes/no): ").strip())


def main() -> None:
    thread_id = sys.argv[1] if len(sys.argv) > 1 else "default"
    config = {"configurable": {"thread_id": thread_id}}
    print(f"Lease Intelligence Crew — thread '{thread_id}'. Type 'exit' to quit.")
    with SqliteSaver.from_conn_string(DB) as checkpointer:
        graph = build_graph(checkpointer)
        while True:
            user = input("\nYou: ").strip()
            if user.lower() in {"exit", "quit"}:
                break
            run_turn(graph, user, config)


if __name__ == "__main__":
    main()
