import { useState } from 'react';
import { createPortal } from 'react-dom';
import { useLocation, useNavigate } from 'react-router-dom';
import { Modal } from './modals';
import { useAnalysisPipeline } from '../context/AnalysisPipelineContext';
import { getPipelinePhaseFromPath, getPipelineStepIdForPhase, pipelineSidebarSteps } from '../utils/pipelineAccess';

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const Maps = navigate;
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const { isPhaseAccessible } = useAnalysisPipeline();

  const currentPhase = getPipelinePhaseFromPath(location.pathname);
  const currentStep = getPipelineStepIdForPhase(currentPhase);

  return (
    <div style={{
      width: "240px",
      height: "100vh",
      background: "linear-gradient(160deg, #1e2433 0%, #252d40 60%, #1a2035 100%)",
      display: "flex",
      flexDirection: "column",
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      boxShadow: "4px 0 24px rgba(0,0,0,0.18)",
      position: "sticky",
      top: 0,
      alignSelf: "flex-start",
      overflow: "hidden",
    }}>
      {/* Subtle decorative line */}
      <div style={{
        position: "absolute",
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundImage: "radial-gradient(ellipse at 20% 10%, rgba(99,120,255,0.10) 0%, transparent 60%)",
        pointerEvents: "none",
      }} />

      {/* Logo area */}
      <div style={{
        height: "64px",
        display: "flex",
        alignItems: "center",
        padding: "0 20px",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
      }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
        }}>
            {/*replace by actual logo when we create one*/}
          <div style={{
            width: "28px",
            height: "28px",
            borderRadius: "8px",
            background: "linear-gradient(135deg, #6378ff)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>
          </div>
          <span style={{
            color: "#e8eaf6",
            fontWeight: "700",
            fontSize: "15px",
            letterSpacing: "0.02em",
          }}>Capstone Project</span>
        </div>
      </div>

      {/* Steps label */}
      <div style={{
        padding: "20px 20px 8px",
        fontSize: "10px",
        fontWeight: "700",
        letterSpacing: "0.12em",
        color: "rgba(255,255,255,0.3)",
        textTransform: "uppercase",
      }}>
        Analysis Progress
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: "0 12px", display: "flex", flexDirection: "column", gap: "2px" }}>
        {pipelineSidebarSteps.map((step) => {
          const isActive = step.id === currentStep;
          const isLocked = !isPhaseAccessible(step.phase);
          const isCompleted = !isLocked && step.id < currentStep;
          const labelColor = isLocked
            ? 'rgba(255,255,255,0.24)'
            : isActive
            ? '#c7d0ff'
            : isCompleted
            ? 'rgba(255,255,255,0.6)'
            : 'rgba(255,255,255,0.45)';

          return (
            <button
              key={step.id}
              type="button"
              aria-disabled={isLocked}
              onClick={() => {
                if (!isLocked) {
                  navigate(step.route);
                }
              }}
              style={{
                width: "100%",
                textAlign: "left",
                padding: "9px 12px",
                borderRadius: "8px",
                border: "none",
                cursor: isLocked ? 'not-allowed' : 'pointer',
                display: "flex",
                alignItems: "center",
                gap: "12px",
                transition: "all 0.15s ease",
                background: isActive
                  ? "rgba(99,120,255,0.18)"
                  : isLocked
                  ? 'rgba(255,255,255,0.02)'
                  : "transparent",
                outline: isActive ? "1px solid rgba(99,120,255,0.35)" : "1px solid transparent",
                opacity: isLocked ? 0.7 : 1,
              }}
              onMouseEnter={e => {
                if (!isActive && !isLocked) e.currentTarget.style.background = "rgba(255,255,255,0.05)";
              }}
              onMouseLeave={e => {
                if (!isActive) e.currentTarget.style.background = isLocked ? 'rgba(255,255,255,0.02)' : "transparent";
              }}
            >
              {/* Step indicator */}
              <div style={{
                width: "22px",
                height: "22px",
                borderRadius: "50%",
                flexShrink: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "10px",
                fontWeight: "700",
                transition: "all 0.15s ease",
                background: isLocked
                  ? 'rgba(255,255,255,0.08)'
                  : isCompleted
                  ? "linear-gradient(135deg, #6378ff)"
                  : isActive
                  ? "rgba(99,120,255,0.35)"
                  : "rgba(255,255,255,0.08)",
                color: isLocked ? 'rgba(255,255,255,0.32)' : isCompleted ? "white" : isActive ? "#a5b4fc" : "rgba(255,255,255,0.3)",
                border: isActive && !isCompleted ? "1.5px solid rgba(99,120,255,0.6)" : "1.5px solid transparent",
              }}>
                {isLocked ? (
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="5" y="11" width="14" height="10" rx="2" />
                    <path d="M8 11V8a4 4 0 118 0v3" />
                  </svg>
                ) : isCompleted ? (
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M1.5 5L4 7.5L8.5 2.5" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : step.id}
              </div>

              <span style={{
                fontSize: "13px",
                fontWeight: isActive ? "600" : "400",
                color: labelColor,
                transition: "color 0.15s ease",
              }}>
                {step.label}
              </span>

              {/* Active indicator dot */}
              {isActive && (
                <div style={{
                  marginLeft: "auto",
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  background: "#6378ff",
                  boxShadow: "0 0 6px #6378ff",
                  flexShrink: 0,
                }} />
              )}
            </button>
          );
        })}
      </nav>

      {/* Divider */}
      <div style={{ height: "1px", background: "rgba(255,255,255,0.06)", margin: "0 12px" }} />

      {/* My Analyses button */}
      <div style={{ padding: "12px" }}>
        <button style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          width: "100%",
          padding: "10px 12px",
          borderRadius: "8px",
          border: "none",
          cursor: "pointer",
          background: "transparent",
          transition: "background 0.15s ease",
          color: "rgba(255,255,255,0.5)",
        }}
        onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.05)"}
        onMouseLeave={e => e.currentTarget.style.background = "transparent"}
        onClick={() => setShowLeaveModal(true)}
        >
          <div style={{
            width: "28px",
            height: "28px",
            borderRadius: "50%",
            background: "rgba(255,255,255,0.08)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <svg width="14" height="14" fill="none" stroke="rgba(255,255,255,0.55)" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <span style={{ fontSize: "13px", fontWeight: "500", color: "white" }}>Return to dashboard</span>
        </button>
      </div>

      {showLeaveModal && createPortal(
        <Modal
          title="Leave Analysis?"
          description="Are you sure you want to return to the dashboard? Your current analysis progress will be lost and cannot be recovered."
          confirmLabel="Leave Analysis"
          confirmColor="red"
          onCancel={() => setShowLeaveModal(false)}
          onConfirm={() => {
            setShowLeaveModal(false);
            Maps('/dashboard');
          }}
        />,
        document.body
      )}
    </div>
  );
};

export default Sidebar;

