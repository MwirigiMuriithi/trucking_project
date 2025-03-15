import React, { useState, FormEvent } from 'react';
import axios from 'axios';
import { TripData } from '../types';
import { API_ROOT } from '../config';

interface TripFormProps {
  setTripData: React.Dispatch<React.SetStateAction<TripData | null>>;
}

const TripForm: React.FC<TripFormProps> = ({ setTripData }) => {
  const [currentLocation, setCurrentLocation] = useState<string>('');
  const [pickupLocation, setPickupLocation] = useState<string>('');
  const [dropoffLocation, setDropoffLocation] = useState<string>('');
  const [currentCycleUsed, setCurrentCycleUsed] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const response = await axios.post<TripData>(`${API_ROOT}/api/calculate-trip/`, {
        currentLocation,
        pickupLocation,
        dropoffLocation,
        currentCycleUsed: parseFloat(currentCycleUsed)
      });
      setTripData(response.data);
    } catch (err: any) {
      console.error("Error calculating trip:", err.response?.data || err.message);
      setError("Failed to calculate trip. Please check your inputs.");
    }
    setLoading(false);
  };

  return (
    <div className="bg-white shadow rounded p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Enter Trip Details</h2>
      {error && <div className="text-red-500 mb-4">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-gray-700">Current Location</label>
          <input
            type="text"
            value={currentLocation}
            onChange={(e) => setCurrentLocation(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="e.g. San Francisco, CA"
            required
          />
        </div>
        <div>
          <label className="block text-gray-700">Pickup Location</label>
          <input
            type="text"
            value={pickupLocation}
            onChange={(e) => setPickupLocation(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="e.g. Sacramento, CA"
            required
          />
        </div>
        <div>
          <label className="block text-gray-700">Dropoff Location</label>
          <input
            type="text"
            value={dropoffLocation}
            onChange={(e) => setDropoffLocation(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="e.g. Los Angeles, CA"
            required
          />
        </div>
        <div>
          <label className="block text-gray-700">Current Cycle Hours Used</label>
          <input
            type="number"
            value={currentCycleUsed}
            onChange={(e) => setCurrentCycleUsed(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="e.g. 15"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition duration-200"
        >
          {loading ? "Calculating..." : "Calculate Trip"}
        </button>
      </form>
    </div>
  );
};

export default TripForm;
