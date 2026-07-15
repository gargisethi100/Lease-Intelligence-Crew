"""The three specialist worker agents, each a scoped create_agent."""

from langchain.agents import create_agent

from lease_crew.config import get_chat_model
from lease_crew.tools import cost_per_sqft, get_market_search, project_rent, search_leases

LEASE_EXPERT_PROMPT = (
    "You are a commercial lease expert. Use search_leases to find relevant "
    "passages, then answer ONLY from those passages and cite the source file. "
    "If the answer is not in the retrieved passages, say you don't know. "
    "Report only what the documents say — do NOT do calculations or "
    "projections; leave all math to the analyst."
)

ANALYST_PROMPT = (
    "You are a real estate financial analyst. Use the tools for any rent math "
    "(rent projections, cost per square foot); never do the arithmetic yourself. "
    "Do not ask for confirmation — compute directly and return the result."
)

MARKET_PROMPT = (
    "You are a market researcher. Use web search for current market context "
    "(vacancy, rents, trends), then summarize concisely and cite the sources."
)


def lease_expert():
    return create_agent(
        get_chat_model(), tools=[search_leases], system_prompt=LEASE_EXPERT_PROMPT
    )


def analyst():
    return create_agent(
        get_chat_model(),
        tools=[project_rent, cost_per_sqft],
        system_prompt=ANALYST_PROMPT,
    )


def market_researcher():
    return create_agent(
        get_chat_model(), tools=[get_market_search()], system_prompt=MARKET_PROMPT
    )
