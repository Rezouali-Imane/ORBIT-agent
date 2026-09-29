from pathlib import Path
import shutil

from langchain_core.tools import tool

from tools.ingest import (
    DOCS_DIR,
    MAX_FILE_SIZE,
    SUPPORTED_SUFFIXES,
    _load_manifest,
    _save_manifest,
    ingest_file,
)
from tools.vector_store import get_vector_store


@tool(
    "add_document",
    description="Copy a supported document into the library and ingest it into RAG.",
)
def add_document(file_path: str) -> str:
    """Copy and ingest a local .pdf, .md, or .txt document."""
    source = Path(file_path)
    if not source.is_file():
        return f"Document not found: {file_path}"
    if source.suffix.lower() not in SUPPORTED_SUFFIXES:
        return "Unsupported file type. Only .pdf, .md, and .txt files are accepted."
    if source.stat().st_size > MAX_FILE_SIZE:
        return "File is too large. The maximum allowed size is 20 MB."
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    destination = DOCS_DIR / source.name
    shutil.copy2(source, destination)
    result = ingest_file(destination)
    if result.startswith("Skipped") and destination.name not in _load_manifest():
        destination.unlink(missing_ok=True)
    return result


@tool("list_documents", description="List stored documents and their RAG chunk counts.")
def list_documents() -> str:
    """Return stored document names and chunk counts."""
    manifest = _load_manifest()
    if not manifest:
        return "No documents are stored."
    return "\n".join(
        f"{name}: {entry['chunk_count']} chunks"
        for name, entry in sorted(manifest.items())
    )


@tool(
    "remove_document",
    description="Remove one named document and its RAG chunks from the library.",
)
def remove_document(name: str) -> str:
    """Delete a document's vector chunks and manifest entry."""
    manifest = _load_manifest()
    entry = manifest.get(name)
    if entry is None:
        return f"Document not found: {name}"
    get_vector_store().delete(ids=entry["chunk_ids"])
    manifest.pop(name)
    _save_manifest(manifest)
    (DOCS_DIR / name).unlink(missing_ok=True)
    return f"Removed {name} and {entry['chunk_count']} chunks."
