import { useState } from 'react';
import Sidebar from './components/sidebar';
import Portfolio from './pages/portfolio';
import Onboarding from './pages/onboarding';
import ProjectInsights from "./pages/ProjectInsights";
import ProgressPage from './pages/progress';
import ResumeDisplay from './pages/resume_display';
// Import your Step 2 component here, e.g.:
// import FileSelection from './pages/FileSelection';

function App() {
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <Sidebar currentStep={currentStep} onStepChange={setCurrentStep} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {currentStep === 1 && <Onboarding onComplete={() => setCurrentStep(2)} />}
        {/* {currentStep === 2 && <FileImport onComplete={() => setCurrentStep(2.5)} />} */}
        {/*step 2.5: intermediate progress page (not in sidebar) */}
        {/* {currentStep === 2.5 && <ProgressPage onComplete={() => setCurrentStep(3)} />} */}
        {/*currently set progress page to step 3 just so I can see it while working on it*/}
        {currentStep === 3 && <ProgressPage onComplete={() => setCurrentStep(4)}/>}
        {/* Step 3*/}
        {currentStep === 5 && <ResumeDisplay />}
        {currentStep === 6 && <Portfolio />}
        {/* add other pages/components for other steps */}
      </main>
    </div>
  );
}

export default App;