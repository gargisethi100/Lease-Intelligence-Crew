"""The same agent, prebuilt: create_agent wires the whole graph for you."""

from langchain.agents import create_agent
from langchain_core.tools import tool

from lease_crew.config import get_chat_model


@tool
def annual_rent(monthly_rent: float, months: int = 12) -> float:
    """Total rent over a number of months (default a full year)."""
    return monthly_rent * months


@tool
def cost_per_sqft(annual_rent: float, area_sqft: float) -> float:
    """Annual rent per square foot."""
    return annual_rent / area_sqft


agent = create_agent(get_chat_model(), tools=[annual_rent, cost_per_sqft])


if __name__ == "__main__":
    print("nodes create_agent built:", list(agent.get_graph().nodes))
    question = "Our unit is 2,000 sqft at $6,000 per month. What is the annual cost per square foot?"
    for state in agent.stream(
        {"messages": [{"role": "user", "content": question}]}, stream_mode="values"
    ):
        state["messages"][-1].pretty_print()
