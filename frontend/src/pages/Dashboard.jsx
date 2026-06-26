import { useEffect, useState } from 'react';
import {
  evaluateFleetImpact,
  fetchDashboardByCity,
  fetchRecentCities,
} from '../api/advisorApi';
import CityLocationMap from '../components/CityLocationMap';
import CitySearchInput from '../components/CitySearchInput';
import FinancialImpactPanel from '../components/FinancialImpactPanel';
import ForecastChart from '../components/ForecastChart';
import MetricCard from '../components/MetricCard';
import RecentCitiesDropdown from '../components/RecentCitiesDropdown';
import RecommendationPanel from '../components/RecommendationPanel';
import WeatherRiskBadge from '../components/WeatherRiskBadge';
import { riskColors } from '../styles/theme';

function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value || 0);
}

function formatPercent(value) {
  return `${((value || 0) * 100).toFixed(1)}%`;
}

function Dashboard() {
  const [cityInput, setCityInput] = useState('');
  const [recentCities, setRecentCities] = useState([]);
  const [selectedCityId, setSelectedCityId] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadRecentCities();
  }, []);

  async function loadRecentCities() {
    const cities = await fetchRecentCities();
    setRecentCities(cities);
  }

  async function handleEvaluate() {
    if (!cityInput.trim()) {
      setError('Please enter a city before evaluating.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await evaluateFleetImpact(cityInput.trim());
      setResult(data);
      await loadRecentCities();
    } catch (err) {
      setError(err.message || 'Unable to evaluate fleet impact.');
    } finally {
      setLoading(false);
    }
  }

  async function handleRecentCitySelect(cityId) {
    setSelectedCityId(cityId);
    if (!cityId) return;

    const selected = recentCities.find((city) => city.id === cityId);
    if (selected) {
      setCityInput(`${selected.name}, ${selected.country}`);
    }

    setLoading(true);
    setError('');

    try {
      const dashboard = await fetchDashboardByCity(cityId);
      if (dashboard) {
        setResult(dashboard);
      } else {
        setError('Unable to load dashboard for the selected city.');
      }
    } catch (err) {
      setError(err.message || 'Unable to load dashboard.');
    } finally {
      setLoading(false);
    }
  }

  const forecast = result?.forecast;
  const financials = result?.financials;
  const fleet = result?.fleet;
  const location = result?.location;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Fleet Connection Advisor</h1>
        <p>Weather-driven fleet investment intelligence</p>

        <div className="header-controls">
          <CitySearchInput
            value={cityInput}
            onChange={setCityInput}
            onSubmit={handleEvaluate}
            disabled={loading}
          />
          <RecentCitiesDropdown
            cities={recentCities}
            value={selectedCityId}
            onChange={handleRecentCitySelect}
            disabled={loading}
          />
          <button
            type="button"
            className="primary-button"
            onClick={handleEvaluate}
            disabled={loading}
          >
            {loading ? 'Evaluating...' : 'Evaluate Fleet Impact'}
          </button>
        </div>
      </header>

      {error && (
        <div className="card state-box error">
          <p>{error}</p>
        </div>
      )}

      {!result && !loading && !error && (
        <div className="card state-box">
          <p>Enter a city and evaluate fleet impact to see executive insights.</p>
        </div>
      )}

      {loading && (
        <div className="card state-box">
          <p>Evaluating weather impact and fleet connection metrics...</p>
        </div>
      )}

      {result && !loading && (
        <>
          {location?.latitude != null && location?.longitude != null && (
            <section className="city-map-section">
              <CityLocationMap location={location} riskLevel={result.risk_level} />
            </section>
          )}

          <section className="kpi-grid">
            <MetricCard
              label="Connection Rate"
              value={formatPercent(financials?.connection_rate)}
              subtext={`Target ${formatPercent(financials?.target_connection_rate)}`}
            />
            <MetricCard
              label="Weather Risk"
              value={result.risk_level}
              accent={riskColors[result.risk_level]}
            />
            <MetricCard
              label="Incremental Weather Cost"
              value={formatCurrency(financials?.incremental_weather_cost)}
            />
            <MetricCard
              label="Investment Needed"
              value={formatCurrency(financials?.investment_needed)}
            />
            <MetricCard
              label="Adjusted Cost per Trip"
              value={formatCurrency(financials?.adjusted_cost_per_trip)}
              subtext={`Multiplier x${financials?.weather_cost_multiplier}`}
            />
          </section>

          <section className="panel-grid">
            <div className="card">
              <h3>Forecast Panel</h3>
              <div className="forecast-list">
                <div className="forecast-item">
                  <span className="item-label">Weather condition</span>
                  <span className="item-value">{forecast?.weather_condition}</span>
                </div>
                <div className="forecast-item">
                  <span className="item-label">Rain probability</span>
                  <span className="item-value">{formatPercent(forecast?.rain_probability)}</span>
                </div>
                <div className="forecast-item">
                  <span className="item-label">Temperature</span>
                  <span className="item-value">{forecast?.temperature} °C</span>
                </div>
                <div className="forecast-item">
                  <span className="item-label">Humidity</span>
                  <span className="item-value">{forecast?.humidity}%</span>
                </div>
                <div className="forecast-item">
                  <span className="item-label">Wind speed</span>
                  <span className="item-value">{forecast?.wind_speed} kph</span>
                </div>
              </div>
            </div>

            <FinancialImpactPanel financials={financials} />

            <RecommendationPanel
              riskLevel={result.risk_level}
              recommendation={result.recommendation}
              fleet={fleet}
              isMock={result.isMock}
              mockMessage={result.mockMessage}
            />
          </section>

          <section style={{ marginBottom: '24px' }}>
            <ForecastChart financials={financials} />
          </section>

          <section className="card">
            <h3>Executive Summary</h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="summary-table">
                <thead>
                  <tr>
                    <th>City</th>
                    <th>Country</th>
                    <th>Forecast date</th>
                    <th>Risk level</th>
                    <th>Expected orders</th>
                    <th>Required couriers</th>
                    <th>Available couriers</th>
                    <th>Connection rate</th>
                    <th>Investment needed</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{location?.name}</td>
                    <td>{location?.country}</td>
                    <td>{forecast?.forecast_date}</td>
                    <td>
                      <WeatherRiskBadge riskLevel={result.risk_level} />
                    </td>
                    <td>{fleet?.expected_orders?.toLocaleString()}</td>
                    <td>{fleet?.required_couriers?.toLocaleString()}</td>
                    <td>{fleet?.available_couriers?.toLocaleString()}</td>
                    <td>{formatPercent(financials?.connection_rate)}</td>
                    <td>{formatCurrency(financials?.investment_needed)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}

      <footer className="app-watermark">
        Desarrollado por <strong>Jean Paul Quitian</strong>
      </footer>
    </div>
  );
}

export default Dashboard;
