-- 🏔️ Khabarovsk Forecast Buddy - Database Schema
-- SQL script to create all necessary tables in Supabase

-- ==========================================
-- 1. SALES DATA TABLE
-- ==========================================
-- Stores historical sales data from CSV uploads
CREATE TABLE IF NOT EXISTS sales_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sku_id VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    units_sold INTEGER NOT NULL CHECK (units_sold >= 0),
    revenue DECIMAL(10,2) NOT NULL CHECK (revenue >= 0),
    price DECIMAL(8,2) NOT NULL CHECK (price >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sales_data_sku_id ON sales_data(sku_id);
CREATE INDEX IF NOT EXISTS idx_sales_data_date ON sales_data(date);
CREATE INDEX IF NOT EXISTS idx_sales_data_sku_date ON sales_data(sku_id, date);

-- ==========================================
-- 2. FORECASTS TABLE
-- ==========================================
-- Stores generated forecasts from GigaChat AI
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sku_id VARCHAR(100) NOT NULL,
    forecast_type VARCHAR(20) NOT NULL CHECK (forecast_type IN ('7_days', '14_days', '30_days')),
    predicted_units INTEGER NOT NULL CHECK (predicted_units >= 0),
    predicted_revenue DECIMAL(10,2) NOT NULL CHECK (predicted_revenue >= 0),
    confidence_level DECIMAL(3,2) CHECK (confidence_level >= 0 AND confidence_level <= 1),
    ai_explanation TEXT,
    context_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_version VARCHAR(50) DEFAULT '1.0.0'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_forecasts_sku_id ON forecasts(sku_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_created_at ON forecasts(created_at);
CREATE INDEX IF NOT EXISTS idx_forecasts_type ON forecasts(forecast_type);

-- ==========================================
-- 3. CSV UPLOAD LOGS TABLE
-- ==========================================
-- Tracks CSV file uploads and processing results
CREATE TABLE IF NOT EXISTS csv_upload_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    rows_processed INTEGER NOT NULL DEFAULT 0,
    rows_inserted INTEGER NOT NULL DEFAULT 0,
    errors_count INTEGER NOT NULL DEFAULT 0,
    error_details JSONB,
    upload_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (upload_status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Index for tracking uploads
CREATE INDEX IF NOT EXISTS idx_csv_upload_logs_created_at ON csv_upload_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_csv_upload_logs_status ON csv_upload_logs(upload_status);

-- ==========================================
-- 4. API USAGE STATS TABLE
-- ==========================================
-- Tracks API usage and performance metrics
CREATE TABLE IF NOT EXISTS api_usage_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    gigachat_tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for analytics
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage_stats(created_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage_stats(endpoint);

-- ==========================================
-- 5. ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================
-- Enable RLS for security
ALTER TABLE sales_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE csv_upload_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage_stats ENABLE ROW LEVEL SECURITY;

-- Allow service role full access (for backend API)
CREATE POLICY "Allow service role full access on sales_data" ON sales_data
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on forecasts" ON forecasts
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on csv_upload_logs" ON csv_upload_logs
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on api_usage_stats" ON api_usage_stats
    FOR ALL USING (auth.role() = 'service_role');

-- Allow anon read access to some data (for frontend)
CREATE POLICY "Allow anon read access to sales_data" ON sales_data
    FOR SELECT USING (true);

CREATE POLICY "Allow anon read access to forecasts" ON forecasts
    FOR SELECT USING (true);

-- ==========================================
-- 6. FUNCTIONS FOR DATA MANAGEMENT
-- ==========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for sales_data
CREATE TRIGGER update_sales_data_updated_at
    BEFORE UPDATE ON sales_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to get sales summary for SKU
CREATE OR REPLACE FUNCTION get_sales_summary(sku_id_param VARCHAR)
RETURNS TABLE (
    total_revenue DECIMAL,
    total_units INTEGER,
    avg_price DECIMAL,
    first_sale_date DATE,
    last_sale_date DATE,
    total_days INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(SUM(s.revenue), 0)::DECIMAL as total_revenue,
        COALESCE(SUM(s.units_sold), 0)::INTEGER as total_units,
        COALESCE(AVG(s.price), 0)::DECIMAL as avg_price,
        MIN(s.date) as first_sale_date,
        MAX(s.date) as last_sale_date,
        COALESCE(EXTRACT(DAY FROM MAX(s.date) - MIN(s.date))::INTEGER, 0) as total_days
    FROM sales_data s
    WHERE s.sku_id = sku_id_param;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- 7. SAMPLE DATA (OPTIONAL)
-- ==========================================
-- Insert some sample data for testing
INSERT INTO sales_data (sku_id, date, units_sold, revenue, price) VALUES
    ('DOWN_JACKET_001', '2024-01-01', 5, 35000, 7000),
    ('DOWN_JACKET_001', '2024-01-02', 3, 21000, 7000),
    ('DOWN_JACKET_001', '2024-01-03', 8, 56000, 7000),
    ('DOWN_JACKET_002', '2024-01-01', 2, 18000, 9000),
    ('DOWN_JACKET_002', '2024-01-02', 4, 36000, 9000),
    ('WINTER_COAT_001', '2024-01-01', 1, 12000, 12000),
    ('WINTER_COAT_001', '2024-01-02', 3, 36000, 12000)
ON CONFLICT DO NOTHING;

-- ==========================================
-- 8. VIEWS FOR ANALYTICS
-- ==========================================

-- View for sales analytics
CREATE OR REPLACE VIEW sales_analytics AS
SELECT
    sku_id,
    COUNT(*) as total_records,
    SUM(units_sold) as total_units,
    SUM(revenue) as total_revenue,
    AVG(price) as avg_price,
    MIN(date) as first_sale,
    MAX(date) as last_sale,
    AVG(units_sold) as avg_daily_units,
    AVG(revenue) as avg_daily_revenue
FROM sales_data
GROUP BY sku_id
ORDER BY total_revenue DESC;

-- View for recent forecasts
CREATE OR REPLACE VIEW recent_forecasts AS
SELECT
    f.*,
    s.avg_price,
    s.total_units as historical_units
FROM forecasts f
LEFT JOIN sales_analytics s ON f.sku_id = s.sku_id
ORDER BY f.created_at DESC
LIMIT 50;

-- Grant access to views
GRANT SELECT ON sales_analytics TO anon, authenticated, service_role;
GRANT SELECT ON recent_forecasts TO anon, authenticated, service_role;

-- ==========================================
-- SCHEMA SETUP COMPLETE!
-- ==========================================

-- Verify tables were created
SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('sales_data', 'forecasts', 'csv_upload_logs', 'api_usage_stats')
ORDER BY tablename;
