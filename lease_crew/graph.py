"""Supervisor graph: routes each question to a specialist. The Analyst writes
Python and PAUSES for human approval (interrupt) before running it."""

import builtins
from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from pydantic import BaseModel

from lease_crew.agents import lease_expert, market_researcher
from lease_crew.config import get_chat_model
from lease_crew.state import State

MEMBERS = ["lease_expert", "analyst", "market_researcher"]

SUPERVISOR_PROMPT = (
    "You route a user's question to specialists:\n"
    "- lease_expert: facts from the lease documents.\n"
    "- analyst: rent math (projections, cost per square foot).\n"
    "- market_researcher: current market/vacancy/rent trends via web search.\n"
    "Route to the ONE specialist for the next unaddressed part of the question. "
    "When every part has been answered by the specialists, choose FINISH. "
    "Never route to a specialist that has already answered its part."
)

CODE_PROMPT = (
    "Write a short Python snippet that computes the answer to the user's request "
    "and assigns it to a variable named `answer`. Output ONLY the code — no "
    "explanation, no markdown fences."
)

# Restricted builtins for exec: enough for rent math, nothing that touches the
# system. The human approval is the primary guard; a real system also sandboxes.
SAFE = {n: getattr(builtins, n) for n in (
    "print range sum round min max abs len pow sorted enumerate zip "
    "float int str list dict tuple bool".split()
)}


class Route(BaseModel):
    next: Literal["lease_expert", "analyst", "market_researcher", "FINISH"]


def supervisor(state: State) -> dict:
    worker_turns = sum(1 for m in state["messages"] if getattr(m, "name", None) in MEMBERS)
    if worker_turns >= 3:  # safety rail: bound coordination
        return {"next": "FINISH"}
    messages = [{"role": "system", "content": SUPERVISOR_PROMPT}] + state["messages"]
    return {"next": get_chat_model().with_structured_output(Route).invoke(messages).next}


def make_worker(factory, name: str):
    agent = factory()

    def node(state: State) -> dict:
        result = agent.invoke({"messages": state["messages"]})
        return {"messages": [AIMessage(content=result["messages"][-1].content, name=name)]}

    return node


def analyst_node(state: State) -> dict:
    code = get_chat_model().invoke(
        [{"role": "system", "content": CODE_PROMPT}] + state["messages"]
    ).content.strip().removeprefix("```python").removeprefix("```").removesuffix("```").strip()

    decision = interrupt({"action": "run_python", "code": code})  # PAUSE for approval
    if str(decision).strip().lower() not in {"yes", "y", "approve"}:
        return {"messages": [AIMessage("Calculation not approved.", name="analyst")]}

    scope = {"__builtins__": SAFE}
    try:
        exec(code, scope)
        answer = scope.get("answer", "(the snippet set no `answer`)")
    except Exception as exc:
        answer = f"error running snippet: {exc}"
    return {"messages": [AIMessage(f"Result: {answer}", name="analyst")]}


def build_graph(checkpointer=None):
    builder = StateGraph(State)
    builder.add_node("supervisor", supervisor)
    builder.add_node("lease_expert", make_worker(lease_expert, "lease_expert"))
    builder.add_node("market_researcher", make_worker(market_researcher, "market_researcher"))
    builder.add_node("analyst", analyst_node)  # custom node so interrupt() propagates

    builder.add_edge(START, "supervisor")
    for member in MEMBERS:
        builder.add_edge(member, "supervisor")
    builder.add_conditional_edges(
        "supervisor", lambda s: s["next"], {**{m: m for m in MEMBERS}, "FINISH": END}
    )
    return builder.compile(checkpointer=checkpointer)
