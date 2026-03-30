import { useState } from 'react';
import { createPortal } from 'react-dom';
import { useLocation, useNavigate } from 'react-router-dom';
import { Modal } from './modals';

const Sidebar = ( {onDashboard, isCollapsed = false } : {onDashboard?: () => void; isCollapsed?: boolean; } ) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [showLeaveModal, setShowLeaveModal] = useState(false);

  const getCurrentStepFromPath = (pathname: string): number => {
    if (pathname.includes('/analysis/new/onboarding')) return 1;
    if (pathname.includes('/analysis/new/import') || pathname.includes('/analysis/new/progress')) return 2;
    if (pathname.includes('/analysis/new/finetune')) return 3;
    if (pathname.includes('/analysis/new/insights')) return 4;
    if (pathname.includes('/analysis/new/resume')) return 5;
    if (pathname.includes('/analysis/new/portfolio')) return 6;
    return 1;
  };

  const currentStep = getCurrentStepFromPath(location.pathname);

  const stepToRoute: Record<number, string> = {
    1: '/analysis/new/onboarding',
    2: '/analysis/new/import',
    3: '/analysis/new/finetune',
    4: '/analysis/new/insights',
    5: '/analysis/new/resume',
    6: '/analysis/new/portfolio',
  };
  const steps = [
    { id: 1, label: "Onboarding" },
    { id: 2, label: "File Selection" },
    { id: 3, label: "Finetuning" },
    { id: 4, label: "Skills & Visualizations" },
    { id: 5, label: "Resume Creation" },
    { id: 6, label: "Portfolio Creation" },
  ];

  const W = isCollapsed ? "64px" : "240px";

  return (
    <div style={{
      width: W,
      minWidth: W,
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
      transition: "width 0.25s cubic-bezier(0.4,0,0.2,1), min-width 0.25s cubic-bezier(0.4,0,0.2,1)",
    }}>
      {/* Decorative gradient */}
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
        padding: isCollapsed ? "0" : "0 20px",
        justifyContent: isCollapsed ? "center" : "flex-start",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        flexShrink: 0,
        transition: "padding 0.25s ease, justify-content 0.25s ease",
      }}>
        {/* Logo icon — always visible */}
        <div style={{
          width: "28px",
          height: "28px",
          borderRadius: "8px",
          background: "linear-gradient(135deg, #6378ff 0%, #818cf8 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}>
          {/* Placeholder — swap for actual logo */}
        </div>

        {/* Wordmark — hidden when collapsed */}
        <span style={{
          color: "#e8eaf6",
          fontWeight: "700",
          fontSize: "15px",
          letterSpacing: "0.02em",
          marginLeft: "10px",
          whiteSpace: "nowrap",
          opacity: isCollapsed ? 0 : 1,
          width: isCollapsed ? 0 : "auto",
          overflow: "hidden",
          transition: "opacity 0.2s ease, width 0.25s ease",
          pointerEvents: "none",
        }}>
          Capstone Project
        </span>
      </div>

      {/* "Analysis Progress" label — hidden when collapsed */}
      <div style={{
        padding: isCollapsed ? "20px 0 8px" : "20px 20px 8px",
        fontSize: "10px",
        fontWeight: "700",
        letterSpacing: "0.12em",
        color: "rgba(255,255,255,0.3)",
        textTransform: "uppercase",
        whiteSpace: "nowrap",
        overflow: "hidden",
        textAlign: isCollapsed ? "center" : "left",
        opacity: isCollapsed ? 0 : 1,
        height: isCollapsed ? "0px" : "auto",
        transition: "opacity 0.15s ease, height 0.25s ease",
        pointerEvents: "none",
      }}>
        Analysis Progress
      </div>

      {/* Navigation */}
      <nav style={{
        flex: 1,
        padding: isCollapsed ? "8px 8px" : "0 12px",
        display: "flex",
        flexDirection: "column",
        gap: "2px",
        transition: "padding 0.25s ease",
      }}>
        {steps.map((step) => {
          const isActive = step.id === currentStep;
          const isCompleted = step.id < currentStep;

          return (
            <button
              key={step.id}
              title={isCollapsed ? step.label : undefined}
              onClick={() => navigate(stepToRoute[step.id])}
              style={{
                width: "100%",
                textAlign: "left",
                padding: isCollapsed ? "9px 0" : "9px 12px",
                borderRadius: "8px",
                border: "none",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: isCollapsed ? "center" : "flex-start",
                gap: "12px",
                transition: "all 0.15s ease",
                background: isActive ? "rgba(99,120,255,0.18)" : "transparent",
                outline: isActive ? "1px solid rgba(99,120,255,0.35)" : "1px solid transparent",
              }}
              onMouseEnter={e => {
                if (!isActive) e.currentTarget.style.background = "rgba(255,255,255,0.05)";
              }}
              onMouseLeave={e => {
                if (!isActive) e.currentTarget.style.background = "transparent";
              }}
            >
              {/* Step indicator dot — always visible */}
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
                background: isCompleted
                  ? "linear-gradient(135deg, #6378ff 0%, #818cf8 100%)"
                  : isActive
                  ? "rgba(99,120,255,0.35)"
                  : "rgba(255,255,255,0.08)",
                color: isCompleted ? "white" : isActive ? "#a5b4fc" : "rgba(255,255,255,0.3)",
                border: isActive && !isCompleted ? "1.5px solid rgba(99,120,255,0.6)" : "1.5px solid transparent",
              }}>
                {isCompleted ? (
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M1.5 5L4 7.5L8.5 2.5" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : step.id}
              </div>

              {/* Step label — hidden when collapsed */}
              <span style={{
                fontSize: "13px",
                fontWeight: isActive ? "600" : "400",
                color: isActive
                  ? "#c7d0ff"
                  : isCompleted
                  ? "rgba(255,255,255,0.6)"
                  : "rgba(255,255,255,0.45)",
                transition: "color 0.15s ease, opacity 0.2s ease, width 0.25s ease",
                whiteSpace: "nowrap",
                overflow: "hidden",
                opacity: isCollapsed ? 0 : 1,
                width: isCollapsed ? 0 : "auto",
                pointerEvents: "none",
              }}>
                {step.label}
              </span>

              {/* Active dot — hidden when collapsed (dot indicator is already the circle) */}
              {isActive && !isCollapsed && (
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

      {/* Return to Dashboard button */}
      <div style={{ padding: "12px", display: "flex", justifyContent: isCollapsed ? "center" : "flex-start" }}>
        <button
          title={isCollapsed ? "Return to Dashboard" : undefined}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            width: "100%",
            padding: isCollapsed ? "10px 0" : "10px 12px",
            justifyContent: isCollapsed ? "center" : "flex-start",
            borderRadius: "8px",
            border: "none",
            cursor: "pointer",
            background: "transparent",
            transition: "background 0.15s ease, padding 0.25s ease",
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
            flexShrink: 0,
          }}>
            <svg width="14" height="14" fill="none" stroke="rgba(255,255,255,0.55)" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74" />
            </svg>
          </div>

          <span style={{
            fontSize: "13px",
            fontWeight: "500",
            color: "white",
            whiteSpace: "nowrap",
            overflow: "hidden",
            opacity: isCollapsed ? 0 : 1,
            width: isCollapsed ? 0 : "auto",
            transition: "opacity 0.2s ease, width 0.25s ease",
            pointerEvents: "none",
          }}>
            Return to Dashboard
          </span>
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
            onDashboard?.();
          }}
        />,
        document.body
      )}
    </div>
  );
};

export default Sidebar;