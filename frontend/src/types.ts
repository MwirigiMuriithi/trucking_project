// src/types.ts
export interface Event {
  status: string;
  start: string;
  end: string;
  description: string;
}

export interface DayLog {
  dayIndex: number;
  events: Event[];
}

export interface FuelStop {
  mile: number;
  location: string;
}

export interface EldFormData {
  dayIndex: number;
  timeline: string[];
}

export interface TripData {
  driver: number;
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  cycle_hours_used: number;
  distance: number;
  route: [number, number][];
  logs: DayLog[];
  fuel_stops: FuelStop[];
  eldFormData: EldFormData[];
}
