import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from '../components/sidebar';
import { AnalysisPipelineProvider } from '../context/AnalysisPipelineContext';

export default function PipelineLayout() {
  const navigate = useNavigate();
  
  return (
    <AnalysisPipelineProvider>
      <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f8' }}>
        <Sidebar onDashboard={() => navigate('/dashboard')} />
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Outlet />
        </main>
      </div>
    </AnalysisPipelineProvider>
  );
}
