"""Supervisor graph: routes each question to the right specialist worker(s)."""

from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from lease_crew.agents import analyst, lease_expert, market_researcher
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


class Route(BaseModel):
    """Who should act next, or FINISH when the question is answered."""

    next: Literal["lease_expert", "analyst", "market_researcher", "FINISH"]


def supervisor(state: State) -> dict:
    # Safety rail: bound coordination so a confused supervisor can't loop forever.
    worker_turns = sum(1 for m in state["messages"] if getattr(m, "name", None) in MEMBERS)
    if worker_turns >= 3:
        return {"next": "FINISH"}
    messages = [{"role": "system", "content": SUPERVISOR_PROMPT}] + state["messages"]
    decision = get_chat_model().with_structured_output(Route).invoke(messages)
    return {"next": decision.next}


def make_worker(factory, name: str):
    agent = factory()  # build the scoped create_agent once

    def node(state: State) -> dict:
        result = agent.invoke({"messages": state["messages"]})
        return {"messages": [AIMessage(content=result["messages"][-1].content, name=name)]}

    return node


def build_graph():
    builder = StateGraph(State)
    builder.add_node("supervisor", supervisor)
    builder.add_node("lease_expert", make_worker(lease_expert, "lease_expert"))
    builder.add_node("analyst", make_worker(analyst, "analyst"))
    builder.add_node("market_researcher", make_worker(market_researcher, "market_researcher"))

    builder.add_edge(START, "supervisor")
    for member in MEMBERS:
        builder.add_edge(member, "supervisor")  # each worker reports back
    builder.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {**{m: m for m in MEMBERS}, "FINISH": END},
    )
    return builder.compile()
