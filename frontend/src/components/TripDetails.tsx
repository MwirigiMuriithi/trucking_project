import React from 'react';
import DailyLog from './DailyLog';
import MapDisplay from './MapDisplay';
import { TripData } from '../types';

interface TripDetailsProps {
  tripData: TripData;
}

const TripDetails: React.FC<TripDetailsProps> = ({ tripData }) => {
  return (
    <div className="bg-white shadow rounded p-6">
      <h2 className="text-2xl font-semibold mb-4">Trip Details</h2>
      <div className="mb-6">
        <p>
          <span className="font-bold">Current Location:</span> {tripData.current_location}
        </p>
        <p>
          <span className="font-bold">Pickup Location:</span> {tripData.pickup_location}
        </p>
        <p>
          <span className="font-bold">Dropoff Location:</span> {tripData.dropoff_location}
        </p>
        <p>
          <span className="font-bold">Cycle Hours Used:</span> {tripData.current_cycle_hours_used}
        </p>
        <p>
          <span className="font-bold">Total Distance:</span> {tripData.distance} miles
        </p>
      </div>
      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-2">Route Map</h3>
        <MapDisplay route={tripData.route} />
      </div>
      <div>
        <h3 className="text-xl font-semibold mb-2">Daily Logs</h3>
        {tripData.logs.map((dayLog, idx) => (
          <DailyLog key={idx} dayLog={dayLog} />
        ))}
      </div>
    </div>
  );
};

export default TripDetails;
