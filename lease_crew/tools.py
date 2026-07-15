"""LangChain @tool adapters — thin wrappers over the provider-neutral core.

The core modules (retrieval, projection) stay framework-neutral so the MCP
server can reuse them too. This file adapts them to LangChain's tool interface.
"""

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from lease_crew.projection import project_rent as _project_rent
from lease_crew.retrieval import search_leases as _search_leases


@tool
def search_leases(query: str) -> str:
    """Search the commercial lease documents for passages relevant to a question."""
    return _search_leases(query)


@tool
def project_rent(monthly_rent: float, annual_increase_pct: float, years: int) -> list[dict]:
    """Project rent year by year from a monthly rent and an annual % escalation."""
    return _project_rent(monthly_rent, annual_increase_pct, years)


@tool
def cost_per_sqft(annual_rent: float, area_sqft: float) -> float:
    """Annual rent per square foot (annual_rent / area_sqft)."""
    return annual_rent / area_sqft


def get_market_search() -> TavilySearch:
    """Build the Tavily web-search tool (needs TAVILY_API_KEY).

    Built lazily — TavilySearch validates the key in its constructor, so
    importing this module must not construct it, or every import would
    require a Tavily key even to use the lease or math tools.
    """
    return TavilySearch(max_results=3, topic="general")
