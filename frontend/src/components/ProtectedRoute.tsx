/**
 * StartupOS AI — Protected Route
 *
 * Redirects to /login if user is not authenticated.
 * Shows loading skeleton while checking auth state.
 */

import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0a0f 0%, #12121f 50%, #0a0a0f 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: "'Inter', system-ui, sans-serif",
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '2.5rem', height: '2.5rem', borderRadius: '50%',
            border: '3px solid rgba(124, 58, 237, 0.2)',
            borderTopColor: '#7c3aed',
            animation: 'spin 0.8s linear infinite',
            margin: '0 auto 1rem',
          }} />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <div style={{ color: '#64748b', fontSize: '0.9rem' }}>Loading...</div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
