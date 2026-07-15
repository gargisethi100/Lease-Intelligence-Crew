"""Ingest lease PDFs into a persistent Chroma vector store.

Pipeline: load PDFs (one Document per page) -> split into chunks ->
embed each chunk -> persist to Chroma on disk.

Run after adding PDFs:  .venv/Scripts/python -m lease_crew.ingest
(Re-running appends; delete chroma_db/ to rebuild from scratch.)
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from lease_crew.config import get_embeddings

DATA_DIR = Path("data/leases")
CHROMA_DIR = "chroma_db"
COLLECTION = "leases"


def build_vector_store(pdfs: list[Path] | None = None) -> Chroma:
    if pdfs is None:
        pdfs = sorted(DATA_DIR.glob("*.pdf"))
    store = Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    for pdf in pdfs:
        pages = PyPDFLoader(str(pdf)).load()  # one Document per page (with metadata)
        chunks = splitter.split_documents(pages)  # carries source + page forward
        store.add_documents(chunks)  # embeds each chunk and persists it
        print(f"  {pdf.name}: {len(pages)} pages -> {len(chunks)} chunks", flush=True)
    return store


if __name__ == "__main__":
    build_vector_store()
    print("vector store ready in", CHROMA_DIR)
