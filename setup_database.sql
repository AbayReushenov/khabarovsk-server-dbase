-- Setup script for Habarovsk Forecast Buddy database
-- Run this in your Supabase SQL editor

-- Create sales_data table
CREATE TABLE IF NOT EXISTS sales_data (
    id SERIAL PRIMARY KEY,
    sku_id VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    units_sold INTEGER NOT NULL DEFAULT 0,
    revenue DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    weather_temp DECIMAL(5,2),
    season VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(sku_id, date)
);

-- Create forecasts table
CREATE TABLE IF NOT EXISTS forecasts (
    id SERIAL PRIMARY KEY,
    sku_id VARCHAR(100) NOT NULL,
    forecast_period INTEGER NOT NULL,
    predictions JSONB NOT NULL,
    total_predicted_units INTEGER NOT NULL DEFAULT 0,
    total_predicted_revenue DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    average_confidence DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    model_explanation TEXT,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_inputs table (optional, for future use)
CREATE TABLE IF NOT EXISTS user_inputs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    input_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sales_data_sku_date ON sales_data(sku_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_forecasts_sku_generated ON forecasts(sku_id, generated_at DESC);

-- Insert some sample data for testing
INSERT INTO sales_data (sku_id, date, units_sold, revenue, weather_temp, season) VALUES
('DOWN_JACKET_001', '2024-01-15', 5, 15000.00, -15.5, 'winter'),
('DOWN_JACKET_002', '2024-01-16', 3, 9500.00, -12.0, 'winter'),
('DOWN_JACKET_001', '2024-01-17', 7, 21000.00, -18.2, 'winter'),
('DOWN_JACKET_003', '2024-01-18', 2, 8000.00, -10.5, 'winter'),
('DOWN_JACKET_001', '2024-01-19', 4, 12000.00, -8.0, 'winter')
ON CONFLICT (sku_id, date) DO NOTHING;

-- Grant necessary permissions (if using RLS)
-- ALTER TABLE sales_data ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE forecasts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_inputs ENABLE ROW LEVEL SECURITY;

-- Create policies (uncomment if you want to enable RLS)
-- CREATE POLICY "Allow all operations for service role" ON sales_data FOR ALL USING (true);
-- CREATE POLICY "Allow all operations for service role" ON forecasts FOR ALL USING (true);
-- CREATE POLICY "Allow all operations for service role" ON user_inputs FOR ALL USING (true);
