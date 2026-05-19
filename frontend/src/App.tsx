import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import Lenis from 'lenis';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { AuthProvider } from './hooks/useAuth';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Report from './pages/Report';
import ObservabilityPage from './pages/ObservabilityPage';
import KnowledgePage from './pages/KnowledgePage';
import PromptsPage from './pages/PromptsPage';
import AdminPage from './pages/AdminPage';
import SharedReport from './pages/SharedReport';

gsap.registerPlugin(ScrollTrigger);

/** Only enable Lenis smooth scroll on the landing page (scrollytelling) */
function LenisProvider({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isLanding = location.pathname === '/';

  useEffect(() => {
    if (!isLanding) return;

    const lenis = new Lenis({
      lerp: 0.1,
      smoothWheel: true,
    });

    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((time) => { lenis.raf(time * 1000); });
    gsap.ticker.lagSmoothing(0);

    return () => { lenis.destroy(); };
  }, [isLanding]);

  return <>{children}</>;
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <LenisProvider>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/shared/:shareToken" element={<SharedReport />} />
              <Route path="/login" element={<Login />} />
              <Route path="/dashboard" element={
                <ProtectedRoute><Dashboard /></ProtectedRoute>
              } />
              <Route path="/report/:projectId" element={
                <ProtectedRoute><Report /></ProtectedRoute>
              } />
              <Route path="/observability" element={
                <ProtectedRoute><ObservabilityPage /></ProtectedRoute>
              } />
              <Route path="/knowledge" element={
                <ProtectedRoute><KnowledgePage /></ProtectedRoute>
              } />
              <Route path="/prompts" element={
                <ProtectedRoute><PromptsPage /></ProtectedRoute>
              } />
              <Route path="/admin" element={
                <ProtectedRoute><AdminPage /></ProtectedRoute>
              } />
            </Routes>
          </LenisProvider>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}

