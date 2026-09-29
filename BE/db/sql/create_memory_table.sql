CREATE TABLE IF NOT EXISTS memory_messages (
    id SERIAL PRIMARY KEY,
    text TEXT,
    response TEXT,
    emotion TEXT,
    feedback TEXT,
    user_suggestion TEXT,
    cycle TEXT,
    subject Text,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
