export type PipelineStage = 'onboarding' | 'file-selection' | 'finetune' | 'post-insights';

export type PipelinePhase =
  | 'onboarding'
  | 'import'
  | 'progress'
  | 'finetune'
  | 'insights'
  | 'resume'
  | 'portfolio';

export interface PipelineSidebarStep {
  id: number;
  label: string;
  phase: PipelinePhase;
  route: string;
}

export const pipelinePhaseRoutes: Record<PipelinePhase, string> = {
  onboarding: '/analysis/new/onboarding',
  import: '/analysis/new/import',
  progress: '/analysis/new/progress',
  finetune: '/analysis/new/finetune',
  insights: '/analysis/new/insights',
  resume: '/analysis/new/resume',
  portfolio: '/analysis/new/portfolio',
};

export const pipelineSidebarSteps: PipelineSidebarStep[] = [
  { id: 1, label: 'Onboarding', phase: 'onboarding', route: pipelinePhaseRoutes.onboarding },
  { id: 2, label: 'File Selection', phase: 'import', route: pipelinePhaseRoutes.import },
  { id: 3, label: 'Finetuning', phase: 'finetune', route: pipelinePhaseRoutes.finetune },
  { id: 4, label: 'Skills & Visualizations', phase: 'insights', route: pipelinePhaseRoutes.insights },
  { id: 5, label: 'Resume Creation', phase: 'resume', route: pipelinePhaseRoutes.resume },
  { id: 6, label: 'Portfolio Creation', phase: 'portfolio', route: pipelinePhaseRoutes.portfolio },
];

const allowedPhasesByStage: Record<PipelineStage, PipelinePhase[]> = {
  onboarding: ['onboarding'],
  'file-selection': ['onboarding', 'import', 'progress'],
  finetune: ['finetune'],
  'post-insights': ['insights', 'resume', 'portfolio'],
};

export function getAllowedPhasesForStage(stage: PipelineStage): PipelinePhase[] {
  return allowedPhasesByStage[stage];
}

export function getFallbackPathForStage(stage: PipelineStage): string {
  return pipelinePhaseRoutes[getAllowedPhasesForStage(stage)[0]];
}

export function getPipelinePhaseFromPath(pathname: string): PipelinePhase {
  if (pathname.includes('/analysis/new/import')) return 'import';
  if (pathname.includes('/analysis/new/progress')) return 'progress';
  if (pathname.includes('/analysis/new/finetune')) return 'finetune';
  if (pathname.includes('/analysis/new/insights')) return 'insights';
  if (pathname.includes('/analysis/new/resume')) return 'resume';
  if (pathname.includes('/analysis/new/portfolio')) return 'portfolio';
  return 'onboarding';
}

export function getPipelineStepIdForPhase(phase: PipelinePhase): number {
  if (phase === 'onboarding') return 1;
  if (phase === 'import' || phase === 'progress') return 2;
  if (phase === 'finetune') return 3;
  if (phase === 'insights') return 4;
  if (phase === 'resume') return 5;
  return 6;
}