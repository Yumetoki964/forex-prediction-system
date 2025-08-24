-- Initial database setup for Forex Prediction System
-- ================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tables
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
    signal_type VARCHAR(10) NOT NULL, -- 'BUY', 'SELL', 'HOLD'
    confidence DECIMAL(5, 2),
    strength DECIMAL(5, 2),
    entry_price DECIMAL(10, 4),
    stop_loss DECIMAL(10, 4),
    take_profit DECIMAL(10, 4),
    risk_reward_ratio DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Technical indicators table
CREATE TABLE IF NOT EXISTS technical_indicators (
    id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(10) DEFAULT 'USD/JPY',
    date DATE NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    indicator_value DECIMAL(15, 4),
    signal VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(currency_pair, date, indicator_name)
);

-- Economic indicators table
CREATE TABLE IF NOT EXISTS economic_indicators (
    id SERIAL PRIMARY KEY,
    indicator_name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    date DATE NOT NULL,
    actual_value DECIMAL(15, 4),
    forecast_value DECIMAL(15, 4),
    previous_value DECIMAL(15, 4),
    impact_level VARCHAR(10), -- 'HIGH', 'MEDIUM', 'LOW'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backtest results table
CREATE TABLE IF NOT EXISTS backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15, 2),
    final_capital DECIMAL(15, 2),
    total_return DECIMAL(10, 2),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 2),
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate DECIMAL(5, 2),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    alert_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    severity VARCHAR(20), -- 'HIGH', 'MEDIUM', 'LOW', 'INFO'
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data sources table
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) UNIQUE NOT NULL,
    source_type VARCHAR(50), -- 'API', 'SCRAPER', 'FILE'
    base_url VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    last_sync TIMESTAMP,
    sync_frequency_hours INTEGER DEFAULT 24,
    configuration JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_exchange_rates_date ON exchange_rates(date DESC);
CREATE INDEX idx_exchange_rates_currency_date ON exchange_rates(currency_pair, date DESC);
CREATE INDEX idx_predictions_dates ON predictions(prediction_date, target_date);
CREATE INDEX idx_trading_signals_date ON trading_signals(signal_date DESC);
CREATE INDEX idx_technical_indicators_date ON technical_indicators(date DESC);
CREATE INDEX idx_economic_indicators_date ON economic_indicators(date DESC);
CREATE INDEX idx_alerts_user_read ON alerts(user_id, is_read);

-- Create update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exchange_rates_updated_at BEFORE UPDATE ON exchange_rates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_sources_updated_at BEFORE UPDATE ON data_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin_password)
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

-- Insert sample data sources
INSERT INTO data_sources (source_name, source_type, base_url, is_active, configuration)
VALUES 
    ('Yahoo Finance', 'API', 'https://finance.yahoo.com', true, '{"symbol": "USDJPY=X"}'),
    ('Alpha Vantage', 'API', 'https://www.alphavantage.co', false, '{"api_key": ""}'),
    ('Bank of Japan', 'SCRAPER', 'https://www.boj.or.jp', false, '{"frequency": "daily"}')
ON CONFLICT (source_name) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO forex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO forex_user;