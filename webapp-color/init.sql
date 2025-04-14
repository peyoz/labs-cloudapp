CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    hostname TEXT NOT NULL,
    content TEXT NOT NULL
);
