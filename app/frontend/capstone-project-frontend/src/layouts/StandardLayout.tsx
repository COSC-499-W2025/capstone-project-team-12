import { Outlet } from 'react-router-dom';

export default function StandardLayout() {
  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f8' }}>
      <Outlet />
    </div>
  );
}
