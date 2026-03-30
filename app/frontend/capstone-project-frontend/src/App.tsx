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
import { PipelinePhaseGuard, PipelineStageRedirect } from './components/PipelinePhaseGuard';

function PipelineOnboardingPage() {
  const navigate = useNavigate();
  const {
    onboardingData, setOnboardingData, resetPipeline, pipelineStage, setPipelineStage,
  } = useAnalysisPipeline();

  useEffect(() => {
    if (pipelineStage === 'onboarding') {
      resetPipeline();
    }
  }, [pipelineStage, resetPipeline]);

  return (
    <Onboarding
      initialData={onboardingData}
      mode="new-analysis"
      onComplete={(data) => {
        setOnboardingData(data);
        setPipelineStage('file-selection');
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
  const { setPipelineStage } = useAnalysisPipeline();

  return <ProgressPage onComplete={() => {
    setPipelineStage('finetune');
    navigate('/analysis/new/finetune');
  }} />;
}

function PipelineFinetunePage() {
  const navigate = useNavigate();
  const {
    extractedData, finetuneState, setFinetuneState, activeAnalysisId, onboardingData, setResumeLocation, setPortfolioLocation, setViewResumeId, setViewPortfolioId, setViewInsightsAnalysisId, setPipelineStage,
  } = useAnalysisPipeline();

  return (
    <FinetunePage
      extractedData={extractedData}
      initialState={finetuneState}
      activeAnalysisId={activeAnalysisId}
      llmMode={onboardingData?.llmMode}
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
        setPipelineStage('post-insights');
        navigate('/analysis/new/insights');
      }}
    />
  );
}

function PipelineInsightsPage() {
  const navigate = useNavigate();
  const { viewInsightsAnalysisId } = useAnalysisPipeline();

  return (
    <ProjectInsights
      analysisId={viewInsightsAnalysisId}
      viewMode="pipeline"
      onComplete={() => navigate('/analysis/new/resume')}
    />
  );
}

function PipelineResumePage() {
  const navigate = useNavigate();
  const { viewResumeId, onboardingData } = useAnalysisPipeline();

  return (
    <ResumeDisplay
      resumeId={viewResumeId}
      githubUsername={onboardingData?.githubUsername}
      userEmail={onboardingData?.email}
      viewMode="pipeline"
      onPrevious={() => navigate('/analysis/new/insights')}
      onComplete={() => navigate('/analysis/new/portfolio')}
    />
  );
}

function PipelinePortfolioPage() {
  const navigate = useNavigate();
  const { viewPortfolioId } = useAnalysisPipeline();

  return (
    <Portfolio
      portfolioId={viewPortfolioId}
      viewMode="pipeline"
      onPrevious={() => navigate('/analysis/new/resume')}
      onComplete={() => navigate('/dashboard')}
    />
  );
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
        <Route index element={<PipelineStageRedirect />} />
        <Route path="onboarding" element={<PipelinePhaseGuard phase="onboarding"><PipelineOnboardingPage /></PipelinePhaseGuard>} />
        <Route path="import" element={<PipelinePhaseGuard phase="import"><PipelineImportPage /></PipelinePhaseGuard>} />
        <Route path="progress" element={<PipelinePhaseGuard phase="progress"><PipelineProgressPage /></PipelinePhaseGuard>} />
        <Route path="finetune" element={<PipelinePhaseGuard phase="finetune"><PipelineFinetunePage /></PipelinePhaseGuard>} />
        <Route path="insights" element={<PipelinePhaseGuard phase="insights"><PipelineInsightsPage /></PipelinePhaseGuard>} />
        <Route path="resume" element={<PipelinePhaseGuard phase="resume"><PipelineResumePage /></PipelinePhaseGuard>} />
        <Route path="portfolio" element={<PipelinePhaseGuard phase="portfolio"><PipelinePortfolioPage /></PipelinePhaseGuard>} />
        <Route path="*" element={<PipelineStageRedirect />} />
      </Route>
    </Routes>
  );
}

export default App;