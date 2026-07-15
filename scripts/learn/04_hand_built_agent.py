"""A ReAct agent built by hand: model node -> tool node -> loop."""

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph

from lease_crew.config import get_chat_model
from lease_crew.state import State


@tool
def annual_rent(monthly_rent: float, months: int = 12) -> float:
    """Total rent over a number of months (default a full year)."""
    return monthly_rent * months


@tool
def cost_per_sqft(annual_rent: float, area_sqft: float) -> float:
    """Annual rent per square foot."""
    return annual_rent / area_sqft


tools = [annual_rent, cost_per_sqft]
tools_by_name = {t.name: t for t in tools}
model = get_chat_model().bind_tools(tools)


def call_model(state: State) -> dict:
    """Model node: reason about the messages so far (maybe emit tool calls)."""
    return {"messages": [model.invoke(state["messages"])]}


def run_tools(state: State) -> dict:
    """Tool node: execute every tool call on the latest AI message."""
    results = []
    for call in state["messages"][-1].tool_calls:
        output = tools_by_name[call["name"]].invoke(call["args"])
        results.append(ToolMessage(content=str(output), tool_call_id=call["id"]))
    return {"messages": results}


def should_continue(state: State) -> str:
    """Router: loop to the tools if the model asked for any, else finish."""
    return "tools" if state["messages"][-1].tool_calls else "end"


builder = StateGraph(State)
builder.add_node("model", call_model)
builder.add_node("tools", run_tools)
builder.add_edge(START, "model")
builder.add_conditional_edges("model", should_continue, {"tools": "tools", "end": END})
builder.add_edge("tools", "model")
graph = builder.compile()


if __name__ == "__main__":
    question = HumanMessage(
        "Our unit is 2,000 sqft at $6,000 per month. "
        "What is the annual cost per square foot?"
    )
    for state in graph.stream({"messages": [question]}, stream_mode="values"):
        state["messages"][-1].pretty_print()
