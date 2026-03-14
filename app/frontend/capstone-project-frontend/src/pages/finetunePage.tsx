import React, { useState, useRef } from "react";

interface FinetunePageProps {
  onComplete: (data: any) => void;
  extractedData?: any;
}

interface Project {
  id: string;
  name: string;
  commits: number;
  selected: boolean;
}

interface TopicGroup {
  id: string;
  keywords: string[];
}

interface Skill {
  id: string;
  name: string;
  selected: boolean;
}

export default function FinetunePage({ onComplete, extractedData }: FinetunePageProps) {
  // --- 1. Projects State & Drag-and-Drop ---
  const [projects, setProjects] = useState<Project[]>([
    { id: "p1", name: "Capstone Analysis Tool", commits: 140, selected: true },
    { id: "p2", name: "COSC 360 - Android App", commits: 85, selected: true },
    { id: "p3", name: "Personal Portfolio", commits: 42, selected: true },
  ]);

  const dragItem = useRef<number | null>(null);
  const dragOverItem = useRef<number | null>(null);

  const handleDragStart = (index: number) => { dragItem.current = index; };
  const handleDragEnter = (index: number) => { dragOverItem.current = index; };
  const handleDrop = () => {
    if (dragItem.current !== null && dragOverItem.current !== null) {
      const copy = [...projects];
      const draggedProject = copy[dragItem.current];
      copy.splice(dragItem.current, 1);
      copy.splice(dragOverItem.current, 0, draggedProject);
      setProjects(copy);
    }
    dragItem.current = null;
    dragOverItem.current = null;
  };

  const toggleProject = (id: string) => {
    setProjects((prev) =>
      prev.map((p) => (p.id === id ? { ...p, selected: !p.selected } : p))
    );
  };

  // --- 2. Topics State & Logic ---
  const [topics, setTopics] = useState<TopicGroup[]>([
    { id: "t0", keywords: ["user", "post", "blog", "comment", "account", "create", "like", "option", "name", "use"] },
    { id: "t1", keywords: ["post", "setting", "view", "recent", "account", "piggybank", "trend", "make", "save", "jane"] },
    { id: "t2", keywords: ["px", "content", "flex", "center", "border", "post", "margin", "align", "fit", "color"] },
    { id: "t3", keywords: ["color", "background", "content", "log", "white", "px", "piggybank", "arial", "pfp", "black"] },
    { id: "t4", keywords: ["id", "user", "post", "utf", "mb", "follow", "ibfk", "increment", "auto", "current"] },
  ]);
  const [newKeywordInputs, setNewKeywordInputs] = useState<Record<string, string>>({});

  const removeKeyword = (topicId: string, keywordToRemove: string) => {
    setTopics((prev) =>
      prev.map((t) =>
        t.id === topicId ? { ...t, keywords: t.keywords.filter((k) => k !== keywordToRemove) } : t
      )
    );
  };

  const addKeyword = (topicId: string) => {
    const keyword = newKeywordInputs[topicId]?.trim();
    if (!keyword) return;
    setTopics((prev) =>
      prev.map((t) =>
        t.id === topicId && !t.keywords.includes(keyword)
          ? { ...t, keywords: [...t.keywords, keyword] }
          : t
      )
    );
    setNewKeywordInputs((prev) => ({ ...prev, [topicId]: "" }));
  };

  const removeTopicGroup = (topicId: string) => {
    setTopics((prev) => prev.filter((t) => t.id !== topicId));
  };

  const addNewTopicGroup = () => {
    setTopics((prev) => [...prev, { id: `t${Date.now()}`, keywords: [] }]);
  };

  // --- 3. Skills State & Logic ---
  const [skills, setSkills] = useState<Skill[]>([
    { id: "s0", name: "PHP", selected: false },
    { id: "s1", name: "CSS", selected: false },
    { id: "s2", name: "JavaScript", selected: false },
    { id: "s3", name: "Web Development", selected: false },
    { id: "s4", name: "Backend Development", selected: false },
    { id: "s5", name: "Database", selected: false },
  ]);
  const [customSkillInput, setCustomSkillInput] = useState("");

  const selectedSkillsCount = skills.filter((s) => s.selected).length;

  const toggleSkill = (id: string) => {
    setSkills((prev) =>
      prev.map((s) => {
        if (s.id === id) {
          if (!s.selected && selectedSkillsCount >= 3) return s; // Max 3 limit
          return { ...s, selected: !s.selected };
        }
        return s;
      })
    );
  };

  const addCustomSkill = () => {
    const skillName = customSkillInput.trim();
    if (!skillName) return;
    const newSkill: Skill = {
      id: `s${Date.now()}`,
      name: skillName,
      selected: selectedSkillsCount < 3, 
    };
    setSkills((prev) => [...prev, newSkill]);
    setCustomSkillInput("");
  };

  const handleSubmit = () => {
    onComplete({ projects, topics, skills: skills.filter(s => s.selected) });
  };

  return (
    <div className="flex-1 min-h-screen bg-[#f8f9fc] flex justify-center font-sans px-6 py-10 overflow-y-auto relative">
      
      {/* Decorative Blurs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] right-[20%] w-[500px] h-[500px] rounded-full bg-[#6378ff]/5 blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[10%] w-[400px] h-[400px] rounded-full bg-[#a78bfa]/5 blur-[100px]" />
      </div>

      <div className="w-full max-w-[800px] relative z-10 flex flex-col gap-8 pb-20">
        
        {/* Page Header */}
        <div className="mb-2">
          <p className="text-[11px] font-bold tracking-[0.12em] uppercase text-[#6378ff] mb-2.5">
            Step 3 of 4
          </p>
          <h1 className="text-[26px] font-extrabold text-[#0f1629] tracking-[-0.02em] leading-tight mb-2">
            Fine-tune your analysis
          </h1>
          <p className="text-sm text-[#6b7280] leading-relaxed">
            Adjust the extracted data below. We will use these exact projects, topics, and skills to guide the LLM when generating your resume and insights.
          </p>
        </div>

        {/* --- Card 1: Rank & Select Projects --- */}
        <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.06)] shadow-[0_10px_40px_rgba(0,0,0,0.03)] p-8">
          <div className="mb-6 flex justify-between items-end">
            <div>
              <h2 className="text-lg font-bold text-[#0f1629] tracking-tight mb-1">Rank & Select Projects</h2>
              <p className="text-xs text-[#9ca3af]">Select and drag to reorder the repositories you want to feature.</p>
            </div>
          </div>
          
          <div className="flex flex-col gap-3">
            {projects.map((project, index) => (
              <div
                key={project.id}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragEnter={() => handleDragEnter(index)}
                onDragEnd={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className={`
                  flex items-center gap-4 p-4 rounded-xl border-2 cursor-grab active:cursor-grabbing transition-all duration-200 bg-white
                  ${project.selected ? "border-[#6378ff]/40 shadow-[0_4px_12px_rgba(99,120,255,0.05)]" : "border-[#eef0f6] hover:border-[#a5b4fc]"}
                `}
              >
                {/* Drag Handle Icon */}
                <svg className="w-5 h-5 text-[#c4c9d4] cursor-grab flex-shrink-0 hover:text-[#9ca3af] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 8h16M4 16h16" />
                </svg>

                {/* Checkbox */}
                <button
                  onClick={() => toggleProject(project.id)}
                  className={`flex-shrink-0 w-5 h-5 rounded-[6px] flex items-center justify-center transition-colors focus:outline-none
                    ${project.selected ? "bg-[#6378ff]" : "bg-[#eef0f6]"}
                  `}
                >
                  {project.selected && (
                    <svg className="w-3.5 h-3.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                </button>

                <div className="flex-1 min-w-0 flex items-center justify-between" onClick={() => toggleProject(project.id)}>
                  <p className="text-sm font-bold text-[#0f1629] truncate">{project.name}</p>
                  <p className="text-[11px] font-bold tracking-widest uppercase text-[#9ca3af]">{project.commits} commits</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* --- Card 2: Fine-tune Topics (Fully Re-designed) --- */}
        <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.06)] shadow-[0_10px_40px_rgba(0,0,0,0.03)] p-8">
          <div className="mb-6 flex justify-between items-end">
            <div>
              <h2 className="text-lg font-bold text-[#0f1629] tracking-tight mb-1">Fine-tune Topics</h2>
              <p className="text-xs text-[#9ca3af]">Edit the extracted topic vectors. Add or remove keywords to guide the generation.</p>
            </div>
            <button 
              onClick={addNewTopicGroup}
              className="flex items-center gap-1.5 text-[11px] font-bold tracking-widest uppercase text-[#6378ff] bg-[#6378ff]/10 hover:bg-[#6378ff]/20 px-3.5 py-2 rounded-lg transition-colors border-none"
            >
              + Add Topic
            </button>
          </div>

          <div className="flex flex-col gap-4">
            {topics.map((topic, index) => (
              <div 
                key={topic.id} 
                className="group flex flex-col md:flex-row items-start gap-4 p-5 rounded-xl border border-[#eef0f6] bg-[#f8f9fc] hover:border-[#c7d0ff] transition-colors"
              >
                {/* Left Label */}
                <div className="w-full md:w-20 shrink-0 pt-1">
                  <span className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#0f1629]">
                    Topic {index}
                  </span>
                </div>

                {/* Middle: Keyword Pills */}
                <div className="flex-1 flex flex-wrap gap-2 items-center">
                  {topic.keywords.map((kw) => (
                    <span 
                      key={kw} 
                      className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white border border-[#eef0f6] text-xs font-bold text-[#6b7280] shadow-[0_2px_10px_rgba(0,0,0,0.02)]"
                    >
                      {kw}
                      <button 
                        onClick={() => removeKeyword(topic.id, kw)} 
                        className="text-[#c4c9d4] hover:text-[#ef4444] transition-colors focus:outline-none"
                        aria-label={`Remove ${kw}`}
                      >
                        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <line x1="18" y1="6" x2="6" y2="18" />
                          <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                      </button>
                    </span>
                  ))}

                  {/* Add Keyword Input directly inside the pill list */}
                  <div className="flex items-center gap-1 bg-transparent px-1">
                    <input
                      type="text"
                      placeholder="Add keyword..."
                      value={newKeywordInputs[topic.id] || ""}
                      onChange={(e) => setNewKeywordInputs(prev => ({ ...prev, [topic.id]: e.target.value }))}
                      onKeyDown={(e) => e.key === "Enter" && addKeyword(topic.id)}
                      className="text-xs font-bold text-[#0f1629] placeholder-[#9ca3af] bg-transparent focus:outline-none w-28 transition-colors"
                    />
                    <button 
                      onClick={() => addKeyword(topic.id)} 
                      disabled={!newKeywordInputs[topic.id]?.trim()}
                      className="text-[#6378ff] hover:text-[#a78bfa] disabled:opacity-50 disabled:cursor-not-allowed p-1 transition-colors border-none bg-transparent"
                    >
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="12" y1="5" x2="12" y2="19" />
                        <line x1="5" y1="12" x2="19" y2="12" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Right Action: Delete Row */}
                <button 
                  onClick={() => removeTopicGroup(topic.id)}
                  title="Delete Topic Row"
                  className="shrink-0 p-2 text-[#9ca3af] hover:text-[#ef4444] hover:bg-[#ef4444]/10 rounded-lg transition-colors border-none bg-transparent mt-[-4px] md:mt-0"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                    <path d="M10 11v6" />
                    <path d="M14 11v6" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* --- Card 3: Highlight Skills --- */}
        <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.06)] shadow-[0_10px_40px_rgba(0,0,0,0.03)] p-8">
          <div className="mb-6 flex justify-between items-end">
            <div>
              <h2 className="text-lg font-bold text-[#0f1629] tracking-tight mb-1">Highlight Skills</h2>
              <p className="text-xs text-[#9ca3af]">Choose up to 3 core skills to anchor your summary.</p>
            </div>
            <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#6378ff]">
              Selected ({selectedSkillsCount}/3)
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5 mb-6">
            {skills.map((skill) => (
              <button
                key={skill.id}
                onClick={() => toggleSkill(skill.id)}
                disabled={!skill.selected && selectedSkillsCount >= 3}
                className={`
                  px-4 py-2 rounded-xl text-xs font-bold transition-all duration-200 border-2
                  ${
                    skill.selected
                      ? "bg-[#6378ff]/10 text-[#6378ff] border-[#6378ff]/30"
                      : "bg-white text-[#6b7280] border-[#eef0f6] hover:border-[#a5b4fc] hover:text-[#0f1629] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:border-[#eef0f6] disabled:hover:text-[#6b7280]"
                  }
                `}
              >
                {skill.name}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="e.g. Docker"
              value={customSkillInput}
              onChange={(e) => setCustomSkillInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addCustomSkill()}
              className="text-sm font-bold text-[#0f1629] placeholder-[#9ca3af] bg-[#f8f9fc] border border-[#eef0f6] rounded-xl focus:border-[#6378ff] focus:outline-none px-4 py-3 flex-1 transition-colors"
            />
            <button
              onClick={addCustomSkill}
              disabled={!customSkillInput.trim()}
              className="text-[11px] tracking-widest uppercase font-bold text-white bg-[#0f1629] px-6 py-3.5 rounded-xl hover:bg-[#6b7280] transition-colors disabled:opacity-50 disabled:cursor-not-allowed border-none"
            >
              Add Skill
            </button>
          </div>
        </div>

        {/* Divider & Confirm */}
        <div className="h-px w-full bg-[#eef0f6] my-1" />

        <button
          onClick={handleSubmit}
          className="w-full py-4 rounded-xl border-none font-bold text-sm flex items-center justify-center gap-2 transition-all duration-300 bg-gradient-to-br from-[#6378ff] to-[#a78bfa] text-white shadow-[0_4px_20px_rgba(99,120,255,0.3)] hover:shadow-[0_6px_28px_rgba(99,120,255,0.4)] hover:-translate-y-0.5 cursor-pointer"
        >
          Confirm & Continue
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </button>

      </div>
    </div>
  );
}