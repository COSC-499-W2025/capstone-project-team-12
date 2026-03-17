export interface Technology {
  name: string;
  uses: number;
}

export interface FileExtension {
  ext: string;
  count: number;
  size: number;
  percentage: number;
  category: string;
}

export interface Contribution {
  level: string;
  rank: number;
  percentile: number;
}

export interface Collaboration {
  teamSize: number;
  isCollaborative: boolean;
  contributionShare: number;
}

export interface Testing {
  testFilesModified: number;
  codeFilesModified: number;
  testingPercentageFiles: number;
  testLinesAdded: number;
  codeLinesAdded: number;
  testingPercentageLines: number;
  hasTests: boolean;
}

export interface Deployment {
  ciFiles: number;
  dockerFiles: number;
  infraFiles: number;
  hasCI: boolean;
  hasDocker: boolean;
}

export interface VersionControl {
  totalCommits: number;
  branches: number;
  mergeCommits: number;
  avgCommitMessageLength: number;
}

export interface Pacing {
  avgLinesPerCommit: number;
  endHeavyPercent: number;
  commitConsistency: string;
}

export interface UserRole {
  title: string;
  description: string;
}

export interface Timeline {
  start: string;
  end: string;
}

export interface Project {
  id: number;
  repoName: string;
  contribution: Contribution;
  collaboration: Collaboration;
  testing: Testing;
  deployment: Deployment;
  versionControl: VersionControl;
  technologies: Technology[];
  fileExtensions: FileExtension[];
  pacing: Pacing;
  userRole: UserRole;
  timeline: Timeline;
}