export interface Contribution {
  level: string;
  teamSize: number;
  rank: number;
  percentile: number;
  share: number;
}

export interface Stats {
  commits: number;
  files: number;
  added: number;
  deleted?: number;
  net: number;
}

export interface Project {
  id: number;
  name: string;
  timeline: string;
  duration: string;
  role: string;
  insight: string;
  contribution: Contribution;
  totals: Stats;
  mine: Stats;
  technologies: string[];
}

export interface Language {
  name: string;
  pct: number;
  files: number;
}

export interface PortfolioData {
  title: string;
  coreCompetencies: string[];
  languages: Language[];
  projects: Project[];
  growthMetrics: {
    has_comparison: boolean;
    earliest_project: string;
    latest_project: string;
    code_metrics: {
      commit_growth: number;
      file_growth: number;
      lines_growth: number;
      user_lines_growth: number;
  };
  technology_metrics: {
    framework_growth: number;
    earliest_frameworks: number;
    latest_frameworks: number;
  };
  testing_evolution: {
    testing_status: string;
    coverage_improvement: number;
    earliest_has_tests: boolean;
    latest_has_tests: boolean;
  };
  collaboration_evolution: {
    earliest_team_size: number;
    latest_team_size: number;
    earliest_level: string;
    latest_level: string;
    collaboration_summary: string;
  };
  role_evolution: {
    earliest_role: string;
    latest_role: string;
    role_changed: boolean;
  };
  framework_timeline_list?: {
    project_name: string;
    date_range: string;
    frameworks: string[];
    total_frameworks: number;
  }[];
  } | null;
}
