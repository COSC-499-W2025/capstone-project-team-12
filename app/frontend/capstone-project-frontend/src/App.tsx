import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Portfolio from './pages/portfolio';

function App() {
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <Sidebar currentStep={currentStep} onStepChange={setCurrentStep} />
      <main style={{ flex: 1 }}>
        {currentStep === 6 && <Portfolio />}
        {/* add other pages/components for other steps */}
      </main>
    </div>
  );
}

export default App;
