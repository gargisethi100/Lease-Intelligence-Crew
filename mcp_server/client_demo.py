"""A minimal MCP client: launch the server, discover its tools, call them.

Run:  .venv/Scripts/python mcp_server/client_demo.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# How to launch the server: the same Python, running server.py over stdio.
server = StdioServerParameters(command=sys.executable, args=["mcp_server/server.py"])


async def main() -> None:
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()  # capability handshake

            tools = await session.list_tools()
            print("discovered tools:", [t.name for t in tools.tools])

            projection = await session.call_tool(
                "project_rent",
                {"monthly_rent": 5000, "annual_increase_pct": 4, "years": 3},
            )
            print("\nproject_rent ->")
            print(" ", projection.content[0].text)

            leases = await session.call_tool(
                "search_leases", {"query": "break clause Marina Bay"}
            )
            print("\nsearch_leases ->")
            print(" ", leases.content[0].text[:180])


if __name__ == "__main__":
    asyncio.run(main())
