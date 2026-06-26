function SimulationNotice({ isSimulated, simulationNotes, isMock, mockMessage }) {
  if (isMock) {
    return (
      <div className="simulation-notice mock">
        {mockMessage || 'Showing mock data because the backend API is unavailable.'}
      </div>
    );
  }

  if (!isSimulated) {
    return (
      <div className="simulation-notice">
        {simulationNotes ||
          'Operational demand and courier availability were provided manually in the request.'}
      </div>
    );
  }

  return (
    <div className="simulation-notice">
      {simulationNotes ||
        'Operational demand and courier availability were simulated because no real internal demand or fleet source was provided.'}
    </div>
  );
}

export default SimulationNotice;
