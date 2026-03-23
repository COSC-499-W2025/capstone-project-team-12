import React, { useState, useRef, useEffect } from "react";

interface FinetunePageProps {
  extractedData?: any;
  initialState?: any;
  activeAnalysisId?: string | null;
  llmMode?: 'online' | 'local';
  onBack?: () => void;
  onStateChange?: (state: any) => void;
  onComplete: (state: any, resumeLocation: string | null, portfolioLocation: string | null, resumeId: number | null, portfolioId: number | null) => void;
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

export default function FinetunePage({ extractedData, initialState, activeAnalysisId, llmMode, onComplete, onBack, onStateChange }: FinetunePageProps) {
  // --- UI State ---
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [showProjectInfoModal, setShowProjectInfoModal] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isCommitting, setIsCommitting] = useState(false);

  const showToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => setToastMessage(null), 3000); // Hides after 3 seconds
  };

  // --- 1. Projects State & Drag-and-Drop ---
  const [projects, setProjects] = useState<Project[]>([]);

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
  const [topics, setTopics] = useState<TopicGroup[]>([]);
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

    // 1. Find the target topic
    const targetTopic = topics.find((t) => t.id === topicId);
    
    // 2. Check for duplicates BEFORE updating state
    if (targetTopic?.keywords.includes(keyword)) {
      showToast(`"${keyword}" is already in this topic!`);
      return; // Stop here, don't clear the input or update state
    }

    // 3. If unique, add it and clear the specific input
    setTopics((prev) =>
      prev.map((t) =>
        t.id === topicId ? { ...t, keywords: [...t.keywords, keyword] } : t
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
  const [skills, setSkills] = useState<Skill[]>([]);
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
    
    // Check for duplicate custom skills too!
    if (skills.some(s => s.name.toLowerCase() === skillName.toLowerCase())) {
      showToast(`"${skillName}" is already in your skills list!`);
      return;
    }

    const newSkill: Skill = {
      id: `s${Date.now()}`,
      name: skillName,
      selected: selectedSkillsCount < 3, 
    };
    setSkills((prev) => [...prev, newSkill]);
    setCustomSkillInput("");
  };

  // --- 4. Initialization & Persistence ---
  useEffect(() => {
    if (initialState && (initialState.projects?.length > 0 || initialState.topics?.length > 0 || initialState.skills?.length > 0)) {
      setProjects(initialState.projects || []);
      setTopics(initialState.topics || []);
      setSkills(initialState.skills || []);
    } else if (extractedData) {
      if (extractedData.analyzed_projects?.length) {
        setProjects(extractedData.analyzed_projects.map((p: any, i: number) => ({
          id: `p${i}`,
          name: p.repository_name,
          commits: Math.round((p.importance_score || 0) * 100), 
          selected: true
        })));
      }
      if (extractedData.topic_keywords?.length) {
        setTopics(extractedData.topic_keywords.map((t: any) => ({
          id: `t${t.topic_id ?? Date.now() + Math.random()}`,
          keywords: t.keywords || []
        })));
      }
      if (extractedData.detected_skills?.length) {
        setSkills(extractedData.detected_skills.map((s: string, i: number) => ({
          id: `s${i}`,
          name: s,
          selected: false 
        })));
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isMounted = useRef(false);
  useEffect(() => {
    if (isMounted.current && onStateChange) {
      onStateChange({ projects, topics, skills });
    } else {
      isMounted.current = true;
    }
  }, [projects, topics, skills, onStateChange]);

  const handleSubmit = async () => {
    if (!extractedData?.analysis_id) {
      console.warn("[FINETUNE] No analysis_id found! Executing frontend-only completion.");
      onComplete({ projects, topics, skills }, null, null, null, null);
      return;
    }

    setIsCommitting(true);
    try {
      const analysisId = extractedData.analysis_id;

      // 1. Commit Update
      const commitPayload = {
        topic_keywords: topics.map(t => ({
          topic_id: parseInt(t.id.replace('t', '')) || 0,
          keywords: t.keywords
        })),
        user_highlights: skills.filter(s => s.selected).map(s => s.name),
        selected_projects: projects.filter(p => p.selected).map(p => p.name),
        online_llm_consent: llmMode === 'online'
      };

      console.log(`\n============== [FINETUNE API LOGS] ==============`);
      console.log(`[FINETUNE] 1. Calling commit endpoint for Analysis ID: ${analysisId}`);
      console.log(`[FINETUNE] Commit Payload being sent:`, JSON.stringify(commitPayload, null, 2));

      const commitUrl = activeAnalysisId 
          ? `http://localhost:8080/projects/${analysisId}/update/commit`
          : `http://localhost:8080/projects/${analysisId}/upload/commit`;

      const commitRes = await fetch(commitUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(commitPayload)
      });
      
      console.log(`[FINETUNE] Commit Response Status:`, commitRes.status);
      if (!commitRes.ok) {
        const errText = await commitRes.text();
        console.error(`[FINETUNE] Commit API failed with body:`, errText);
        throw new Error("Commit API failed");
      }

      // 2. Generate Resume
      console.log(`\n[FINETUNE] 2. Calling Resume Generation Endpoint...`);
      const resumeResp = await fetch(`http://localhost:8080/resume/generate/${analysisId}`, { method: 'POST' });
      const resumeLocation = resumeResp.headers.get('location');
      const resumeData = await resumeResp.json().catch(() => ({}));
      console.log(`[FINETUNE] Resume Status:`, resumeResp.status);
      console.log(`[FINETUNE] Resume Location Header:`, resumeLocation);
      console.log(`[FINETUNE] Resume Body Data:`, resumeData);
      
      // 3. Generate Portfolio
      console.log(`\n[FINETUNE] 3. Calling Portfolio Generation Endpoint...`);
      const portResp = await fetch(`http://localhost:8080/portfolio/generate/${analysisId}`, { method: 'POST' });
      const portLocation = portResp.headers.get('location');
      const portData = await portResp.json().catch(() => ({}));
      console.log(`[FINETUNE] Portfolio Status:`, portResp.status);
      console.log(`[FINETUNE] Portfolio Location Header:`, portLocation);
      console.log(`[FINETUNE] Portfolio Body Data:`, portData);
      console.log(`=================================================\n`);

      onComplete(
        { projects, topics, skills },
        resumeLocation,
        portLocation,
        resumeData?.resume_id || null,
        portData?.portfolio_id || null
      );
      
    } catch (err) {
      console.error("[FINETUNE] Caught Exception during processing:", err);
      showToast("Error processing data. Check console.");
    } finally {
      setIsCommitting(false);
    }
  };

  return (
    <>
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
                <p className="text-xs text-[#9ca3af]">
                  Select and drag to reorder the repositories you want to feature.{" "}
                  <button 
                    onClick={() => setShowProjectInfoModal(true)}
                    className="text-[#6378ff] hover:text-[#a78bfa] underline underline-offset-2 transition-colors border-none bg-transparent cursor-pointer font-semibold p-0"
                  >
                    How are projects scored?
                  </button>
                </p>
              </div>
            </div>
            
            <div className="flex flex-col gap-3">
              {projects.length === 0 ? (
                <p className="text-sm text-[#9ca3af] italic">No projects found.</p>
              ) : (
                projects.map((project, index) => (
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
                      className={`flex-shrink-0 w-5 h-5 rounded-[6px] flex items-center justify-center transition-colors focus:outline-none border-none cursor-pointer
                        ${project.selected ? "bg-[#6378ff]" : "bg-[#eef0f6]"}
                      `}
                    >
                      {project.selected && (
                        <svg className="w-3.5 h-3.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      )}
                    </button>

                    <div className="flex-1 min-w-0 flex items-center justify-between cursor-pointer" onClick={() => toggleProject(project.id)}>
                      <p className="text-sm font-bold text-[#0f1629] truncate">{project.name}</p>
                      <p className="text-[11px] font-bold tracking-widest uppercase text-[#9ca3af]">{project.commits} score</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* --- Card 2: Fine-tune Topics --- */}
          <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.06)] shadow-[0_10px_40px_rgba(0,0,0,0.03)] p-8">
            <div className="mb-6 flex justify-between items-end">
              <div>
                <h2 className="text-lg font-bold text-[#0f1629] tracking-tight mb-1">Fine-tune Topics</h2>
                <p className="text-xs text-[#9ca3af]">
                  Edit the extracted topic vectors.{" "}
                  <button 
                    onClick={() => setShowInfoModal(true)}
                    className="text-[#6378ff] hover:text-[#a78bfa] underline underline-offset-2 transition-colors border-none bg-transparent cursor-pointer font-semibold p-0"
                  >
                    What are topic vectors?
                  </button>
                </p>
              </div>
              <button 
                onClick={addNewTopicGroup}
                className="flex items-center gap-1.5 text-[11px] font-bold tracking-widest uppercase text-[#6378ff] bg-[#6378ff]/10 hover:bg-[#6378ff]/20 px-3.5 py-2 rounded-lg transition-colors border-none cursor-pointer"
              >
                + Add Topic
              </button>
            </div>

            <div className="flex flex-col gap-4">
              {topics.length === 0 ? (
                <p className="text-sm text-[#9ca3af] italic">No topics extracted.</p>
              ) : (
                topics.map((topic, index) => (
                  <div 
                    key={topic.id} 
                    className="group flex flex-col md:flex-row items-start gap-4 p-5 rounded-xl border border-[#eef0f6] bg-[#f8f9fc] hover:border-[#c7d0ff] transition-colors"
                  >
                    <div className="w-full md:w-20 shrink-0 pt-1">
                      <span className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#0f1629]">
                        Topic {index}
                      </span>
                    </div>

                    <div className="flex-1 flex flex-wrap gap-2 items-center">
                      {topic.keywords.map((kw) => (
                        <span 
                          key={kw} 
                          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white border border-[#eef0f6] text-xs font-bold text-[#6b7280] shadow-[0_2px_10px_rgba(0,0,0,0.02)]"
                        >
                          {kw}
                          <button 
                            onClick={() => removeKeyword(topic.id, kw)} 
                            className="text-[#c4c9d4] hover:text-[#ef4444] transition-colors focus:outline-none border-none bg-transparent cursor-pointer p-0"
                            aria-label={`Remove ${kw}`}
                          >
                            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                              <line x1="18" y1="6" x2="6" y2="18" />
                              <line x1="6" y1="6" x2="18" y2="18" />
                            </svg>
                          </button>
                        </span>
                      ))}

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
                          className="text-[#6378ff] hover:text-[#a78bfa] disabled:opacity-50 disabled:cursor-not-allowed p-1 transition-colors border-none bg-transparent cursor-pointer"
                        >
                          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="12" y1="5" x2="12" y2="19" />
                            <line x1="5" y1="12" x2="19" y2="12" />
                          </svg>
                        </button>
                      </div>
                    </div>

                    <button 
                      onClick={() => removeTopicGroup(topic.id)}
                      title="Delete Topic Row"
                      className="shrink-0 p-2 text-[#9ca3af] hover:text-[#ef4444] hover:bg-[#ef4444]/10 rounded-lg transition-colors border-none bg-transparent mt-[-4px] md:mt-0 cursor-pointer"
                    >
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                        <path d="M10 11v6" />
                        <path d="M14 11v6" />
                      </svg>
                    </button>
                  </div>
                ))
              )}
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
              {skills.length === 0 ? (
                <p className="text-sm text-[#9ca3af] italic">No skills extracted.</p>
              ) : (
                skills.map((skill) => (
                  <button
                    key={skill.id}
                    onClick={() => toggleSkill(skill.id)}
                    disabled={!skill.selected && selectedSkillsCount >= 3}
                    className={`
                      px-4 py-2 rounded-xl text-xs font-bold transition-all duration-200 border-2 cursor-pointer
                      ${
                        skill.selected
                          ? "bg-[#6378ff]/10 text-[#6378ff] border-[#6378ff]/30"
                          : "bg-white text-[#6b7280] border-[#eef0f6] hover:border-[#a5b4fc] hover:text-[#0f1629] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:border-[#eef0f6] disabled:hover:text-[#6b7280]"
                      }
                    `}
                  >
                    {skill.name}
                  </button>
                ))
              )}
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
                className="text-[11px] tracking-widest uppercase font-bold text-white bg-[#0f1629] px-6 py-3.5 rounded-xl hover:bg-[#6b7280] transition-colors disabled:opacity-50 disabled:cursor-not-allowed border-none cursor-pointer"
              >
                Add Skill
              </button>
            </div>
          </div>

          {/* Divider & Actions */}
          <div className="h-px w-full bg-[#eef0f6] my-1" />

          <div className="flex items-center gap-4">
            {onBack && (
              <button
                onClick={onBack}
                disabled={isCommitting}
                className="py-4 px-6 rounded-xl font-bold text-sm transition-all duration-200 bg-white text-[#6b7280] border border-[#eef0f6] hover:border-[#c4c9d4] hover:text-[#0f1629] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shadow-[0_2px_10px_rgba(0,0,0,0.02)]"
              >
                Back
              </button>
            )}
            <button
              onClick={handleSubmit}
              disabled={isCommitting}
              className={`flex-1 py-4 rounded-xl border-none font-bold text-sm flex items-center justify-center gap-2 transition-all duration-300
                ${isCommitting 
                  ? "bg-gradient-to-br from-[#6378ff] to-[#a78bfa] text-white/80 cursor-wait" 
                  : "bg-gradient-to-br from-[#6378ff] to-[#a78bfa] text-white shadow-[0_4px_20px_rgba(99,120,255,0.3)] hover:shadow-[0_6px_28px_rgba(99,120,255,0.4)] hover:-translate-y-0.5 cursor-pointer"
                }`}
            >
              {isCommitting ? "Processing..." : "Confirm & Continue"}
              {!isCommitting && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              )}
            </button>
          </div>

        </div>
      </div>

      {/* --- Explanation Modal Overlay (Topics) --- */}
      {showInfoModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0f1629]/30 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl shadow-[0_20px_60px_rgba(0,0,0,0.15)] border border-[rgba(0,0,0,0.05)] w-full max-w-md p-7 relative">
            <h3 className="text-[20px] font-extrabold text-[#0f1629] tracking-tight mb-3">
              What are Topic Vectors?
            </h3>
            <div className="text-sm text-[#6b7280] leading-relaxed space-y-3 mb-7">
              <p>
                Topic vectors are like <strong>"underlying themes"</strong> that our AI discovered by scanning through your codebase using a machine learning library called Gensim.
              </p>
              <p>
                Instead of just looking for exact words, the AI groups together terms that frequently appear in the same context. For example, keywords like <code className="text-[#6378ff] font-bold font-mono bg-[#6378ff]/10 px-1.5 py-0.5 rounded">database</code>, <code className="text-[#6378ff] font-bold font-mono bg-[#6378ff]/10 px-1.5 py-0.5 rounded">sql</code>, and <code className="text-[#6378ff] font-bold font-mono bg-[#6378ff]/10 px-1.5 py-0.5 rounded">query</code> might be automatically clustered into a single topic representing your backend experience.
              </p>
              <p>
                By curating these lists—removing irrelevant words or adding missing technologies—you ensure the LLM focuses on the right themes when summarizing your resume!
              </p>
            </div>
            <button
              onClick={() => setShowInfoModal(false)}
              className="w-full py-3.5 rounded-xl font-bold text-sm bg-[#eef0f6] text-[#0f1629] hover:bg-[#e2e6f0] transition-colors border-none cursor-pointer"
            >
              Got it
            </button>
          </div>
        </div>
      )}

      {/* --- Explanation Modal Overlay (Projects) --- */}
      {showProjectInfoModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0f1629]/30 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl shadow-[0_20px_60px_rgba(0,0,0,0.15)] border border-[rgba(0,0,0,0.05)] w-full max-w-md p-7 relative">
            <h3 className="text-[20px] font-extrabold text-[#0f1629] tracking-tight mb-3">
              How are Projects Scored?
            </h3>
            <div className="text-sm text-[#6b7280] leading-relaxed space-y-3 mb-7">
              <p>
                Your projects are automatically assigned an <strong>Importance Score</strong> (from 0 to 100) using an algorithm that averages three normalized metrics from your repository history:
              </p>
              <ul className="list-disc pl-5 space-y-1.5">
                <li><strong>Commit Volume:</strong> The total number of commits you contributed.</li>
                <li><strong>Lines of Code:</strong> The volume of code you actively added to the project.</li>
                <li><strong>Project Duration:</strong> The lifespan of the project (days between first and last commit).</li>
              </ul>
              <p>
                These metrics are normalized, meaning small, dense projects can still rank highly against longer, sporadic ones. If you disagree with the algorithm, you can always drag and drop to manually adjust your feature order!
              </p>
            </div>
            <button
              onClick={() => setShowProjectInfoModal(false)}
              className="w-full py-3.5 rounded-xl font-bold text-sm bg-[#eef0f6] text-[#0f1629] hover:bg-[#e2e6f0] transition-colors border-none cursor-pointer"
            >
              Got it
            </button>
          </div>
        </div>
      )}

      {/*duplicate warning toast*/}
      {toastMessage && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-[#0f1629] text-white text-sm font-bold px-6 py-3.5 rounded-xl shadow-[0_10px_40px_rgba(0,0,0,0.2)] flex items-center gap-3 transition-all duration-300">
          <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          {toastMessage}
        </div>
      )}
    </>
  );
}