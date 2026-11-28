import json
from collections.abc import Mapping, Sequence

from psycopg import Connection


EMBEDDING_DIMENSIONS = 384


def _vector_literal(embedding: Sequence[float]) -> str:
    if len(embedding) != EMBEDDING_DIMENSIONS or not any(embedding):
        raise ValueError(f"向量必须有 {EMBEDDING_DIMENSIONS} 维且不能全为零")
    return json.dumps(list(embedding), allow_nan=False, separators=(",", ":"))


def save_passage_embeddings(
    connection: Connection,
    embedding_model: str,
    embeddings: Mapping[str, Sequence[float]],
) -> None:
    rows = [
        (embedding_model, passage_id, _vector_literal(embedding))
        for passage_id, embedding in embeddings.items()
    ]
    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO knowledge_passage_embeddings (embedding_model, passage_id, embedding)
            VALUES (%s, %s, %s::vector)
            ON CONFLICT (embedding_model, passage_id)
            DO UPDATE SET embedding = EXCLUDED.embedding
            """,
            rows,
        )


def find_nearest_passages(
    connection: Connection,
    embedding_model: str,
    query_embedding: Sequence[float],
    limit: int = 3,
) -> list[tuple[str, float]]:
    return connection.execute(
        """
        SELECT passage_id, embedding <=> %s::vector AS distance
        FROM knowledge_passage_embeddings
        WHERE embedding_model = %s
        ORDER BY distance, passage_id
        LIMIT %s
        """,
        (_vector_literal(query_embedding), embedding_model, limit),
    ).fetchall()
