// src/App.tsx
import { useState } from 'react';
import Sidebar from './components/sidebar';
import Portfolio from './pages/portfolio';
import Onboarding from './pages/onboarding';
import ProgressPage from './pages/progress';
import ResumeDisplay from './pages/resume_display';
import Dashboard from './pages/dashboard';
import FileImport, { type UploadEntry } from './pages/fileImport';
import FinetunePage from './pages/FinetunePage';


interface OnboardingData {
  llmMode: 'online' | 'local';
  githubUsername: string;
  email: string;
}

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [showDashboard, setShowDashboard] = useState(false);
  const [onboardingData, setOnboardingData] = useState<OnboardingData | null>(null);
  const [uploads, setUploads] = useState<UploadEntry[]>([]);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <Sidebar currentStep={currentStep} onStepChange={(step) => { setShowDashboard(false); setCurrentStep(step); }} onDashboard={() => setShowDashboard(true)} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {showDashboard ? (<Dashboard />) : (
        <>
          {currentStep === 1 && (
          <Onboarding
            initialData={onboardingData}
            onComplete={(data) => { setOnboardingData(data); setCurrentStep(2); }}
          />
        )}
          {currentStep === 2 && (
            <FileImport
              onComplete={() => setCurrentStep(2.5)}
              githubUsername={onboardingData?.githubUsername || ''}
              githubEmail={onboardingData?.email || ''}
              model={onboardingData?.llmMode || 'online'}
              uploads={uploads}
              onUploadsChange={setUploads}
            />
          )}

          {currentStep === 2.5 && <ProgressPage onComplete={() => setCurrentStep(3)} />}
          {currentStep === 3 && <FinetunePage onComplete ={() => setCurrentStep(4)} />}
          {currentStep === 4 && <ProjectInsights onPrevious={() => setCurrentStep(2)} onComplete={() => setCurrentStep(5)} />}
          {currentStep === 5 && <ResumeDisplay onPrevious={() => setCurrentStep(4)} onComplete={() => setCurrentStep(6)} />}
          {currentStep === 6 && <Portfolio onPrevious={() => setCurrentStep(5)} onComplete={() => setShowDashboard(true)} />}
          {/* add other pages/components for other steps */}
        </>      
        )}
      </main>
    </div>
  );
}

export default App;