// src/App.tsx
import { useState } from 'react';
import Sidebar from './components/sidebar';
import Portfolio from './pages/portfolio';
import Onboarding from './pages/onboarding';
import ProgressPage from './pages/progress';
import ResumeDisplay from './pages/resume_display';

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedData, setExtractedData] = useState<any>(null); // Holds the API results

  // This is the function your File Upload step will call when the user clicks "Submit"
  const handleUploadSubmit = async (formData: FormData) => {
    setCurrentStep(2.5); // 1. Immediately show the Progress Placeholder
    setIsExtracting(true); // 2. Tell the placeholder to start counting and cap at 95%

    try {
      // 3. Do it asynchronously (Your teammate's rule #1)
      const response = await fetch('http://localhost:8000/projects/upload/extract', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      // 4. Wait until we have ALL the fields (Your teammate's rule #2)
      setExtractedData(data); 
    } catch (error) {
      console.error("Upload failed", error);
    } finally {
      // 5. Release the UI to go to 100%
      setIsExtracting(false); 
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <Sidebar currentStep={currentStep} onStepChange={setCurrentStep} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        
        {currentStep === 1 && <Onboarding onComplete={() => setCurrentStep(2)} />}
        
        {/* Step 2 (File Upload) needs to call handleUploadSubmit when ready */}
        {currentStep === 2 && (
           <div style={{padding: 50}}>
             {/* Temporary test button so you can see it work! */}
             <button onClick={() => handleUploadSubmit(new FormData())}>Test Fake Upload</button>
           </div>
        )}
        
        {/* The Placeholder */}
        {currentStep === 3 && (
          <ProgressPage 
            isProcessing={isExtracting} 
            onComplete={() => setCurrentStep(3)} 
          />
        )}
        
        {/* Step 3 (Finetuning) - Note how we pass the extractedData here so it renders flawlessly */}
        {/* {currentStep === 3 && (
           <div style={{padding: 50}}>
             <h2>Finetuning Page</h2>
             <pre>{JSON.stringify(extractedData, null, 2)}</pre>
           </div>
        )} */}
        
        {currentStep === 5 && <ResumeDisplay />}
        {currentStep === 6 && <Portfolio />}
      </main>
    </div>
  );
}

export default App;