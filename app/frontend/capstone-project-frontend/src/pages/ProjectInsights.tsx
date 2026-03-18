import { useState, useEffect } from "react";
import OverviewTab from "../components/OverviewTab";
import TestingTab from "../components/TestingTab";
import DeploymentTab from "../components/DeploymentTab";
import PacingTab from "../components/PacingTab";
import type { Project, Technology, FileExtension } from "../types/insightTypes";


type Tab = "overview" | "testing" | "deployment" | "pacing & role";
const tabs: Tab[] = ["overview", "testing", "deployment", "pacing & role"];


// ---- Mapping Function ----
function mapToProjects(raw: any): Project[] {
  const insights = raw.project_insights?.analyzed_insights ?? [];
  return insights.map((p: any, i: number) => ({
    id: i + 1,
    repoName: p.repository_name ?? 'Unknown',
    contribution: {
      level: p.contribution_analysis?.contribution_level ?? '',
      rank: p.contribution_analysis?.rank_by_commits ?? 1,
      percentile: p.contribution_analysis?.percentile ?? 0,
    },
    collaboration: {
      teamSize: p.repository_context?.all_commits_dates ? 
        Object.keys(p.repository_context?.all_authors_stats ?? {}).length : 1,
      isCollaborative: p.collaboration_insights?.is_collaborative ?? false,
      contributionShare: p.collaboration_insights?.user_contribution_share_percentage ?? 100,
    },
    testing: {
      testFilesModified: p.testing_insights?.test_files_modified ?? 0,
      codeFilesModified: p.testing_insights?.code_files_modified ?? 0,
      testingPercentageFiles: p.testing_insights?.testing_percentage_files ?? 0,
      testLinesAdded: p.testing_insights?.test_lines_added ?? 0,
      codeLinesAdded: p.testing_insights?.code_lines_added ?? 0,
      testingPercentageLines: p.testing_insights?.testing_percentage_lines ?? 0,
      hasTests: p.testing_insights?.has_tests ?? false,
    },
    deployment: {
      ciFiles: p.success_indicators?.deployment?.has_cicd ? 1 : 0,
      dockerFiles: p.success_indicators?.deployment?.has_containerization ? 1 : 0,
      hasCI: p.success_indicators?.deployment?.has_cicd ?? false,
      hasDocker: p.success_indicators?.deployment?.has_containerization ?? false,
      cicdTools: p.success_indicators?.deployment?.cicd_tools ?? [],
      containerizationTools: p.success_indicators?.deployment?.containerization_tools ?? [],
      hostingPlatforms: p.success_indicators?.deployment?.hosting_platforms ?? [],
    },
    versionControl: {
      totalCommits: p.statistics?.user_commits ?? p.user_commits?.length ?? 0,
      branches: 1,
      mergeCommits: 0,
      avgCommitMessageLength: 0,
    },
    technologies: Object.entries(raw.metadata_insights?.language_stats ?? {})
      .map(([name, stats]: [string, any]) => ({ name, uses: stats.file_count })),
    fileExtensions: Object.entries(raw.metadata_insights?.extension_stats ?? {})
      .map(([ext, stats]: [string, any]) => ({
        ext,
        count: stats.count,
        size: stats.total_size,
        percentage: stats.percentage,
        category: stats.category,
      })),
    pacing: {
      avgLinesPerCommit: p.success_indicators?.version_control?.avg_lines_per_commit ?? 0,
      endHeavyPercent: (() => {
        const msg = p.success_indicators?.version_control?.commit_consistency ?? '';
        const match = msg.match(/(\d+\.?\d*)%/);
        return match ? parseFloat(match[1]) : 0;
      })(),
      commitConsistency: p.success_indicators?.version_control?.commit_consistency ?? '',
    },
    userRole: {
      title: p.user_role?.role ?? '',
      description: p.user_role?.blurb ?? '',
    },
    timeline: {
      start: formatDate(p.dates?.start_date ?? ''),
      end: formatDate(p.dates?.end_date ?? ''),
    },
  }));
}

function formatDate(iso: string): string {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

// TEMPORARY: Mock data for demo/development. Remove or comment out when integrating real backend flow.
const MOCK_PROJECTS: Project[] = [
  {
    id: 1,
    repoName: "capstone-project-team-12",
    contribution: { level: "High contributor", rank: 2, percentile: 85 },
    collaboration: { teamSize: 5, isCollaborative: true, contributionShare: 65 },
    testing: { testFilesModified: 12, codeFilesModified: 45, testingPercentageFiles: 21, testLinesAdded: 340, codeLinesAdded: 1250, testingPercentageLines: 21, hasTests: true },
    deployment: { ciFiles: 1, dockerFiles: 2, infraFiles: 0, hasCI: true, hasDocker: true, cicdTools: ["GitHub Actions"], containerizationTools: ["Docker"], hostingPlatforms: ["Heroku"] },
    versionControl: { totalCommits: 142, branches: 8, mergeCommits: 15, avgCommitMessageLength: 45 },
    technologies: [{ name: "TypeScript", uses: 38 }, { name: "React", uses: 35 }, { name: "Python", uses: 28 }, { name: "Docker", uses: 12 }],
    fileExtensions: [{ ext: "tsx", count: 28, size: 125000, percentage: 32, category: "Frontend" }, { ext: "py", count: 19, size: 85000, percentage: 22, category: "Backend" }, { ext: "json", count: 15, size: 45000, percentage: 11, category: "Config" }],
    pacing: { avgLinesPerCommit: 45, endHeavyPercent: 15, commitConsistency: "Consistent (80% of commits within 5-50 line range)" },
    userRole: { title: "Full-Stack Developer", description: "Led frontend architecture and database schema design" },
    timeline: { start: "Jan 2025", end: "Mar 2026" },
  },
  {
    id: 2,
    repoName: "personal-portfolio",
    contribution: { level: "Solo developer", rank: 1, percentile: 100 },
    collaboration: { teamSize: 1, isCollaborative: false, contributionShare: 100 },
    testing: { testFilesModified: 4, codeFilesModified: 22, testingPercentageFiles: 15, testLinesAdded: 120, codeLinesAdded: 680, testingPercentageLines: 15, hasTests: true },
    deployment: { ciFiles: 1, dockerFiles: 0, infraFiles: 0, hasCI: true, hasDocker: false, cicdTools: ["GitHub Pages"], containerizationTools: [], hostingPlatforms: ["GitHub Pages", "Vercel"] },
    versionControl: { totalCommits: 87, branches: 3, mergeCommits: 0, avgCommitMessageLength: 32 },
    technologies: [{ name: "React", uses: 24 }, { name: "TypeScript", uses: 20 }, { name: "Tailwind CSS", uses: 16 }, { name: "Next.js", uses: 14 }],
    fileExtensions: [{ ext: "tsx", count: 18, size: 92000, percentage: 55, category: "Frontend" }, { ext: "css", count: 8, size: 42000, percentage: 25, category: "Styling" }],
    pacing: { avgLinesPerCommit: 28, endHeavyPercent: 8, commitConsistency: "Very consistent (92% of commits within 3-30 line range)" },
    userRole: { title: "UI/UX Developer", description: "Designed and built responsive portfolio showcasing web development skills" },
    timeline: { start: "Jun 2024", end: "Jan 2025" },
  },
];

export default function ProjectInsights( { onComplete, onPrevious, analysisId }: { onComplete?: () => void, onPrevious?: () => void, analysisId?: string | null }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(analysisId != null);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  useEffect(() => {
    // TEMPORARY: Use mock data if no analysisId provided. Remove when real backend flow wired.
    if (analysisId == null) {
      setProjects(MOCK_PROJECTS);
      setSelectedProject(MOCK_PROJECTS[0] ?? null);
      setLoading(false);
      return;
    }
    
    fetch('http://localhost:8080/projects')
      .then(r => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then((data: any[]) => {
        const match = data.find(d => d.analysis_id === analysisId);
        if (!match) throw new Error('Analysis not found');
        const mapped = mapToProjects(match);
        setProjects(mapped);
        setSelectedProject(mapped[0] ?? null);  // set initial selection here
        setLoading(false);
      })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [analysisId]);

  if (loading) return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><p className="text-slate-500">Loading insights...</p></div>;
  if (error) return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><p className="text-red-500">Error: {error}</p></div>;

  const p = selectedProject;
  if (!p) return null;

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <div className="max-w-4xl mx-auto px-6 py-10">

        <div className="mb-6">
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-500 mb-1">Skills & Visualizations</p>
          <h1 className="text-3xl font-bold text-slate-800">Here are your tailored insights.</h1>
        </div>

        {/* Project selector */}
        <div className="mb-7">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Repository</p>
          <div className="flex flex-wrap gap-2">
            {projects.map((proj) => (
              <button
                key={proj.id}
                onClick={() => { setSelectedProject(proj); setActiveTab("overview"); }}
                className={`px-4 py-2 rounded-xl text-sm font-semibold border transition-all ${
                  selectedProject?.id === proj.id
                    ? "bg-indigo-600 text-white border-indigo-600 shadow-md"
                    : "bg-white text-slate-600 border-slate-200 hover:border-indigo-300 hover:text-indigo-600"
                }`}
              >
                {proj.repoName}
              </button>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-7 bg-slate-200 rounded-xl p-1 w-fit flex-wrap">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg text-xs font-semibold capitalize transition-all ${
                activeTab === tab ? "bg-white text-indigo-700 shadow-sm" : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {activeTab === "overview"      && <OverviewTab   p={p} />}
        {activeTab === "testing"       && <TestingTab    p={p} />}
        {activeTab === "deployment"    && <DeploymentTab p={p} />}
        {activeTab === "pacing & role" && <PacingTab     p={p} />}

          {/* Back button */}
          <div className="flex justify-between mt-8">
            <button
              onClick={onPrevious}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
              Back
            </button>
          
            {/* Next button */}
            <button
              onClick={onComplete}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all"
            >
              Next
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>          
      </div>
      
    </div>
  );
}
