from langchain_core.documents import Document

import tools.doc_search as doc_search


class FakeVectorStore:
    def __init__(self, matches):
        self.matches = matches

    def similarity_search_with_relevance_scores(self, query, k):
        return self.matches[:k]


def test_search_returns_passage_for_answerable_question(monkeypatch):
    store = FakeVectorStore(
        [
            (
                Document(
                    page_content="ORBIT uses a manager agent to coordinate specialists.",
                    metadata={"document_name": "architecture.md", "page_number": 1},
                ),
                0.91,
            )
        ]
    )
    monkeypatch.setattr(doc_search, "get_vector_store", lambda: store)

    result = doc_search.search_my_documents.invoke(
        {"query": "How does ORBIT coordinate specialists?"}
    )

    assert "architecture.md" in result
    assert "Page: 1" in result
    assert "manager agent" in result


def test_search_rejects_unanswerable_question(monkeypatch):
    store = FakeVectorStore(
        [
            (
                Document(
                    page_content="ORBIT uses Python.",
                    metadata={"document_name": "architecture.md", "page_number": 1},
                ),
                0.20,
            )
        ]
    )
    monkeypatch.setattr(doc_search, "get_vector_store", lambda: store)

    result = doc_search.search_my_documents.invoke(
        {"query": "What is the office temperature in Paris?"}
    )

    assert result == doc_search.NO_RELEVANT_DOCUMENTS
