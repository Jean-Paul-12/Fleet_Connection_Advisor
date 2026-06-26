function CitySearchInput({ value, onChange, onSubmit, disabled }) {
  return (
    <input
      type="text"
      placeholder="Enter city (e.g. Bogotá, Colombia)"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' && !disabled) {
          onSubmit();
        }
      }}
      disabled={disabled}
      aria-label="City search"
    />
  );
}

export default CitySearchInput;
