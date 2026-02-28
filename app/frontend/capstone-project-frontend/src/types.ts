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
  developer: string;
  coreCompetencies: string[];
  languages: Language[];
  projects: Project[];
}
