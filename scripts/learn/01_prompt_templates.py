

from langchain_core.prompts import ChatPromptTemplate

from lease_crew.config import get_chat_model

# A template: a fixed system role + a human message with a {clause} placeholder.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a concise assistant for a commercial real estate team."),
        ("human", "In one sentence, explain the '{clause}' clause in a commercial lease."),
    ]
)


filled = prompt.invoke({"clause": "break"})
print("--- expanded messages ---")
for m in filled.messages:
    print(f"[{m.type}] {m.content}")

# 2) Pipe the template into the model to form a chain, then run it.
model = get_chat_model()
chain = prompt | model

print("\n--- reply: break ---")
print(chain.invoke({"clause": "break"}).content)

# 3) Reuse the SAME chain with a different value — that is the whole point.
print("\n--- reply: rent review ---")
print(chain.invoke({"clause": "rent review"}).content)
