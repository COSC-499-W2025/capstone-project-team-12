import { useState } from 'react';
import Sidebar from './components/sidebar';
import Portfolio from './pages/portfolio';
import Onboarding from './pages/onboarding';
import ProjectInsights from "./pages/ProjectInsights";
import ProgressPage from './pages/progress';

function App() {
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <Sidebar currentStep={currentStep} onStepChange={setCurrentStep} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {currentStep === 1 && <Onboarding onComplete={() => setCurrentStep(2)} />}
        {/* added progress page as step 3 for now, will set to step 2.5 next week */ }
        {currentStep === 3 && <ProgressPage />}
        {currentStep === 6 && <Portfolio />}
        {/* add other pages/components for other steps */}
      </main>
    </div>
  );
}

export default App;