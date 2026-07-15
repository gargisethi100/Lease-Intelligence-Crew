"""Message trimming: keep a bounded, recent window of a long conversation.

Once a chat runs many turns, sending the whole history every call costs
tokens, latency, and can blow the context window. trim_messages keeps the
most recent messages (plus the system prompt) and drops the older ones.
"""

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)

# A long conversation: a system prompt + five back-and-forth turns.
messages = [SystemMessage("You are a lease assistant.")]
for i in range(1, 6):
    messages.append(HumanMessage(f"Question {i}"))
    messages.append(AIMessage(f"Answer {i}"))

trimmed = trim_messages(
    messages,
    max_tokens=5,  # with token_counter=len this means "at most 5 messages"
    token_counter=len,  # count messages; use a model or count_tokens_approximately for real tokens
    strategy="last",  # keep the most recent
    include_system=True,  # always keep the system prompt
    start_on="human",  # the kept window should begin on a human turn
)

print(f"before: {len(messages)} messages")
print(f"after:  {len(trimmed)} messages")
for m in trimmed:
    print(f"  [{m.type}] {m.content}")
