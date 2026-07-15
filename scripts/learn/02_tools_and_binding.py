from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from lease_crew.config import get_chat_model


@tool
def annual_rent(monthly_rent: float, months: int = 12) -> float:
    """Compute the total rent over a number of months (default a full year)."""
    return monthly_rent * months


model = get_chat_model()
model_with_tools = model.bind_tools([annual_rent])

question = HumanMessage("What is the annual rent if the monthly rent is 4500?")
ai_msg = model_with_tools.invoke([question])

print("--- what the model emitted ---")
print("content:", repr(ai_msg.content))
print("tool_calls:", ai_msg.tool_calls)

# The model asked us to run the function; WE execute it with its chosen args.
call = ai_msg.tool_calls[0]
result = annual_rent.invoke(call["args"])
print("\nwe ran the tool ->", result)

# Hand the result back as a ToolMessage (tied to the call id); model concludes.
tool_msg = ToolMessage(content=str(result), tool_call_id=call["id"])
final = model_with_tools.invoke([question, ai_msg, tool_msg])
print("\n--- final answer ---")
print(final.content)
