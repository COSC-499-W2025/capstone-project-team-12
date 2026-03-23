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
    onboardingData,
    setOnboardingData,
    setActiveAnalysisId,
    setUploads,
    setExtractedData,
    setFinetuneState,
    setResumeLocation,
    setPortfolioLocation,
    setViewResumeId,
    setViewPortfolioId,
    setViewInsightsAnalysisId,
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
    setActiveAnalysisId,
    setUploads,
    setExtractedData,
    setFinetuneState,
    setResumeLocation,
    setPortfolioLocation,
    setViewResumeId,
    setViewPortfolioId,
    setViewInsightsAnalysisId,
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

function PipelineProgressPage() {
  const navigate = useNavigate();
  return <ProgressPage onComplete={() => navigate('/analysis/new/finetune')} />;
}

function PipelineFinetunePage() {
  const navigate = useNavigate();
  const {
    extractedData,
    finetuneState,
    setFinetuneState,
    activeAnalysisId,
    onboardingData,
    setResumeLocation,
    setPortfolioLocation,
    setViewResumeId,
    setViewPortfolioId,
    setViewInsightsAnalysisId,
  } = useAnalysisPipeline();

  return (
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