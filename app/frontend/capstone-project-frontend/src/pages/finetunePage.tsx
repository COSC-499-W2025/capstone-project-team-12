import React, { useState, useEffect } from "react";

interface FinetunePageProps {
  onComplete: (data: any) => void;
  extractedData?: any; // To be populated by API later
}

interface Project {
  id: string;
  name: string;
  commits: number;
  selected: boolean;
}

interface Topic {
  id: string;
  name: string;
  weight: number;
}

interface Skill {
  id: string;
  name: string;
  selected: boolean;
}

export default function FinetunePage({ onComplete, extractedData }: FinetunePageProps) {
  //mock data (will be replaced by extractedData mapping when API is connected)
  const [projects, setProjects] = useState<Project[]>([
    { id: "p1", name: "COSC 360 Project", commits: 14, selected: true },
    { id: "p2", name: "Personal Portfolio", commits: 28, selected: true },
    { id: "p3", name: "Algorithm Benchmarker", commits: 8, selected: false },
    { id: "p4", name: "FastAPI Backend Service", commits: 42, selected: true },
  ]);

  const [topics, setTopics] = useState<Topic[]>([
    { id: "t1", name: "Frontend Development", weight: 85 },
    { id: "t2", name: "API Design", weight: 60 },
    { id: "t3", name: "Database Management", weight: 30 },
    { id: "t4", name: "Data Visualization", weight: 45 },
  ]);

  const [skills, setSkills] = useState<Skill[]>([
    { id: "s1", name: "React", selected: true },
    { id: "s2", name: "TypeScript", selected: true },
    { id: "s3", name: "Python", selected: true },
    { id: "s4", name: "Tailwind CSS", selected: true },
    { id: "s5", name: "FastAPI", selected: false },
    { id: "s6", name: "Java", selected: false },
    { id: "s7", name: "SQL", selected: false },
    { id: "s8", name: "Docker", selected: false },
  ]);

  const toggleProject = (id: string) => {
    setProjects((prev) =>
      prev.map((p) => (p.id === id ? { ...p, selected: !p.selected } : p))
    );
  };

  const updateTopicWeight = (id: string, newWeight: number) => {
    const clamped = Math.max(0, Math.min(100, newWeight));
    setTopics((prev) =>
      prev.map((t) => (t.id === id ? { ...t, weight: clamped } : t))
    );
  };

  const toggleSkill = (id: string) => {
    setSkills((prev) =>
      prev.map((s) => (s.id === id ? { ...s, selected: !s.selected } : s))
    );
  };

  const handleSubmit = () => {
    // Package the finalized data to send to the Step 2 /commit API later
    onComplete({ projects, topics, skills });
  };

  return (
    <div className="flex-1 min-h-screen bg-[#f8f9fc] flex justify-center font-sans px-6 py-10 overflow-y-auto relative">
      
      {/* Decorative gradient blurs matching onboarding */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] right-[20%] w-[500px] h-[500px] rounded-full bg-[#6378ff] opacity-[0.03] blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[10%] w-[400px] h-[400px] rounded-full bg-[#a78bfa] opacity-[0.03] blur-[100px]" />
      </div>

      <div className="w-full max-w-[720px] relative z-10 flex flex-col gap-8 pb-20">
        
        {/* Page Header */}
        <div className="mb-2">
          <p className="text-[11px] font-bold tracking-[0.12em] uppercase text-[#6378ff] mb-2.5">
            Step 3 of 4
          </p>
          <h1 className="text-[26px] font-extrabold text-[#0f1629] tracking-[-0.02em] leading-tight mb-2">
            Fine-tune your profile
          </h1>
          <p className="text-sm text-[#6b7280] leading-relaxed">
            Adjust the extracted data below. We will use these exact weights, projects, and skills to guide the LLM when generating your resume and insights.
          </p>
        </div>

        {/* Section 1: Select Projects */}
        <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.06)] shadow-[0_10px_40px_rgba(0,0,0,0.03)] p-8">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-[#0f1629] tracking-tight mb-1">
              Select Projects
            </h2>
            <p className="text-xs text-[#9ca3af]">
              Select the repositories you want to feature on your resume.
            </p>
          </div>
          
          <div className="flex flex-col gap-3">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => toggleProject(project.id)}
                className={`
                  flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all duration-200
                  ${
                    project.selected
                      ? "border-[#6378ff] bg-[#6378ff]/[0.02]"
                      : "border-[#eef0f6] hover:border-[#a5b4fc] hover:bg-[#f3f4f8]"
                  }
                `}
              >
                {/* Custom Checkbox */}
                <div
                  className={`
                    flex-shrink-0 w-5 h-5 rounded-[6px] flex items-center justify-center transition-colors
                    ${project.selected ? "bg-[#6378ff]" : "bg-[#eef0f6]"}
                  `}
                >
                  {project.selected && (
                    <svg className="w-3.5 h-3.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                </div>
                <div>
                  <p className="text-sm font-bold text-[#0f1629] mb-0.5">
                    {project.name}
                  </p>
                  <p className="text-xs font-semibold text-[#9ca3af]">
                    {project.commits} commit{project.commits !== 1 ? "s" : ""}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 2: Fine-tune Topics */}
        <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.06)] shadow-[0_10px_40px_rgba(0,0,0,0.03)] p-8">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-[#0f1629] tracking-tight mb-1">
              Fine-tune Topics
            </h2>
            <p className="text-xs text-[#9ca3af]">
              Adjust topic weights to reflect your actual expertise.
            </p>
          </div>

          <div className="flex flex-col gap-6">
            {topics.map((topic) => (
              <div key={topic.id} className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-bold text-[#6b7280]">
                    {topic.name}
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={topic.weight}
                      onChange={(e) => updateTopicWeight(topic.id, parseInt(e.target.value) || 0)}
                      className="w-16 text-right text-sm font-bold text-[#0f1629] bg-[#eef0f6] border border-transparent rounded-lg py-1.5 px-3 focus:outline-none focus:border-[#6378ff] focus:bg-white transition-all appearance-none"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-[#9ca3af] pointer-events-none">%</span>
                  </div>
                </div>
                {/* Progress Bar Track */}
                <div className="w-full bg-[#eef0f6] rounded-full h-2.5 overflow-hidden border border-[rgba(0,0,0,0.04)] shadow-inner">
                  <div
                    className="h-full rounded-full transition-all duration-300 ease-out bg-gradient-to-r from-[#6378ff] to-[#a78bfa]"
                    style={{ width: `${topic.weight}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 3: Highlight Skills */}
        <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.06)] shadow-[0_10px_40px_rgba(0,0,0,0.03)] p-8">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-[#0f1629] tracking-tight mb-1">
              Highlight Skills
            </h2>
            <p className="text-xs text-[#9ca3af]">
              Select the specific technologies you want explicitly highlighted.
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5">
            {skills.map((skill) => (
              <button
                key={skill.id}
                onClick={() => toggleSkill(skill.id)}
                className={`
                  px-4 py-2 rounded-xl text-sm font-bold transition-all duration-200 border-2
                  ${
                    skill.selected
                      ? "bg-[#6378ff]/10 text-[#6378ff] border-[#6378ff]/30"
                      : "bg-white text-[#6b7280] border-[#eef0f6] hover:border-[#a5b4fc] hover:text-[#0f1629]"
                  }
                `}
              >
                {skill.name}
              </button>
            ))}
          </div>
        </div>

        {/* Divider */}
        <div className="h-px w-full bg-[#eef0f6] my-2" />

        {/* Confirm Button */}
        <button
          onClick={handleSubmit}
          className="w-full py-4 rounded-xl border-none font-bold text-sm flex items-center justify-center gap-2 transition-all duration-300 bg-gradient-to-br from-[#6378ff] to-[#a78bfa] text-white shadow-[0_4px_20px_rgba(99,120,255,0.3)] hover:shadow-[0_6px_28px_rgba(99,120,255,0.4)] hover:-translate-y-0.5 cursor-pointer"
        >
          Save & Generate Results
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </button>

      </div>
    </div>
  );
}