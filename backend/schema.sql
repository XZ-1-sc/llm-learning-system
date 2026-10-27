CREATE TABLE learner_profiles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    python_level TEXT NOT NULL
        CHECK (python_level IN ('beginner', 'intermediate', 'advanced')),
    ai_level TEXT NOT NULL
        CHECK (ai_level IN ('beginner', 'intermediate', 'advanced')),
    learning_goal TEXT NOT NULL
        CHECK (char_length(learning_goal) BETWEEN 1 AND 200),
    weekly_hours INTEGER NOT NULL
        CHECK (weekly_hours BETWEEN 1 AND 168),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);