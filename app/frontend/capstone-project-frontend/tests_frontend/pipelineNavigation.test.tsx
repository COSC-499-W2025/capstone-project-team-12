import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Sidebar from '../src/components/sidebar';
import { PipelinePhaseGuard, PipelineStageRedirect } from '../src/components/PipelinePhaseGuard';

const mockNavigate = vi.fn();
const mockUseAnalysisPipeline = vi.fn();

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../src/context/AnalysisPipelineContext', () => ({
  useAnalysisPipeline: () => mockUseAnalysisPipeline(),
}));

vi.mock('../src/components/modals', () => ({
  Modal: () => null,
}));

function setPipelineContext(overrides: Record<string, unknown> = {}) {
  mockUseAnalysisPipeline.mockReturnValue({
    pipelineStage: 'onboarding',
    allowedPhases: ['onboarding'],
    isPhaseAccessible: (phase: string) => phase === 'onboarding',
    ...overrides,
  });
}

describe('Pipeline route guards', () => {
  beforeEach(() => {
    setPipelineContext();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('redirects a locked direct URL to the first allowed phase', () => {
    render(
      <MemoryRouter initialEntries={['/analysis/new/finetune']}>
        <Routes>
          <Route path="/analysis/new/onboarding" element={<div>Onboarding Page</div>} />
          <Route
            path="/analysis/new/finetune"
            element={
              <PipelinePhaseGuard phase="finetune">
                <div>Finetune Page</div>
              </PipelinePhaseGuard>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Onboarding Page')).toBeInTheDocument();
    expect(screen.queryByText('Finetune Page')).not.toBeInTheDocument();
  });

  it('allows an unlocked direct URL to render normally', () => {
    setPipelineContext({
      pipelineStage: 'finetune',
      allowedPhases: ['finetune'],
      isPhaseAccessible: (phase: string) => phase === 'finetune',
    });

    render(
      <MemoryRouter initialEntries={['/analysis/new/finetune']}>
        <Routes>
          <Route path="/analysis/new/onboarding" element={<div>Onboarding Page</div>} />
          <Route
            path="/analysis/new/finetune"
            element={
              <PipelinePhaseGuard phase="finetune">
                <div>Finetune Page</div>
              </PipelinePhaseGuard>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Finetune Page')).toBeInTheDocument();
  });

  it('redirects the pipeline index to the current stage entry point', () => {
    setPipelineContext({
      pipelineStage: 'post-insights',
      allowedPhases: ['insights', 'resume', 'portfolio'],
      isPhaseAccessible: (phase: string) => ['insights', 'resume', 'portfolio'].includes(phase),
    });

    render(
      <MemoryRouter initialEntries={['/analysis/new']}>
        <Routes>
          <Route path="/analysis/new" element={<PipelineStageRedirect />} />
          <Route path="/analysis/new/insights" element={<div>Insights Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Insights Page')).toBeInTheDocument();
  });
});

describe('Pipeline sidebar locking', () => {
  beforeEach(() => {
    setPipelineContext({
      pipelineStage: 'file-selection',
      allowedPhases: ['onboarding', 'import', 'progress'],
      isPhaseAccessible: (phase: string) => ['onboarding', 'import', 'progress'].includes(phase),
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('marks later phases as locked and prevents navigation', () => {
    render(
      <MemoryRouter initialEntries={['/analysis/new/import']}>
        <Sidebar />
      </MemoryRouter>
    );

    const finetuneButton = screen.getByRole('button', { name: /finetuning/i });
    const onboardingButton = screen.getByRole('button', { name: /onboarding/i });

    expect(finetuneButton).toHaveAttribute('aria-disabled', 'true');
    expect(onboardingButton).toHaveAttribute('aria-disabled', 'false');

    fireEvent.click(finetuneButton);
    fireEvent.click(onboardingButton);

    expect(mockNavigate).toHaveBeenCalledTimes(1);
    expect(mockNavigate).toHaveBeenCalledWith('/analysis/new/onboarding');
  });
});