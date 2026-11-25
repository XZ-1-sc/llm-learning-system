CREATE TABLE diagnostic_results (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profile_id BIGINT NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL CHECK (total > 0),
    incorrect_question_ids TEXT[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (score BETWEEN 0 AND total)
);

CREATE INDEX diagnostic_results_profile_id_idx
    ON diagnostic_results (profile_id);