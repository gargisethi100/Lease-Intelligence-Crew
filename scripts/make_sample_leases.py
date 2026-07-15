"""Generate a few FICTIONAL commercial lease PDFs into data/leases/.

These are synthetic samples for testing the RAG pipeline. Replace or augment
them with real lease PDFs (e.g. SEC EDGAR exhibits) anytime — same pipeline.
Run:  .venv/Scripts/python scripts/make_sample_leases.py
"""

from pathlib import Path

from fpdf import FPDF

LEASES = [
    {
        "file": "marina_bay_tower.pdf",
        "title": "COMMERCIAL LEASE AGREEMENT - Marina Bay Tower",
        "body": """This Lease Agreement is made between Harbourfront Estates Pte Ltd ("Landlord") and Meridian Capital Advisors Pte Ltd ("Tenant").

1. PREMISES. Level 24, Marina Bay Tower, 10 Marina Boulevard, Singapore 018983, comprising 8,500 square feet of net lettable area.

2. TERM. Six (6) years commencing on 1 March 2025.

3. RENT. S$12.50 per square foot per month, payable monthly in advance.

4. RENT ESCALATION. The rent shall increase by 3.5% per annum on each anniversary of the commencement date.

5. SECURITY DEPOSIT. A deposit equal to six (6) months' gross rent shall be held by the Landlord.

6. BREAK CLAUSE. The Tenant may terminate this Lease at the end of the fourth (4th) year by giving not less than nine (9) months' prior written notice.""",
    },
    {
        "file": "orchard_central_tower.pdf",
        "title": "COMMERCIAL LEASE AGREEMENT - Orchard Central Tower",
        "body": """This Lease Agreement is made between Somerset Property Holdings Pte Ltd ("Landlord") and Bright Leaf Retail Pte Ltd ("Tenant").

1. PREMISES. Level 8, Orchard Central Tower, 181 Orchard Road, Singapore 238896, comprising 4,200 square feet.

2. TERM. Three (3) years commencing on 1 July 2024.

3. RENT. S$18.00 per square foot per month, payable monthly in advance.

4. RENT ESCALATION. The rent shall increase by 5.0% per annum on each anniversary of the commencement date.

5. SECURITY DEPOSIT. A deposit equal to three (3) months' gross rent.

6. TERMINATION. This Lease does not contain a break clause. The Tenant is committed for the full three-year term.""",
    },
    {
        "file": "raffles_place_plaza.pdf",
        "title": "COMMERCIAL LEASE AGREEMENT - Raffles Place Plaza",
        "body": """This Lease Agreement is made between Cecil Street Trustees Pte Ltd ("Landlord") and Northwind Legal LLP ("Tenant").

1. PREMISES. Level 31, Raffles Place Plaza, 2 Raffles Place, Singapore 048616, comprising 6,000 square feet of net lettable area.

2. TERM. Five (5) years commencing on 15 January 2026.

3. RENT. S$15.75 per square foot per month, payable monthly in advance.

4. RENT ESCALATION. The rent shall increase by 4.0% per annum on each anniversary of the commencement date.

5. SECURITY DEPOSIT. A deposit equal to four (4) months' gross rent.

6. BREAK CLAUSE. The Tenant may terminate this Lease at the end of the third (3rd) year by giving not less than six (6) months' prior written notice.""",
    },
]


def make_pdf(path: Path, title: str, body: str) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.multi_cell(0, 8, title)
    pdf.ln(3)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, body.strip())
    pdf.output(str(path))


if __name__ == "__main__":
    out_dir = Path("data/leases")
    out_dir.mkdir(parents=True, exist_ok=True)
    for lease in LEASES:
        make_pdf(out_dir / lease["file"], lease["title"], lease["body"])
        print("wrote", lease["file"])
