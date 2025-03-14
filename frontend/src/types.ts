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
  
  export interface TripData {
    current_location: string;
    pickup_location: string;
    dropoff_location: string;
    current_cycle_hours_used: number;
    distance: number;
    route: [number, number][];
    logs: DayLog[];
    fuel_stops: FuelStop[];
  }
  