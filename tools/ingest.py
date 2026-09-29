from __future__ import annotations

import hashlib
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from tools.vector_store import get_vector_store

DOCS_DIR = Path(__file__).resolve().parents[1] / "data" / "docs"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SUPPORTED_SUFFIXES = {".pdf", ".md", ".txt"}


def _read_documents() -> list[Document]:
    documents: list[Document] = []
    for path in sorted(DOCS_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        document_name = path.name
        if path.suffix.lower() == ".pdf":
            for page_number, page in enumerate(PdfReader(str(path)).pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "document_name": document_name,
                                "page_number": page_number,
                            },
                        )
                    )
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "document_name": document_name,
                            "page_number": 1,
                        },
                    )
                )
    return documents


def _chunk_documents(documents: list[Document]) -> tuple[list[Document], list[str]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)
    ids: list[str] = []
    for chunk_number, chunk in enumerate(chunks):
        identity = (
            f"{chunk.metadata['document_name']}|"
            f"{chunk.metadata['page_number']}|{chunk_number}|{chunk.page_content}"
        )
        ids.append(hashlib.sha256(identity.encode("utf-8")).hexdigest())
    return chunks, ids


def ingest_documents() -> int:
    documents = _read_documents()
    if not documents:
        return 0

    chunks, ids = _chunk_documents(documents)
    get_vector_store().add_documents(chunks, ids=ids)
    return len(chunks)


if __name__ == "__main__":
    count = ingest_documents()
    print(f"Ingested {count} document chunks.")
