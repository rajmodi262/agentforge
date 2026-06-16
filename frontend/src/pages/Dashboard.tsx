/**
 * AgentForge AI — Dashboard Page
 *
 * Shows user's projects, workflow status, and report downloads.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import DashboardLayout from '../components/DashboardLayout';
import * as api from '../services/api';

import { colors, spacing, typography, gradients, radii } from '../styles/tokens';

const STATUS_COLORS: Record<string, string> = {
  draft: colors.textMuted,
  running: colors.amber,
  completed: colors.emerald,
  error: colors.error,
  failed: colors.error,
};

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft',
  running: '⏳ Running...',
  completed: '✓ Completed',
  error: '✗ Error',
  failed: '✗ Failed',
};

import DashboardCharts from '../components/DashboardCharts';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [projects, setProjects] = useState<api.Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await api.listProjects();
      setProjects(data.projects);
    } catch (err: any) {
      if (err?.status === 401) {
        navigate('/login');
        return;
      }
      setError(err?.detail || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <DashboardLayout>
      {/* Content */}
      <div style={{ maxWidth: '900px', padding: `${spacing.xl} ${spacing.lg}` }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.xl }}>
          <div>
            <h1 style={{ fontSize: '1.8rem', fontWeight: typography.bold, margin: 0 }}>
              Your Projects
            </h1>
            <p style={{ color: colors.textMuted, fontSize: typography.sm, margin: '0.3rem 0 0 0' }}>
              {projects.length} blueprint{projects.length !== 1 ? 's' : ''} created
            </p>
          </div>
          <button
            onClick={() => navigate('/')}
            style={{
              padding: '0.7rem 1.4rem',
              background: gradients.hero,
              color: colors.white,
              border: 'none',
              borderRadius: radii.md,
              fontSize: typography.sm,
              fontWeight: typography.semibold,
              cursor: 'pointer',
            }}
          >
            + New Blueprint
          </button>
        </div>

        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: `1px solid rgba(239, 68, 68, 0.3)`,
            borderRadius: radii.md,
            padding: spacing.lg,
            marginBottom: spacing.lg,
            color: colors.error,
          }}>
            {error}
          </div>
        )}

        {/* Charts Section */}
        {!loading && projects.length > 0 && (
          <DashboardCharts projects={projects} />
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem', color: colors.textMuted }}>
            Loading projects...
          </div>
        ) : projects.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '5rem 2rem',
            background: 'rgba(255,255,255,0.02)',
            border: `1px dashed ${colors.border}`,
            borderRadius: radii.lg,
          }}>
            <div style={{ fontSize: '3rem', marginBottom: spacing.md }}>🚀</div>
            <h3 style={{ color: colors.white, fontWeight: typography.semibold, margin: '0 0 0.5rem 0' }}>
              No blueprints yet
            </h3>
            <p style={{ color: colors.textMuted, fontSize: typography.sm, margin: `0 0 ${spacing.lg} 0` }}>
              Head to the homepage and enter your startup idea to generate your first AI-powered blueprint.
            </p>
            <button
              onClick={() => navigate('/')}
              style={{
                padding: '0.7rem 1.5rem',
                background: gradients.hero,
                color: colors.white,
                border: 'none',
                borderRadius: radii.md,
                fontSize: typography.sm,
                fontWeight: typography.semibold,
                cursor: 'pointer',
              }}
            >
              Create Your First Blueprint →
            </button>
          </div>
        ) : (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', 
            gap: spacing.lg 
          }}>
            {projects.map(project => (
              <div
                key={project.id}
                style={{
                  background: 'rgba(30, 41, 59, 0.4)',
                  border: `1px solid rgba(255,255,255,0.05)`,
                  borderRadius: '1.5rem',
                  padding: spacing.xl,
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: project.status === 'completed' ? 'pointer' : 'default',
                  position: 'relative',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: spacing.md,
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                }}
                onMouseEnter={(e) => {
                  if (project.status === 'completed') {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1)';
                    e.currentTarget.style.borderColor = 'rgba(124, 58, 237, 0.3)';
                    e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (project.status === 'completed') {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)';
                    e.currentTarget.style.background = 'rgba(30, 41, 59, 0.4)';
                  }
                }}
                onClick={() => {
                  if (project.status === 'completed') {
                    navigate(`/report/${project.id}`);
                  }
                }}
              >
                {/* Top decorative gradient */}
                <div style={{
                  position: 'absolute', top: 0, left: 0, right: 0, height: '3px',
                  background: project.status === 'completed' 
                    ? `linear-gradient(90deg, transparent, ${STATUS_COLORS.completed}, transparent)`
                    : `linear-gradient(90deg, transparent, ${STATUS_COLORS[project.status] || colors.border}, transparent)`,
                  opacity: 0.7
                }} />

                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: typography.bold, margin: 0, color: colors.white, lineHeight: 1.3 }}>
                    {project.title}
                  </h3>
                  <span style={{
                    padding: '0.25rem 0.75rem',
                    borderRadius: '2rem',
                    fontSize: '0.7rem',
                    fontWeight: typography.bold,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    background: `${STATUS_COLORS[project.status] || colors.textMuted}15`,
                    color: STATUS_COLORS[project.status] || colors.textMuted,
                    border: `1px solid ${STATUS_COLORS[project.status] || colors.textMuted}30`,
                    whiteSpace: 'nowrap'
                  }}>
                    {STATUS_LABELS[project.status] || project.status}
                  </span>
                </div>

                <p style={{
                  color: colors.textMuted,
                  fontSize: typography.sm,
                  margin: 0,
                  lineHeight: 1.6,
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  flex: 1
                }}>
                  {project.business_idea}
                </p>

                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  marginTop: 'auto',
                  paddingTop: spacing.md,
                  borderTop: '1px solid rgba(255,255,255,0.05)'
                }}>
                  <div style={{ color: '#64748b', fontSize: '0.75rem' }}>
                    {new Date(project.created_at).toLocaleDateString()}
                  </div>
                  
                  {project.status === 'completed' && (
                    <a
                      href={api.getReportDownloadUrl(project.id)}
                      onClick={e => e.stopPropagation()}
                      style={{
                        padding: '0.4rem 0.8rem',
                        borderRadius: radii.md,
                        fontSize: typography.xs,
                        fontWeight: typography.bold,
                        background: 'rgba(16, 185, 129, 0.1)',
                        color: colors.emerald,
                        border: '1px solid rgba(16, 185, 129, 0.2)',
                        textDecoration: 'none',
                        transition: 'all 0.2s',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(16, 185, 129, 0.2)';
                        e.currentTarget.style.transform = 'scale(1.05)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'rgba(16, 185, 129, 0.1)';
                        e.currentTarget.style.transform = 'scale(1)';
                      }}
                    >
                      ↓ PDF
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

const smallBtnStyle: React.CSSProperties = {
  padding: '0.4rem 0.8rem',
  background: 'rgba(255,255,255,0.05)',
  border: `1px solid ${colors.border}`,
  borderRadius: radii.sm,
  color: colors.textMuted,
  fontSize: typography.sm,
  cursor: 'pointer',
};
