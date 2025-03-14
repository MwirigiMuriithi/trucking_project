// src/components/MapDisplay.tsx
import React from 'react';

interface MapDisplayProps {
  route: [number, number][];
}

const MapDisplay: React.FC<MapDisplayProps> = ({ route }) => {
  return (
    <div className="border p-4 rounded">
      <h4 className="font-bold mb-2">Route Coordinates</h4>
      {route && route.length > 0 ? (
        <ul className="list-disc list-inside">
          {route.map((coord, idx) => (
            <li key={idx}>
              Latitude: {coord[1].toFixed(4)}, Longitude: {coord[0].toFixed(4)}
            </li>
          ))}
        </ul>
      ) : (
        <p>No route data available.</p>
      )}
    </div>
  );
};

export default MapDisplay;
