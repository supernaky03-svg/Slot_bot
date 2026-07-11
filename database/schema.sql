CREATE TABLE IF NOT EXISTS group_config (
    id SERIAL PRIMARY KEY,
    group_id BIGINT,
    min_bet BIGINT DEFAULT 100,
    max_bet BIGINT DEFAULT 5000000,
    daily_amount BIGINT DEFAULT 500,
    duration INT DEFAULT 60,
    is_paused BOOLEAN DEFAULT FALSE,
    is_running BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    balance BIGINT DEFAULT 0,
    highest_balance BIGINT DEFAULT 0,
    today_bet_times INT DEFAULT 0,
    today_betted_amount BIGINT DEFAULT 0,
    last_daily_claim DATE
);

CREATE TABLE IF NOT EXISTS round_history (
    id SERIAL PRIMARY KEY,
    group_id BIGINT,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default config row if not exists
INSERT INTO group_config (id) VALUES (1) ON CONFLICT DO NOTHING;

