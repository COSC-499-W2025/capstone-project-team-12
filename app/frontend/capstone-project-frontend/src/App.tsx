import { useState } from 'react';
import ResumeDisplay from './pages/resume_display';

function App() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <ResumeDisplay />
      </main>
    </div>
  );
}

export default App;