import { useState } from 'react';
import Sidebar from './components/sidebar';
import Portfolio from './pages/portfolio';
import Onboarding from './pages/onboarding';
import ProjectInsights from "./pages/ProjectInsights";
import ProgressPage from './pages/progress';
import ResumeDisplay from './pages/resume_display';
import FileImport from './pages/fileImport';
import FinetunePage from './pages/FinetunePage';

function App() {
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <Sidebar currentStep={currentStep} onStepChange={setCurrentStep} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {currentStep === 1 && <Onboarding onComplete={() => setCurrentStep(2)} />}
        {currentStep === 2 && <FileImport onComplete={() => setCurrentStep(2.5)} />}
        {currentStep === 2.5 && <ProgressPage onComplete={() => setCurrentStep(3)} />}
        {currentStep === 3 && <FinetunePage onComplete ={() => setCurrentStep(4)} />}
          {currentStep === 4 && <ProjectInsights onPrevious={() => setCurrentStep(3)} onComplete={() => setCurrentStep(5)} />}
        {currentStep === 5 && <ResumeDisplay />}
        {currentStep === 6 && <Portfolio />}
        {/* add other pages/components for other steps */}
      </main>
    </div>
  );
}

export default App;