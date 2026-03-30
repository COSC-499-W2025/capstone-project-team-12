import { useEffect } from 'react';
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import Portfolio from './pages/portfolio';
import Onboarding from './pages/onboarding';
import ProjectInsights from './pages/ProjectInsights';
import ProgressPage from './pages/progress';
import ResumeDisplay from './pages/resume_display';
import Dashboard from './pages/dashboard';
import FileImport from './pages/fileImport';
import FinetunePage from './pages/finetunePage';
import PipelineLayout from './layouts/PipelineLayout';
import StandardLayout from './layouts/StandardLayout';
import { useAnalysisPipeline } from './context/AnalysisPipelineContext';

function PipelineOnboardingPage() {
  const navigate = useNavigate();
  const {
    onboardingData, setOnboardingData, setActiveAnalysisId, setUploads, setExtractedData, setFinetuneState, setResumeLocation, setPortfolioLocation, setViewResumeId, setViewPortfolioId, setViewInsightsAnalysisId,
  } = useAnalysisPipeline();

  useEffect(() => {
    setActiveAnalysisId(null);
    setUploads([]);
    setExtractedData(null);
    setFinetuneState(null);
    setResumeLocation(null);
    setPortfolioLocation(null);
    setViewResumeId(null);
    setViewPortfolioId(null);
    setViewInsightsAnalysisId(null);
  }, [
    setActiveAnalysisId, setUploads, setExtractedData, setFinetuneState,setResumeLocation,setPortfolioLocation,setViewResumeId, setViewPortfolioId, setViewInsightsAnalysisId,
  ]);

  return (
    <Onboarding
      initialData={onboardingData}
      mode="new-analysis"
      onComplete={(data) => {
        setOnboardingData(data);
        navigate('/analysis/new/import');
      }}
    />
  );
}

function PipelineImportPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const {
    activeAnalysisId,
    setActiveAnalysisId,
    onboardingData,
    uploads,
    setUploads,
    setExtractedData,
    setViewInsightsAnalysisId,
  } = useAnalysisPipeline();

  const queryId = new URLSearchParams(location.search).get('analysisId');
  const resolvedAnalysisId = activeAnalysisId ?? queryId;

  useEffect(() => {
    if (queryId && queryId !== activeAnalysisId) {
      setActiveAnalysisId(queryId);
    }
  }, [queryId, activeAnalysisId, setActiveAnalysisId]);

  return (
    <FileImport
      activeAnalysisId={resolvedAnalysisId}
      onComplete={(data?: any) => {
        if (data) {
          setExtractedData(data);
          if (data.analysis_id) {
            setViewInsightsAnalysisId(data.analysis_id);
          }
        }
        navigate('/analysis/new/progress');
      }}
      model={onboardingData?.llmMode || 'online'}
      uploads={uploads}
      onUploadsChange={setUploads}
    />
  );
}

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [showDashboard, setShowDashboard] = useState(false);
  const [onboardingData, setOnboardingData] = useState<OnboardingData | null>(null);
  const [uploads, setUploads] = useState<UploadEntry[]>([]);
  const [analysisMode, setAnalysisMode] = useState<'setup' | 'new-analysis'>('setup');
  const [activeAnalysisId, setActiveAnalysisId] = useState<string | null>(null);
  const [viewResumeId, setViewResumeId] = useState<number | null>(null);
  const [viewPortfolioId, setViewPortfolioId] = useState<number | null>(null);
  const [viewInsightsAnalysisId, setViewInsightsAnalysisId] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // --- Global States for Persistence & API ---
  const [extractedData, setExtractedData] = useState<any>(null);
  const [finetuneState, setFinetuneState] = useState<any>(null);
  const [resumeLocation, setResumeLocation] = useState<string | null>(null);
  const [portfolioLocation, setPortfolioLocation] = useState<string | null>(null);

  const handleViewInsights = (analysisId: string) => {
    setViewInsightsAnalysisId(analysisId);
    setShowDashboard(false);
    setCurrentStep(4);
  };

  const handleViewPortfolio = (portfolioId: number) => {
    setViewPortfolioId(portfolioId);
    setShowDashboard(false);
    setCurrentStep(6); 
  };
  
  const handleViewResume = (resumeId: number) => {
    setViewResumeId(resumeId);
    setShowDashboard(false);
    setCurrentStep(5); 
  };


  const handleNewAnalysis = () => {
    setShowDashboard(false);
    setAnalysisMode('new-analysis');
    setCurrentStep(1);
  };


  const handleIncremental = (analysisId: string) => {
    setActiveAnalysisId(analysisId);
    setShowDashboard(false);
    setCurrentStep(2); // skip onboarding and go straight to FileImport
  };
  
  
  function PipelineProgressPage() {
    const navigate = useNavigate();
    return <ProgressPage onComplete={() => navigate('/analysis/new/finetune')} />;
  }

  function PipelineFinetunePage() {
    const navigate = useNavigate();
    const {
      extractedData, finetuneState,setFinetuneState, activeAnalysisId, onboardingData, setResumeLocation, setPortfolioLocation, setViewResumeId, setViewPortfolioId, setViewInsightsAnalysisId,
    } = useAnalysisPipeline();

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <Sidebar currentStep={currentStep} onStepChange={(step) => { setShowDashboard(false); setCurrentStep(step); }} onDashboard={() => setShowDashboard(true)}   isCollapsed={sidebarCollapsed} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {showDashboard ? (
          <Dashboard 
            onNewAnalysis={handleNewAnalysis} 
            onIncremental={handleIncremental} 
            onViewResume={handleViewResume} 
            onViewPortfolio={handleViewPortfolio}
            onViewInsights={handleViewInsights}
          />) : (
        <>
          {currentStep === 1 && (
          <Onboarding
            initialData={onboardingData}
            mode={analysisMode}
            onComplete={(data) => { setOnboardingData(data); setCurrentStep(2); }}
          />
          )}
            {currentStep === 2 && (
              <FileImport
                activeAnalysisId={activeAnalysisId}
                onComplete={(data?: any) => { 
                  if (data) setExtractedData(data);
                  setCurrentStep(2.5); 
                }}
                model={onboardingData?.llmMode || 'online'}
                uploads={uploads}
                onUploadsChange={setUploads}
              />
            )}

          {currentStep === 2.5 && <ProgressPage onComplete={() => setCurrentStep(3)} />}
          
          {currentStep === 3 && (
            <FinetunePage 
              extractedData={extractedData}
              initialState={finetuneState}
              activeAnalysisId={activeAnalysisId}
              llmMode={onboardingData?.llmMode}
              onBack={() => setCurrentStep(2.5)}
              // Continuously sync state upwards so nothing is lost if user navigates away via sidebar
              onStateChange={(state) => setFinetuneState(state)}
              onComplete={(state, resLoc, portLoc, rId, pId) => {
                setFinetuneState(state);
                if (resLoc) setResumeLocation(resLoc);
                if (portLoc) setPortfolioLocation(portLoc);
                if (rId) setViewResumeId(rId);
                if (pId) setViewPortfolioId(pId);
                if (extractedData?.analysis_id) setViewInsightsAnalysisId(extractedData.analysis_id);
                setCurrentStep(4);
              }} 
            />
          )}

          {currentStep === 4 && 
            (<ProjectInsights 
              onPrevious={() => setCurrentStep(3)} 
              onComplete={() => setCurrentStep(5)} 
              analysisId={viewInsightsAnalysisId}
              /> 
            )}
          
          {currentStep === 5 && (
            <ResumeDisplay 
              resumeId={viewResumeId}
              onPrevious={() => setCurrentStep(4)} 
              onComplete={() => setCurrentStep(6)} 
            /> 
          )}
          
          {currentStep === 6 && (
            <Portfolio 
              onPrevious={() => setCurrentStep(5)} 
              onComplete={() => setShowDashboard(true)} 
              portfolioId={viewPortfolioId} 
              onSidebarCollapse={setSidebarCollapsed}
            />
          )}

          {/* add other pages/components for other steps */}
        </>      
        )}
      </main>
    </div>
    <FinetunePage
      extractedData={extractedData}
      initialState={finetuneState}
      activeAnalysisId={activeAnalysisId}
      llmMode={onboardingData?.llmMode}
      onBack={() => navigate('/analysis/new/progress')}
      onComplete={(state, resLoc, portLoc, rId, pId) => {
        setFinetuneState(state);
        if (resLoc) {
          setResumeLocation(resLoc);
        }
        if (portLoc) {
          setPortfolioLocation(portLoc);
        }
        if (rId) {
          setViewResumeId(rId);
        }
        if (pId) {
          setViewPortfolioId(pId);
        }
        if (extractedData?.analysis_id) {
          setViewInsightsAnalysisId(extractedData.analysis_id);
        }
        navigate('/analysis/new/insights');
      }}
    />
  );
}

function PipelineInsightsPage() {
  const { viewInsightsAnalysisId } = useAnalysisPipeline();
  return <ProjectInsights analysisId={viewInsightsAnalysisId} viewMode="pipeline" />;
}

function PipelineResumePage() {
  const { viewResumeId } = useAnalysisPipeline();
  return <ResumeDisplay resumeId={viewResumeId} viewMode="pipeline" />;
}

function PipelinePortfolioPage() {
  const { viewPortfolioId } = useAnalysisPipeline();
  return <Portfolio portfolioId={viewPortfolioId} viewMode="pipeline" />;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      <Route element={<StandardLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/portfolio/:id" element={<Portfolio viewMode="standalone" />} />
        <Route path="/resume/:id" element={<ResumeDisplay viewMode="standalone" />} />
        <Route path="/insights/:id" element={<ProjectInsights viewMode="standalone" />} />
      </Route>

      <Route path="/analysis/new" element={<PipelineLayout />}>
        <Route path="onboarding" element={<PipelineOnboardingPage />} />
        <Route path="import" element={<PipelineImportPage />} />
        <Route path="progress" element={<PipelineProgressPage />} />
        <Route path="finetune" element={<PipelineFinetunePage />} />
        <Route path="insights" element={<PipelineInsightsPage />} />
        <Route path="resume" element={<PipelineResumePage />} />
        <Route path="portfolio" element={<PipelinePortfolioPage />} />
      </Route>
    </Routes>
  );
}

export default App;