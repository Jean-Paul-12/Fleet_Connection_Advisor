import { riskColors } from '../styles/theme';

function WeatherRiskBadge({ riskLevel }) {
  const color = riskColors[riskLevel] || riskColors.MEDIUM;

  return (
    <span className="risk-badge" style={{ backgroundColor: color }}>
      {riskLevel} RISK
    </span>
  );
}

export default WeatherRiskBadge;
