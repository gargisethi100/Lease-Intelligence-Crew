"""MCP server exposing the crew's core capabilities as MCP tools.

The SAME core functions the LangGraph agents use, surfaced over the Model
Context Protocol so any MCP host (Claude Desktop, an IDE, another agent) can
call them — no reimplementation, just a second thin adapter over `core`.

Run (stdio):  .venv/Scripts/python mcp_server/server.py
Inspector:    mcp dev mcp_server/server.py
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from lease_crew.abstraction import extract_lease_terms as _extract
from lease_crew.abstraction import lease_text
from lease_crew.projection import project_rent as _project_rent
from lease_crew.retrieval import search_leases as _search_leases

mcp = FastMCP("lease-intelligence")


@mcp.tool()
def search_leases(query: str) -> str:
    """Search the commercial lease documents for passages relevant to a question."""
    return _search_leases(query)


@mcp.tool()
def extract_lease_terms(lease_file: str) -> dict:
    """Extract key commercial terms from a lease PDF as JSON.

    lease_file: a filename in data/leases, e.g. 'marina_bay_tower.pdf'.
    """
    text = lease_text(str(Path("data/leases") / lease_file))
    return _extract(text).model_dump()


@mcp.tool()
def project_rent(monthly_rent: float, annual_increase_pct: float, years: int) -> list[dict]:
    """Project rent year by year from a monthly rent and an annual % escalation."""
    return _project_rent(monthly_rent, annual_increase_pct, years)


if __name__ == "__main__":
    mcp.run()  # default transport: stdio
