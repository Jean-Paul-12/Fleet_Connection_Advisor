function RecentCitiesDropdown({ cities, value, onChange, disabled }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      aria-label="Recent cities"
    >
      <option value="">Recent cities</option>
      {cities.map((city) => (
        <option key={city.id} value={city.id}>
          {city.name}, {city.country}
        </option>
      ))}
    </select>
  );
}

export default RecentCitiesDropdown;
