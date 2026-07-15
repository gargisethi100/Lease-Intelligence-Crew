"""SQLite checkpointer: a conversation survives a full process restart.

Run twice as SEPARATE processes to prove it:
  python scripts/learn/07_sqlite_memory.py start    # pauses at the interrupt, exits
  python scripts/learn/07_sqlite_memory.py resume   # a NEW process resumes by thread_id
"""

import sys

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict

DB = "checkpoints.sqlite"
CONFIG = {"configurable": {"thread_id": "restart-demo"}}


class State(TypedDict):
    code: str
    result: str


def approve(state: State) -> dict:
    decision = interrupt({"question": "Run this code?", "code": state["code"]})
    return {"result": "APPROVED" if decision == "yes" else "REJECTED"}


def run_code(state: State) -> dict:
    if state["result"] != "APPROVED":
        return {"result": "skipped"}
    scope = {"__builtins__": {}, "sum": sum, "range": range, "round": round}
    exec(state["code"], scope)
    return {"result": str(scope.get("answer"))}


def make_graph(checkpointer):
    b = StateGraph(State)
    b.add_node("approve", approve)
    b.add_node("run_code", run_code)
    b.add_edge(START, "approve")
    b.add_edge("approve", "run_code")
    b.add_edge("run_code", END)
    return b.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    # from_conn_string is a CONTEXT MANAGER — must be used with `with`.
    with SqliteSaver.from_conn_string(DB) as checkpointer:
        graph = make_graph(checkpointer)
        if command == "start":
            paused = graph.invoke(
                {"code": "answer = round(sum(5000 * 1.04 ** y for y in range(3)), 2)"},
                CONFIG,
            )
            print("PAUSED, saved to", DB, "->", paused["__interrupt__"][0].value["code"])
        else:
            resumed = graph.invoke(Command(resume="yes"), CONFIG)
            print("RESUMED in a fresh process -> result:", resumed["result"])
