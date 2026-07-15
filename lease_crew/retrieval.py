"""Retrieve relevant lease passages from the persistent Chroma store.

search_leases() is the provider-neutral core reused by both the LangChain
retrieval tool and the MCP server.
"""

from functools import lru_cache

from langchain_chroma import Chroma

from lease_crew.config import get_embeddings
from lease_crew.ingest import CHROMA_DIR, COLLECTION


@lru_cache(maxsize=1)
def _store() -> Chroma:
    # Reopen the SAME collection with the SAME embedding model used to build it.
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def search_leases(query: str, k: int = 4) -> str:
    """Search the lease documents; return the k most relevant passages with citations."""
    docs = _store().similarity_search(query, k=k)
    if not docs:
        return "No lease passages found."
    return "\n\n".join(
        f"[{d.metadata.get('source', '?')} p.{d.metadata.get('page', '?')}] {d.page_content}"
        for d in docs
    )
