// src/components/DailyLog.tsx
import React from 'react';
import { DayLog } from '../types';

interface DailyLogProps {
  dayLog: DayLog;
}

const DailyLog: React.FC<DailyLogProps> = ({ dayLog }) => {
  return (
    <div className="mb-4 border p-4 rounded">
      <h4 className="font-bold mb-2">Day {dayLog.dayIndex}</h4>
      <table className="w-full text-left">
        <thead>
          <tr>
            <th className="border-b pb-1">Status</th>
            <th className="border-b pb-1">Start</th>
            <th className="border-b pb-1">End</th>
            <th className="border-b pb-1">Description</th>
          </tr>
        </thead>
        <tbody>
          {dayLog.events.map((event, idx) => (
            <tr key={idx}>
              <td className="py-1">{event.status}</td>
              <td className="py-1">{event.start}</td>
              <td className="py-1">{event.end}</td>
              <td className="py-1">{event.description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DailyLog;
