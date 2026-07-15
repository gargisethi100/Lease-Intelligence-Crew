"""Shared graph state for the agent.

Every node receives this state and returns a partial update. The `messages`
field carries the add_messages reducer, so a node's returned messages are
APPENDED to the running conversation instead of overwriting it.
"""

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
