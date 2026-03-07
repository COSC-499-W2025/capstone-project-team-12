import { useState } from "react";
import OverviewTab from "./components/OverviewTab";
import TestingTab from "./components/TestingTab";
import DeploymentTab from "./components/DeploymentTab";
import PacingTab from "./components/PacingTab";
import type { Project, Technology, FileExtension } from "./insightTypes";

const projects: Project[] = [
  {
    id: 1,
    repoName: "COSC 360 Project",
    contribution: { level: "Top Contributor", rank: 1, percentile: 66.67 },
    collaboration: { teamSize: 3, isCollaborative: true, contributionShare: 46.03 },
    testing: {
      testFilesModified: 0, codeFilesModified: 26,
      testingPercentageFiles: 0.0, testLinesAdded: 0,
      codeLinesAdded: 836, testingPercentageLines: 0.0, hasTests: false,
    },
    deployment: { ciFiles: 0, dockerFiles: 0, infraFiles: 1, hasCI: false, hasDocker: false },
    versionControl: { totalCommits: 14, branches: 2, mergeCommits: 1, avgCommitMessageLength: 42 },
    technologies: [
      { name: "android.os", uses: 8 }, { name: "android.content", uses: 8 },
      { name: "android.widget", uses: 7 }, { name: "java.util", uses: 4 },
      { name: "android.graphics", uses: 4 }, { name: "android.view", uses: 4 },
    ] as Technology[],
    fileExtensions: [
      { ext: ".md",   count: 1,  size: 3987,   percentage: 0.69,  category: "Documentation" },
      { ext: ".xml",  count: 50, size: 2345,   percentage: 34.72, category: "Mobile App Dev" },
      { ext: ".json", count: 3,  size: 589406, percentage: 0.69,  category: "Other" },
      { ext: ".sql",  count: 1,  size: 564,    percentage: 18.75, category: "Database" },
      { ext: ".yml",  count: 1,  size: 345,    percentage: 6.94,  category: "DevOps" },
    ] as FileExtension[],
    pacing: { avgLinesPerCommit: 230, endHeavyPercent: 76 },
    userRole: {
      title: "Feature Developer",
      description: "Contributed a substantial amount of new code, indicating a strong role in implementing features and expanding the project's functionality.",
    },
    timeline: { start: "2025-04-01", end: "2025-04-05" },
  },
  {
    id: 2,
    repoName: "Personal Portfolio",
    contribution: { level: "Sole Contributor", rank: 1, percentile: 100 },
    collaboration: { teamSize: 1, isCollaborative: false, contributionShare: 100 },
    testing: {
      testFilesModified: 2, codeFilesModified: 14,
      testingPercentageFiles: 12.5, testLinesAdded: 120,
      codeLinesAdded: 540, testingPercentageLines: 18.2, hasTests: true,
    },
    deployment: { ciFiles: 1, dockerFiles: 0, infraFiles: 2, hasCI: true, hasDocker: false },
    versionControl: { totalCommits: 28, branches: 4, mergeCommits: 5, avgCommitMessageLength: 61 },
    technologies: [
      { name: "react", uses: 12 }, { name: "tailwindcss", uses: 10 },
      { name: "typescript", uses: 9 }, { name: "vite", uses: 5 },
      { name: "framer-motion", uses: 3 },
    ] as Technology[],
    fileExtensions: [
      { ext: ".tsx",  count: 18, size: 42000, percentage: 55.2, category: "Frontend" },
      { ext: ".css",  count: 4,  size: 8200,  percentage: 12.3, category: "Styling" },
      { ext: ".json", count: 2,  size: 1500,  percentage: 4.5,  category: "Other" },
      { ext: ".yml",  count: 2,  size: 980,   percentage: 6.0,  category: "DevOps" },
      { ext: ".md",   count: 3,  size: 5400,  percentage: 8.1,  category: "Documentation" },
    ] as FileExtension[],
    pacing: { avgLinesPerCommit: 98, endHeavyPercent: 38 },
    userRole: {
      title: "Full Stack Developer",
      description: "Sole contributor with broad ownership across the entire codebase, from UI components to deployment configuration.",
    },
    timeline: { start: "2025-02-10", end: "2025-03-28" },
  },
];

type Tab = "overview" | "testing" | "deployment" | "pacing & role";
const tabs: Tab[] = ["overview", "testing", "deployment", "pacing & role"];

export default function ProjectInsights() {
  const [selectedProject, setSelectedProject] = useState<Project>(projects[0]);
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const p = selectedProject;

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
                  selectedProject.id === proj.id
                    ? "bg-indigo-600 text-slate-600 border-indigo-600 shadow-md"
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
      </div>
    </div>
  );
}
