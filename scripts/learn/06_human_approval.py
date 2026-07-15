"""Human-in-the-loop: pause for approval before running analyst code.

interrupt() pauses the graph and surfaces a payload to the caller; you resume
with Command(resume=<value>), which becomes interrupt()'s return value.
interrupt() REQUIRES a checkpointer + a thread_id to save and restore the pause.
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict


class State(TypedDict):
    code: str
    result: str


def approve(state: State) -> dict:
    # Pause here and ask the human. The graph stops until you resume;
    # the resume value becomes `decision`.
    decision = interrupt({"question": "Run this code?", "code": state["code"]})
    return {"result": "APPROVED" if decision == "yes" else "REJECTED"}


def run_code(state: State) -> dict:
    if state["result"] != "APPROVED":
        return {"result": "skipped (rejected by human)"}
    scope = {"__builtins__": {}, "sum": sum, "range": range, "round": round}
    exec(state["code"], scope)  # restricted namespace; the approval is the real guard
    return {"result": str(scope.get("answer"))}


builder = StateGraph(State)
builder.add_node("approve", approve)
builder.add_node("run_code", run_code)
builder.add_edge(START, "approve")
builder.add_edge("approve", "run_code")
builder.add_edge("run_code", END)

# interrupt() needs a checkpointer to persist the pause.
graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "demo-1"}}
    code = "answer = round(sum(5000 * 1.04 ** y for y in range(3)), 2)"

    paused = graph.invoke({"code": code}, config)
    print("PAUSED — awaiting approval:")
    print("  ", paused["__interrupt__"][0].value)

    resumed = graph.invoke(Command(resume="yes"), config)
    print("RESUMED — result:", resumed["result"])
