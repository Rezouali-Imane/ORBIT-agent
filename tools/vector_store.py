import hashlib
import re

import numpy as np
from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector

from config import SUPABASE_DB_URL

COLLECTION_NAME = "orbit_documents_local"
EMBEDDING_DIMENSION = 384


class LocalHashEmbeddings(Embeddings):
    """Create deterministic lexical vectors without a separate model provider."""

    def _embed(self, text: str) -> list[float]:
        vector = np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)
        for token in re.findall(r"\w+", text.lower()):
            index = int.from_bytes(
                hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest(),
                "big",
            ) % EMBEDDING_DIMENSION
            vector[index] += 1.0
        norm = np.linalg.norm(vector)
        return (vector / norm if norm else vector).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def get_vector_store() -> PGVector:
    if not SUPABASE_DB_URL or not SUPABASE_DB_URL.startswith(
        ("postgresql://", "postgresql+psycopg://")
    ):
        raise ValueError(
            "SUPABASE_DB_URL must be a PostgreSQL connection string, "
            "such as postgresql+psycopg://..."
        )

    return PGVector(
        embeddings=LocalHashEmbeddings(),
        embedding_length=EMBEDDING_DIMENSION,
        collection_name=COLLECTION_NAME,
        connection=SUPABASE_DB_URL,
        use_jsonb=True,
    )
