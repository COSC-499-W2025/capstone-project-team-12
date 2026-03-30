import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import type { UploadEntry } from '../pages/fileImport';
import { getAllowedPhasesForStage, type PipelinePhase, type PipelineStage } from '../utils/pipelineAccess';

export interface OnboardingData {
  llmMode: 'online' | 'local';
  githubUsername: string;
  email: string;
}

interface AnalysisPipelineContextValue {
  onboardingData: OnboardingData | null;
  setOnboardingData: (data: OnboardingData | null) => void;
  uploads: UploadEntry[];
  setUploads: (uploads: UploadEntry[]) => void;
  extractedData: any;
  setExtractedData: (data: any) => void;
  finetuneState: any;
  setFinetuneState: (state: any) => void;
  resumeLocation: string | null;
  setResumeLocation: (location: string | null) => void;
  portfolioLocation: string | null;
  setPortfolioLocation: (location: string | null) => void;
  activeAnalysisId: string | null;
  setActiveAnalysisId: (id: string | null) => void;
  viewResumeId: number | null;
  setViewResumeId: (id: number | null) => void;
  viewPortfolioId: number | null;
  setViewPortfolioId: (id: number | null) => void;
  viewInsightsAnalysisId: string | null;
  setViewInsightsAnalysisId: (id: string | null) => void;
  pipelineStage: PipelineStage;
  setPipelineStage: (stage: PipelineStage) => void;
  allowedPhases: PipelinePhase[];
  isPhaseAccessible: (phase: PipelinePhase) => boolean;
  resetPipeline: () => void;
}

const AnalysisPipelineContext = createContext<AnalysisPipelineContextValue | null>(null);

export function AnalysisPipelineProvider({ children }: { children: ReactNode }) {
  const [onboardingData, setOnboardingData] = useState<OnboardingData | null>(null);
  const [uploads, setUploads] = useState<UploadEntry[]>([]);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [finetuneState, setFinetuneState] = useState<any>(null);
  const [resumeLocation, setResumeLocation] = useState<string | null>(null);
  const [portfolioLocation, setPortfolioLocation] = useState<string | null>(null);
  const [activeAnalysisId, setActiveAnalysisId] = useState<string | null>(null);
  const [viewResumeId, setViewResumeId] = useState<number | null>(null);
  const [viewPortfolioId, setViewPortfolioId] = useState<number | null>(null);
  const [viewInsightsAnalysisId, setViewInsightsAnalysisId] = useState<string | null>(null);
  const [pipelineStage, setPipelineStage] = useState<PipelineStage>('onboarding');

  const resetPipeline = useCallback(() => {
    setOnboardingData(null);
    setUploads([]);
    setExtractedData(null);
    setFinetuneState(null);
    setResumeLocation(null);
    setPortfolioLocation(null);
    setActiveAnalysisId(null);
    setViewResumeId(null);
    setViewPortfolioId(null);
    setViewInsightsAnalysisId(null);
    setPipelineStage('onboarding');
  }, []);

  const allowedPhases = useMemo(() => getAllowedPhasesForStage(pipelineStage), [pipelineStage]);
  const isPhaseAccessible = useCallback(
    (phase: PipelinePhase) => allowedPhases.includes(phase),
    [allowedPhases],
  );

  return (
    <AnalysisPipelineContext.Provider
      value={{
        onboardingData, setOnboardingData, uploads, setUploads, extractedData, setExtractedData, finetuneState, setFinetuneState, resumeLocation, setResumeLocation, portfolioLocation, setPortfolioLocation,
        activeAnalysisId,
        setActiveAnalysisId,
        viewResumeId,
        setViewResumeId,
        viewPortfolioId,
        setViewPortfolioId,
        viewInsightsAnalysisId,
        setViewInsightsAnalysisId,
        pipelineStage,
        setPipelineStage,
        allowedPhases,
        isPhaseAccessible,
        resetPipeline,
      }}
    >
      {children}
    </AnalysisPipelineContext.Provider>
  );
}

export function useAnalysisPipeline() {
  const context = useContext(AnalysisPipelineContext);
  if (!context) {
    throw new Error('useAnalysisPipeline must be used within AnalysisPipelineProvider');
  }
  return context;
}
