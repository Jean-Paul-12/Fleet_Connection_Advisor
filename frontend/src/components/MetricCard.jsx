function MetricCard({ label, value, subtext, accent }) {
  return (
    <div className="card metric-card">
      <span className="metric-label">{label}</span>
      <span className="metric-value" style={accent ? { color: accent } : undefined}>
        {value}
      </span>
      {subtext && <span className="metric-subtext">{subtext}</span>}
    </div>
  );
}

export default MetricCard;
