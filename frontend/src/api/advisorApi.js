import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const MOCK_RESULT = {
  isMock: true,
  mockMessage: 'Showing mock data because the backend API is unavailable.',
  id: 'mock-id',
  city_id: 'mock-city-id',
  created_at: new Date().toISOString(),
  city: {
    id: 'mock-city-id',
    name: 'Bogotá',
    region: 'Cundinamarca',
    country: 'Colombia',
  },
  location: {
    name: 'Bogotá',
    region: 'Cundinamarca',
    country: 'Colombia',
    latitude: 4.711,
    longitude: -74.0721,
    timezone: 'America/Bogota',
  },
  forecast: {
    forecast_date: new Date().toISOString().slice(0, 10),
    weather_condition: 'Moderate rain',
    rain_probability: 0.72,
    temperature: 16,
    humidity: 82,
    wind_speed: 18,
  },
  fleet: {
    expected_orders: 11200,
    required_couriers: 2800,
    available_couriers: 2240,
    is_simulated: true,
    simulation_notes:
      'Operational demand and courier availability were simulated because no real internal demand or fleet source was provided.',
  },
  financials: {
    base_cost_per_trip: 1.0,
    weather_cost_multiplier: 1.5,
    adjusted_cost_per_trip: 1.5,
    normal_operational_cost: 11200,
    estimated_operational_cost: 16800,
    incremental_weather_cost: 5600,
    connection_rate: 0.8,
    target_connection_rate: 0.95,
    connection_gap: 0.15,
    missing_couriers: 560,
    investment_needed: 8400,
  },
  risk_level: 'CRITICAL',
  recommendation:
    'Immediate action required: deploy emergency incentives, prioritize high-demand zones and monitor courier availability in real time.',
};

function unwrapResponse(response) {
  return response.data?.data ?? response.data;
}

export async function fetchRecentCities() {
  try {
    const response = await api.get('/cities');
    return unwrapResponse(response);
  } catch {
    return [];
  }
}

function getApiErrorMessage(error, fallback) {
  if (error.response?.data?.error?.message) {
    return error.response.data.error.message;
  }
  if (!error.response) {
    return 'Unable to reach the backend API. Make sure it is running on port 5000.';
  }
  return fallback;
}

export async function evaluateFleetImpact(location) {
  try {
    const response = await api.post('/advisor/evaluate', { location });
    return { ...unwrapResponse(response), isMock: false };
  } catch (error) {
    throw new Error(getApiErrorMessage(error, 'Unable to evaluate fleet impact.'));
  }
}

export async function fetchDashboardByCity(cityId) {
  try {
    const response = await api.get('/advisor/dashboard', {
      params: { city_id: cityId },
    });
    return { ...unwrapResponse(response), isMock: false };
  } catch {
    return null;
  }
}

export function getMockResult() {
  return { ...MOCK_RESULT, isMock: true };
}

export { MOCK_RESULT };
