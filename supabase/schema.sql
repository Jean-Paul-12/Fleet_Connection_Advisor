-- Fleet Connection Advisor - Supabase schema
-- Run this script in the Supabase SQL Editor for project Rappi_Prueba

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS cities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    region TEXT,
    country TEXT NOT NULL,
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    timezone TEXT,
    external_provider TEXT DEFAULT 'openweathermap',
    external_location_id TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS weather_forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city_id UUID NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    weather_condition TEXT NOT NULL,
    rain_probability NUMERIC NOT NULL,
    temperature NUMERIC,
    humidity NUMERIC,
    wind_speed NUMERIC,
    raw_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fleet_advisor_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city_id UUID NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    expected_orders INTEGER NOT NULL,
    required_couriers INTEGER NOT NULL,
    available_couriers INTEGER NOT NULL,
    base_cost_per_trip NUMERIC NOT NULL,
    weather_cost_multiplier NUMERIC NOT NULL,
    adjusted_cost_per_trip NUMERIC NOT NULL,
    normal_operational_cost NUMERIC NOT NULL,
    estimated_operational_cost NUMERIC NOT NULL,
    incremental_weather_cost NUMERIC NOT NULL,
    connection_rate NUMERIC NOT NULL,
    target_connection_rate NUMERIC NOT NULL,
    connection_gap NUMERIC NOT NULL,
    investment_needed NUMERIC NOT NULL,
    risk_level TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    is_simulated BOOLEAN DEFAULT TRUE,
    simulation_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cities_created_at ON cities(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cities_name_country ON cities(name, country);

CREATE INDEX IF NOT EXISTS idx_weather_forecasts_city_id ON weather_forecasts(city_id);
CREATE INDEX IF NOT EXISTS idx_weather_forecasts_forecast_date ON weather_forecasts(forecast_date);
CREATE INDEX IF NOT EXISTS idx_weather_forecasts_created_at ON weather_forecasts(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_fleet_advisor_results_city_id ON fleet_advisor_results(city_id);
CREATE INDEX IF NOT EXISTS idx_fleet_advisor_results_forecast_date ON fleet_advisor_results(forecast_date);
CREATE INDEX IF NOT EXISTS idx_fleet_advisor_results_created_at ON fleet_advisor_results(created_at DESC);

-- Row Level Security: blocks direct access via anon/authenticated keys.
-- The Flask backend uses service_role, which bypasses RLS.
ALTER TABLE public.cities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weather_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fleet_advisor_results ENABLE ROW LEVEL SECURITY;
