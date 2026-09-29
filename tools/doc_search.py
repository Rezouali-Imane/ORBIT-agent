from langchain_core.tools import tool

from tools.vector_store import get_vector_store

TOP_K = 2
MIN_RELEVANCE_SCORE = 0.40
NO_RELEVANT_DOCUMENTS = "NO_RELEVANT_DOCUMENTS"


@tool(
    "search_my_documents",
    description=(
        "Search the user's ingested documents for an answer. Answer only from "
        "the passages returned by this tool. If the tool returns "
        "NO_RELEVANT_DOCUMENTS, say exactly: I don't have this in my documents."
    ),
)
def search_my_documents(query: str) -> str:
    """Return the four most relevant document passages for a question."""
    matches = get_vector_store().similarity_search_with_relevance_scores(
        query,
        k=TOP_K,
    )
    if not matches or matches[0][1] < MIN_RELEVANCE_SCORE:
        return NO_RELEVANT_DOCUMENTS

    passages = []
    for document, _score in matches:
        passages.append(
            "Document: "
            f"{document.metadata.get('document_name', 'unknown')}\n"
            "Page: "
            f"{document.metadata.get('page_number', 'unknown')}\n"
            f"Text: {document.page_content[:700]}"
        )
    return "\n\n---\n\n".join(passages)
