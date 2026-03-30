import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAnalysisPipeline } from '../context/AnalysisPipelineContext';
import { getFallbackPathForStage, type PipelinePhase } from '../utils/pipelineAccess';

export function PipelinePhaseGuard({ phase, children }: { phase: PipelinePhase; children: ReactNode }) {
  const { pipelineStage, isPhaseAccessible } = useAnalysisPipeline();

  if (!isPhaseAccessible(phase)) {
    return <Navigate to={getFallbackPathForStage(pipelineStage)} replace />;
  }

  return <>{children}</>;
}

export function PipelineStageRedirect() {
  const { pipelineStage } = useAnalysisPipeline();
  return <Navigate to={getFallbackPathForStage(pipelineStage)} replace />;
}