// // src/App.tsx
// import React, { useState } from 'react';
// import TripForm from './components/TripForm';
// import TripDetails from './components/TripDetails';
// import { TripData } from './types';

// const App: React.FC = () => {
//   const [tripData, setTripData] = useState<TripData | null>(null);

//   return (
//     <div className="min-h-screen bg-gray-100 p-4">
//       <header className="max-w-4xl mx-auto mb-8">
//         <h1 className="text-3xl font-bold text-center text-blue-600">
//           Trucking Trip Calculator
//         </h1>
//       </header>
//       <main className="max-w-4xl mx-auto">
//         <TripForm setTripData={setTripData} />
//         {tripData && <TripDetails tripData={tripData} />}
//       </main>
//     </div>
//   );
// };

// export default App;


// src/App.tsx
import React, { useState } from 'react';
import TripForm from './components/TripForm';
import TripDetails from './components/TripDetails';
import { TripData } from './types';

const App: React.FC = () => {
  const [tripData, setTripData] = useState<TripData | null>(null);

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <header className="max-w-4xl mx-auto mb-8">
        <h1 className="text-3xl font-bold text-center text-blue-600">
          Trucking Trip Calculator
        </h1>
      </header>
      <main className="max-w-4xl mx-auto">
        <TripForm setTripData={setTripData} />
        {tripData && <TripDetails tripData={tripData} />}
      </main>
    </div>
  );
};

export default App;
