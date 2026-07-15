"""Lease abstraction: extract key commercial terms into validated JSON.
 Uses structured output (a Pydantic schema),
so the model returns typed, validated data instead of free text.
"""

from pydantic import BaseModel, Field, field_validator
from pypdf import PdfReader

from lease_crew.config import get_chat_model


class Parties(BaseModel):
    landlord: str = Field(description="the landlord / lessor name")
    tenant: str = Field(description="the tenant / lessee name")


class BreakClause(BaseModel):
    earliest_termination: str = Field(
        description="when the tenant may first terminate early, e.g. 'end of year 4'"
    )
    notice_period: str = Field(description="required notice, e.g. '9 months'")


class LeaseAbstract(BaseModel):
    """Key commercial terms abstracted from a commercial lease."""

    parties: Parties
    premises: str = Field(description="the leased property or address")
    monthly_rent: float | None = Field(default=None, description="monthly rent as a number")
    rent_currency: str | None = Field(default=None, description="rent currency, e.g. SGD, USD")
    term_months: int | None = Field(default=None, description="total lease length in months")
    escalation: str | None = Field(default=None, description="rent escalation, e.g. '3.5% per annum'")
    security_deposit: str | None = Field(
        default=None, description="security deposit, e.g. '6 months gross rent'"
    )
    break_clause: BreakClause | None = Field(
        default=None, description="tenant's early-termination right; omit if the lease has none"
    )

    @field_validator("break_clause", mode="before")
    @classmethod
    def _blank_to_none(cls, v):
        # Models sometimes emit the string "null" for an absent nested object.
        if isinstance(v, str) and v.strip().lower() in {"null", "none", ""}:
            return None
        return v


def lease_text(pdf_path: str) -> str:
    """Read the full text of a lease PDF."""
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_lease_terms(text: str) -> LeaseAbstract:
    """Abstract a lease's full text into a validated LeaseAbstract."""
    extractor = get_chat_model().with_structured_output(LeaseAbstract)
    return extractor.invoke(
        "Extract the key commercial terms from this lease. "
        "If a term is genuinely absent, omit that field.\n\n" + text
    )
