import { useEffect } from 'react';
import L from 'leaflet';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';
import 'leaflet/dist/leaflet.css';

const defaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

function MapViewUpdater({ center, zoom }) {
  const map = useMap();

  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1.2 });
  }, [map, center, zoom]);

  return null;
}

function formatLocationLabel(location) {
  const parts = [location.name];

  if (location.region) {
    parts.push(location.region);
  }

  parts.push(location.country);
  return parts.join(', ');
}

function CityLocationMap({ location, riskLevel }) {
  const center = [location.latitude, location.longitude];
  const label = formatLocationLabel(location);

  return (
    <div className="card city-map-card">
      <h3>City Location</h3>
      <p className="city-map-subtitle">{label}</p>
      <div className="city-map-container">
        <MapContainer
          center={center}
          zoom={11}
          scrollWheelZoom={false}
          aria-label={`Map showing ${label}`}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapViewUpdater center={center} zoom={11} />
          <Marker position={center} icon={defaultIcon}>
            <Popup>
              <strong>{location.name}</strong>
              <br />
              {location.country}
              {riskLevel ? (
                <>
                  <br />
                  Risk: {riskLevel}
                </>
              ) : null}
            </Popup>
          </Marker>
        </MapContainer>
      </div>
    </div>
  );
}

export default CityLocationMap;
