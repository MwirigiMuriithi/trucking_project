// // src/components/MapDisplay.tsx
// import React from 'react';

// interface MapDisplayProps {
//   route: [number, number][];
// }

// const MapDisplay: React.FC<MapDisplayProps> = ({ route }) => {
//   return (
//     <div className="border p-4 rounded">
//       <h4 className="font-bold mb-2">Route Coordinates</h4>
//       {route && route.length > 0 ? (
//         <ul className="list-disc list-inside">
//           {route.map((coord, idx) => (
//             <li key={idx}>
//               Latitude: {coord[1].toFixed(4)}, Longitude: {coord[0].toFixed(4)}
//             </li>
//           ))}
//         </ul>
//       ) : (
//         <p>No route data available.</p>
//       )}
//     </div>
//   );
// };

// export default MapDisplay;


import React from 'react';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

interface MapDisplayProps {
  route: [number, number][];
}

const MapDisplay: React.FC<MapDisplayProps> = ({ route }) => {
  if (!route || route.length === 0) {
    return <p>No route data available.</p>;
  }

  // Convert route coordinates from [lng, lat] to [lat, lng]
  const latlngs = route.map(coord => [coord[1], coord[0]]);
  // Use the first coordinate as the center
  const center = latlngs[0];

  return (
    <MapContainer center={center} zoom={6} style={{ height: '400px', width: '100%' }}>
      <TileLayer
        attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Polyline positions={latlngs} pathOptions={{ color: "blue" }} />
    </MapContainer>
  );
};

export default MapDisplay;
