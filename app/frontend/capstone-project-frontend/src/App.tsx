import { useState } from 'react';
import Sidebar from './components/sidebar';
import Portfolio from './pages/portfolio';
import Onboarding from './pages/onboarding';
import ProjectInsights from "./pages/ProjectInsights";
import ProgressPage from './pages/progress';
import ResumeDisplay from './pages/resume_display';
import Dashboard from './pages/dashboard';

function App() {
  const [currentStep, setCurrentStep] = useState(1);
   const [showDashboard, setShowDashboard] = useState(false);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <Sidebar currentStep={currentStep} onStepChange={(step) => { setShowDashboard(false); setCurrentStep(step); }} onDashboard={() => setShowDashboard(true)} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {showDashboard ? (<Dashboard />) : (
        <>
          {currentStep === 1 && <Onboarding onComplete={() => setCurrentStep(2)} />}
          {currentStep === 3 && <ProgressPage onComplete={() => setCurrentStep(4)} />}
          {currentStep === 4 && <ProjectInsights onPrevious={() => setCurrentStep(3)} onComplete={() => setCurrentStep(5)} />}
          {currentStep === 5 && <ResumeDisplay />}
          {currentStep === 6 && <Portfolio />}
          {/* add other pages/components for other steps */}
        </>      
        )}
      </main>
    </div>
  );
}

export default App;