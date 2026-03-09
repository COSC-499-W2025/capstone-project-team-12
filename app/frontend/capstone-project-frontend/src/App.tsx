import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Portfolio from './pages/portfolio';
import Onboarding from './pages/onboarding';

function App() {
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <Sidebar currentStep={currentStep} onStepChange={setCurrentStep} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {currentStep === 1 && <Onboarding onComplete={() => setCurrentStep(2)} />}
        {currentStep === 6 && <Portfolio />}
        {/* add other pages/components for other steps */}
      </main>
    </div>
  );
}

export default App;
