export type AnalysisStatus = "complete" | "pending" | "error";
export type BadgeColor = "indigo" | "emerald" | "slate" | "amber";

export interface Analysis {
  id: string;
  label: string;
  createdAt: string;
  repos: string[];
  hasResume: boolean;
  hasPortfolio: boolean;
  hasInsights: boolean;
  status: AnalysisStatus;
}

export interface NewAnalysisPayload {
  label: string;
  repos: string[];
}

export interface AnalysisCardProps {
  analysis: Analysis;
  onDelete: (id: string) => void;
  onDeleteResume: (id: string) => void;
  onDeletePortfolio: (id: string) => void;
  onIncremental: (id: string, files: string[]) => void;
  onViewResume: (analysis: Analysis) => void;
  onViewPortfolio: (analysis: Analysis) => void;
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