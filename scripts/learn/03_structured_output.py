from pydantic import BaseModel, Field

from lease_crew.config import get_chat_model


class LeaseSummary(BaseModel):
    """Key commercial terms extracted from a lease."""

    tenant: str = Field(description="the tenant / lessee company name")
    landlord: str = Field(description="the landlord / lessor name")
    monthly_rent: float = Field(description="monthly rent amount, in dollars")
    term_months: int = Field(description="total lease length in months")
    has_break_clause: bool = Field(description="whether the tenant can terminate early")


LEASE_TEXT = """
This lease is made between Riverside Holdings LLC (Landlord) and
Acme Robotics Inc (Tenant). The premises at 200 Marina Blvd are let for a
term of three years. Rent is $8,000 per calendar month. The Tenant may
terminate early at the end of the second year on six months' notice.
"""

model = get_chat_model()
extractor = model.with_structured_output(LeaseSummary)

result = extractor.invoke(f"Extract the lease terms from this text:\n{LEASE_TEXT}")

print("returned type:", type(result).__name__)
print(result)
print("\ntyped, so real math works -> annual rent =", result.monthly_rent * 12)
