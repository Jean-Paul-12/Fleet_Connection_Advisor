import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function ForecastChart({ financials }) {
  const data = [
    {
      name: 'Impact',
      normal_operational_cost: financials?.normal_operational_cost || 0,
      estimated_operational_cost: financials?.estimated_operational_cost || 0,
      incremental_weather_cost: financials?.incremental_weather_cost || 0,
      investment_needed: financials?.investment_needed || 0,
    },
  ];

  return (
    <div className="card">
      <h3>Financial Impact Overview</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3E8DE" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(value) => `$${Math.round(value / 1000)}k`} />
            <Tooltip formatter={(value) => formatCurrency(value)} />
            <Legend />
            <Bar dataKey="normal_operational_cost" name="Normal Cost" fill="#FFD447" />
            <Bar dataKey="estimated_operational_cost" name="Weather Cost" fill="#FF441F" />
            <Bar dataKey="incremental_weather_cost" name="Incremental Cost" fill="#F59E0B" />
            <Bar dataKey="investment_needed" name="Investment Needed" fill="#991B1B" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default ForecastChart;
