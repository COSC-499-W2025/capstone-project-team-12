export type AnalysisStatus = "complete" | "pending" | "error";
export type BadgeColor = "indigo" | "emerald" | "slate" | "amber";

export interface Analysis {
  id: string;
  label: string;
  createdAt: string;
  repos: string[];
  resumeIds: number[];
  portfolioIds: number[];
  hasResume: boolean;
  hasPortfolio: boolean;
  hasInsights: boolean;
  status: AnalysisStatus;
}

export interface NewAnalysisPayload {
  label: string;
  repos: string[];
}

export interface DashboardProps {
  onNewAnalysis: () => void;
}

export interface AnalysisCardProps {
  analysis: Analysis;
  onDelete: (id: string) => void;
  onDeleteResume: (resumeId: number) => void;
  onDeletePortfolio: (portfolioId: number) => void;
  onIncremental: (id: string, files: string[]) => void;
  onViewResume: (analysis: Analysis, resumeId: number) => void;
  onViewPortfolio: (analysis: Analysis, portfolioId: number) => void;
  onViewInsights: (analysis: Analysis) => void;
}

export interface BadgeProps {
  label: string;
  color?: BadgeColor;
}

export interface IconButtonProps {
  onClick: () => void;
  title: string;
  className?: string;
  children: React.ReactNode;
}

export interface EmptyStateProps {
  onNew: () => void;
}

export interface ToastProps {
  message: string;
  onDismiss: () => void;
}

export interface RawProject {
  analysis_id: string;
  analysis_title: string | null;
  creation_date: string;
  metadata_insights: any;
  project_insights: any;
  file_path: string;
}

export interface RawResume {
  resume_id: number;
  analysis_id: string;
  resume_title: string | null;
  resume_data: any;
}

export interface RawPortfolio {
  portfolio_id: number;
  analysis_id: string;
  portfolio_title: string | null;
  portfolio_data: any;
}