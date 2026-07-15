"""Rent projection math (no LLM).

Provider-neutral core reused by the Analyst's tool and the MCP server.
"""


def project_rent(monthly_rent: float, annual_increase_pct: float, years: int) -> list[dict]:
    """Project rent year by year given an annual percentage escalation.

    Returns one row per year: {year, monthly_rent, annual_rent}.
    """
    rows = []
    rent = monthly_rent
    for year in range(1, years + 1):
        rows.append(
            {
                "year": year,
                "monthly_rent": round(rent, 2),
                "annual_rent": round(rent * 12, 2),
            }
        )
        rent *= 1 + annual_increase_pct / 100
    return rows
