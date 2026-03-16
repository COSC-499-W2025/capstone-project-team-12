import React, { useState } from 'react';

interface OnboardingProps {
  initialData?: { llmMode: 'online' | 'local'; githubUsername: string; email: string } | null;
  onComplete?: (data: { llmMode: 'online' | 'local'; githubUsername: string; email: string }) => void;
}

const Onboarding: React.FC<OnboardingProps> = ({ initialData, onComplete }) => {
  const [llmMode, setLlmMode] = useState<'online' | 'local'>(initialData?.llmMode ?? 'online');
  const [githubUsername, setGithubUsername] = useState(initialData?.githubUsername ?? '');
  const [email, setEmail] = useState(initialData?.email ?? '');
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [showConsentPopup, setShowConsentPopup] = useState(false);

  const isValid = githubUsername.trim() !== '' && email.trim() !== '';

  const saveUserConfigs = async () => {
    try {
      await fetch('http://localhost:8080/configs/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferences: { llm_mode: llmMode, github_username: githubUsername, github_email: email } }),
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleContinue = async () => {
    if (!isValid) return;
    if (llmMode === 'online') {
      setShowConsentPopup(true);
    } else {
      await saveUserConfigs();
      onComplete?.({ llmMode, githubUsername, email });
    }
  };

  return (
    <div style={{
      flex: 1, minHeight: '100vh',
      background: '#f8f9fc',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      padding: '40px 24px', position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        backgroundImage: `
          radial-gradient(ellipse at 70% 0%, rgba(99,120,255,0.07) 0%, transparent 55%),
          radial-gradient(ellipse at 10% 100%, rgba(167,139,250,0.05) 0%, transparent 50%)
        `,
      }} />

      <div style={{ width: '100%', maxWidth: '440px', position: 'relative' }}>

        {/* Header */}
        {/*later on we check for git file, if yes provide space for git info*/}
        <div style={{ marginBottom: '36px' }}>
          <p style={{ fontSize: '11px', fontWeight: '700', letterSpacing: '0.12em', textTransform: 'uppercase', color: '#6378ff', margin: '0 0 10px' }}>
            
          </p>
          <h1 style={{ fontSize: '26px', fontWeight: '800', color: '#0f1629', margin: '0 0 8px', letterSpacing: '-0.02em', lineHeight: 1.25 }}>
            Let's get you set up
          </h1>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: 0, lineHeight: 1.6 }}>
            Choose your summary generation AI model and provide your github info.
          </p>
        </div>

        {/* LLM Toggle */}
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: '700', letterSpacing: '0.1em', textTransform: 'uppercase', color: '#64748b', marginBottom: '8px' }}>
            Summary Model
          </label>
          <div style={{
            display: 'flex', background: '#eef0f6',
            borderRadius: '10px', padding: '3px',
            border: '1px solid rgba(0,0,0,0.06)',
          }}>
            {([
              { id: 'online' as const, label: 'Online LLM', sub: 'OpenAI GPT-4o-Mini - faster' },
              { id: 'local' as const, label: 'Local LLM', sub: 'Microsoft Phi-3 Mini - Private, slower' },
            ]).map(opt => {
              const active = llmMode === opt.id;
              return (
                <button key={opt.id} onClick={() => setLlmMode(opt.id)} style={{
                  flex: 1, padding: '10px 14px', borderRadius: '8px', border: 'none',
                  cursor: 'pointer', transition: 'all 0.18s ease', fontFamily: 'inherit',
                  background: active ? 'white' : 'transparent',
                  boxShadow: active ? '0 1px 4px rgba(0,0,0,0.1), inset 0 0 0 1px rgba(99,120,255,0.25)' : 'none',
                  display: 'flex', alignItems: 'center', gap: '10px',
                }}>
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontSize: '13px', fontWeight: '600', color: active ? '#1e2433' : '#9ca3af', lineHeight: 1.2 }}>{opt.label}</div>
                    <div style={{ fontSize: '10px', color: active ? '#6378ff' : '#c4c9d4', marginTop: '2px', letterSpacing: '0.02em' }}>{opt.sub}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Divider */}
        <div style={{ height: '1px', background: 'rgba(0,0,0,0.07)', marginBottom: '24px' }} />

        {/* Inputs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
          {[
            { key: 'github', label: 'GitHub Username', placeholder: 'e.g. torvalds', type: 'text', value: githubUsername, onChange: setGithubUsername },
            { key: 'email', label: 'Email Address', placeholder: 'you@example.com', type: 'email', value: email, onChange: setEmail },
          ].map(field => {
            const focused = focusedField === field.key;
            return (
              <div key={field.key}>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: '700', letterSpacing: '0.1em', textTransform: 'uppercase', color: '#64748b', marginBottom: '7px' }}>
                  {field.label}
                </label>
                <div style={{
                  display: 'flex', alignItems: 'center',
                  background: focused ? 'white' : '#f3f4f8',
                  borderRadius: '10px',
                  border: focused ? '1px solid rgba(99,120,255,0.5)' : '1px solid rgba(0,0,0,0.07)',
                  boxShadow: focused ? '0 0 0 3px rgba(99,120,255,0.08)' : 'none',
                  transition: 'all 0.15s ease', overflow: 'hidden',
                }}>
                  <input
                    type={field.type}
                    placeholder={field.placeholder}
                    value={field.value}
                    onChange={e => field.onChange(e.target.value)}
                    onFocus={() => setFocusedField(field.key)}
                    onBlur={() => setFocusedField(null)}
                    style={{
                      flex: 1, border: 'none', outline: 'none', padding: '0 14px',
                      height: '44px', fontSize: '14px', color: '#0f1629',
                      background: 'transparent', fontFamily: 'inherit',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* CTA */}
        <button
          onClick={handleContinue}
          style={{
            width: '100%', padding: '13px', borderRadius: '10px', border: 'none',
            cursor: isValid ? 'pointer' : 'not-allowed',
            background: isValid ? 'linear-gradient(135deg, #6378ff 0%, #a78bfa 100%)' : '#eef0f6',
            color: isValid ? 'white' : '#c4c9d4',
            fontSize: '14px', fontWeight: '700', transition: 'all 0.2s ease',
            boxShadow: isValid ? '0 4px 20px rgba(99,120,255,0.3)' : 'none',
            fontFamily: 'inherit', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
          }}
        >
          Continue
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
          </svg>
        </button>

        <p style={{ textAlign: 'center', fontSize: '11px', color: '#c4c9d4', marginTop: '16px' }}>
        </p>
      </div>

      {/* Online LLM Consent Popup */}
      {showConsentPopup && (
        <div style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            background: 'white', borderRadius: '14px', padding: '28px 32px',
            maxWidth: '380px', width: '90%',
            boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
            fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
          }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0f1629', margin: '0 0 10px' }}>
              Use Online LLM?
            </h2>
            <p style={{ fontSize: '13px', color: '#6b7280', lineHeight: 1.6, margin: '0 0 22px' }}>
              Some of your extracted data will be sent to an external API for summary generation. Do you consent to proceed?
            </p>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => setShowConsentPopup(false)}
                style={{
                  flex: 1, padding: '10px', borderRadius: '8px',
                  border: '1px solid rgba(0,0,0,0.12)', background: '#f3f4f8',
                  color: '#4b5563', fontSize: '13px', fontWeight: '600',
                  cursor: 'pointer', fontFamily: 'inherit',
                }}
              >
                No
              </button>
              <button
                onClick={async () => {
                  setShowConsentPopup(false);
                  await saveUserConfigs();
                  onComplete?.({ llmMode, githubUsername, email });
                }}
                style={{
                  flex: 1, padding: '10px', borderRadius: '8px', border: 'none',
                  background: 'linear-gradient(135deg, #6378ff)',
                  color: 'white', fontSize: '13px', fontWeight: '600',
                  cursor: 'pointer', fontFamily: 'inherit',
                  boxShadow: '0 2px 10px rgba(99,120,255,0.3)',
                }}
              >
                Yes, continue
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`input::placeholder { color: #c4c9d4 !important; }`}</style>
    </div>
  );
};

export default Onboarding;