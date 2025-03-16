import React from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

interface MarkerData {
  coordinate: [number, number];
  description: string;
  status: string;
}

interface MapDisplayProps {
  route: [number, number][];
  markers?: MarkerData[];
}

const MapDisplay: React.FC<MapDisplayProps> = ({ route, markers = [] }) => {
  if (!route || route.length === 0) {
    return <p>No route data available.</p>;
  }

  // Convert route coordinates from [lng, lat] to [lat, lng]
  const latlngs = route.map(coord => [coord[1], coord[0]]);
  const center = latlngs[0];

  return (
    <MapContainer center={center} zoom={6} style={{ height: '400px', width: '100%' }}>
      <TileLayer
        attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Polyline positions={latlngs} pathOptions={{ color: "blue" }} />
      {markers.map((marker, idx) => {
        // Convert marker coordinate from [lng, lat] to [lat, lng]
        const position: [number, number] = [marker.coordinate[1], marker.coordinate[0]];
        return (
          <Marker key={idx} position={position}>
            <Popup>
              <strong>{marker.status}</strong>: {marker.description}
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
};

export default MapDisplay;
