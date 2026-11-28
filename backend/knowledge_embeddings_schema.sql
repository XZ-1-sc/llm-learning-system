CREATE TABLE IF NOT EXISTS knowledge_passage_embeddings (
    embedding_model TEXT NOT NULL,
    passage_id TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL CHECK (vector_norm(embedding) > 0),
    PRIMARY KEY (embedding_model, passage_id)
);
