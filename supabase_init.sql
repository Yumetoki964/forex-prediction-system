-- Forex Prediction System - Supabase初期設定SQL
-- ================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exchange rates table
CREATE TABLE IF NOT EXISTS exchange_rates (
    id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(10) DEFAULT 'USD/JPY',
    date DATE NOT NULL,
    open_rate DECIMAL(10, 4),
    high_rate DECIMAL(10, 4),
    low_rate DECIMAL(10, 4),
    close_rate DECIMAL(10, 4) NOT NULL,
    volume BIGINT,
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(currency_pair, date, source)
);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(10) DEFAULT 'USD/JPY',
    prediction_date DATE NOT NULL,
    target_date DATE NOT NULL,
    predicted_rate DECIMAL(10, 4) NOT NULL,
    confidence_score DECIMAL(5, 2),
    model_type VARCHAR(50),
    model_version VARCHAR(20),
    actual_rate DECIMAL(10, 4),
    error_percentage DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(10) DEFAULT 'USD/JPY',
    signal_date DATE NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    confidence DECIMAL(5, 2),
    strength DECIMAL(5, 2),
    entry_price DECIMAL(10, 4),
    stop_loss DECIMAL(10, 4),
    take_profit DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default admin user (password: password)
-- パスワードハッシュは'password'のbcryptハッシュ
INSERT INTO users (username, email, password_hash, full_name, role, is_active, is_verified)
VALUES (
    'admin',
    'admin@forex.com',
    '$2b$12$LQYeVPIvLBqVGzLPep6o8OgGKvJLeGGfFpS1sC7OKQqWXxQJKvGDu',
    'System Administrator',
    'admin',
    true,
    true
) ON CONFLICT (username) DO NOTHING;

-- サンプルデータ（オプション）
INSERT INTO exchange_rates (currency_pair, date, open_rate, high_rate, low_rate, close_rate, volume, source)
VALUES 
    ('USD/JPY', CURRENT_DATE, 149.50, 150.20, 149.30, 149.85, 150000, 'sample'),
    ('USD/JPY', CURRENT_DATE - INTERVAL '1 day', 149.20, 149.80, 149.00, 149.50, 145000, 'sample'),
    ('USD/JPY', CURRENT_DATE - INTERVAL '2 days', 148.90, 149.40, 148.70, 149.20, 160000, 'sample')
ON CONFLICT (currency_pair, date, source) DO NOTHING;