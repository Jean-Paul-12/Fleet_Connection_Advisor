import SimulationNotice from './SimulationNotice';
import WeatherRiskBadge from './WeatherRiskBadge';

function RecommendationPanel({ riskLevel, recommendation, fleet, isMock, mockMessage }) {
  return (
    <div className="card">
      <h3>Executive Recommendation</h3>
      <WeatherRiskBadge riskLevel={riskLevel} />
      <p className="recommendation-text">{recommendation}</p>
      <SimulationNotice
        isSimulated={fleet?.is_simulated}
        simulationNotes={fleet?.simulation_notes}
        isMock={isMock}
        mockMessage={mockMessage}
      />
    </div>
  );
}

export default RecommendationPanel;
