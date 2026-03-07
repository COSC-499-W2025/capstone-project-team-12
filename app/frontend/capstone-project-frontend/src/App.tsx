import { useState } from 'react';
import ProgressPage from './pages/progress';
import DevPortfolio from './pages/portfolio'; 

function App() {
  //start the app on Step 1 (the progress page)
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#000000' }}>
      
      {/* The main container taking up the full screen */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        
        {/*step 1: show the loading progress */}
        {currentStep === 1 && (
          <ProgressPage onComplete={() => setCurrentStep(2)} />
        )}
        
        {/*step 2: show the results (portfolio) once loading finishes */}
        {currentStep === 2 && (
          <DevPortfolio />
        )}
        
      </main>
    </div>
  );
}

export default App;