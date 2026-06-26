function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function FinancialImpactPanel({ financials }) {
  const items = [
    { label: 'Normal operational cost', value: formatCurrency(financials?.normal_operational_cost) },
    { label: 'Estimated weather cost', value: formatCurrency(financials?.estimated_operational_cost) },
    { label: 'Incremental weather cost', value: formatCurrency(financials?.incremental_weather_cost) },
    { label: 'Investment needed', value: formatCurrency(financials?.investment_needed) },
  ];

  return (
    <div className="card">
      <h3>Financial Impact</h3>
      <div className="financial-list">
        {items.map((item) => (
          <div key={item.label} className="financial-item">
            <span className="item-label">{item.label}</span>
            <span className="item-value">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default FinancialImpactPanel;
