from __future__ import annotations

import hashlib
import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from tools.vector_store import get_vector_store


DOCS_DIR = Path(__file__).resolve().parents[1] / "data" / "docs"
MANIFEST_PATH = DOCS_DIR / ".manifest.json"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
MAX_FILE_SIZE = 20 * 1024 * 1024
SUPPORTED_SUFFIXES = {".pdf", ".md", ".txt"}


def _validate_file(path: Path) -> None:
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError("Unsupported file type. Only .pdf, .md, and .txt files are accepted.")
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File is too large. The maximum allowed size is 20 MB.")


def _content_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_manifest() -> dict[str, dict]:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _save_manifest(manifest: dict[str, dict]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _read_file(path: Path, content_hash: str) -> list[Document]:
    documents: list[Document] = []
    if path.suffix.lower() == ".pdf":
        for page_number, page in enumerate(PdfReader(str(path)).pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "document_name": path.name,
                            "page_number": page_number,
                            "content_hash": content_hash,
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
                        "document_name": path.name,
                        "page_number": 1,
                        "content_hash": content_hash,
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
            f"{chunk.metadata['content_hash']}|"
            f"{chunk.metadata['page_number']}|{chunk_number}|{chunk.page_content}"
        )
        ids.append(hashlib.sha256(identity.encode("utf-8")).hexdigest())
    return chunks, ids


def ingest_file(path: str | Path) -> str:
    """Validate, deduplicate, replace, and ingest one supported file."""
    file_path = Path(path)
    _validate_file(file_path)
    file_hash = _content_hash(file_path)
    manifest = _load_manifest()
    if any(entry["content_hash"] == file_hash for entry in manifest.values()):
        return f"Skipped {file_path.name}: this file content is already stored."

    previous = manifest.get(file_path.name)
    vector_store = get_vector_store()
    if previous is not None:
        vector_store.delete(ids=previous["chunk_ids"])

    chunks, ids = _chunk_documents(_read_file(file_path, file_hash))
    if chunks:
        vector_store.add_documents(chunks, ids=ids)
    manifest[file_path.name] = {
        "content_hash": file_hash,
        "chunk_ids": ids,
        "chunk_count": len(ids),
    }
    _save_manifest(manifest)
    action = "Replaced" if previous is not None else "Ingested"
    return f"{action} {file_path.name}: {len(ids)} chunks stored."


def ingest_documents() -> int:
    """Keep folder ingestion working by ingesting each supported file."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for path in sorted(DOCS_DIR.iterdir()):
        if path.is_file() and path.name != MANIFEST_PATH.name and path.suffix.lower() in SUPPORTED_SUFFIXES:
            result = ingest_file(path)
            if "chunks stored" in result:
                total += _load_manifest()[path.name]["chunk_count"]
    return total


if __name__ == "__main__":
    print(f"Ingested {ingest_documents()} document chunks.")
