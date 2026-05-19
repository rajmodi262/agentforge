/**
 * StartupOS AI — Shared Report View
 *
 * A public, read-only view of a generated project report via a share token.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import * as api from '../services/api';

const pageStyle: React.CSSProperties = {
  minHeight: '100vh',
  background: '#0f172a',
  color: '#f8fafc',
  fontFamily: '"Inter", sans-serif',
};

const btnPrimary: React.CSSProperties = {
  background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
  border: 'none',
  padding: '0.6rem 1.25rem',
  color: 'white',
  borderRadius: '0.5rem',
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'all 0.2s',
  boxShadow: '0 4px 15px rgba(124, 58, 237, 0.3)',
};

export default function SharedReport() {
  const { shareToken } = useParams<{ shareToken: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<api.SharedProject | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadSharedProject() {
      if (!shareToken) return;
      try {
        const data = await api.getSharedProject(shareToken);
        setProject(data);
      } catch (err: any) {
        setError(err.detail || 'Failed to load shared report');
      } finally {
        setLoading(false);
      }
    }
    loadSharedProject();
  }, [shareToken]);

  if (loading) {
    return (
      <div style={pageStyle}>
        <div style={{ textAlign: 'center', padding: '6rem 2rem' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⏳</div>
          <div style={{ color: '#64748b' }}>Loading shared report...</div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div style={pageStyle}>
        <div style={{ textAlign: 'center', padding: '6rem 2rem' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🔒</div>
          <div style={{ color: '#fca5a5', marginBottom: '1rem' }}>{error || 'Report not found'}</div>
          <div style={{ color: '#64748b', fontSize: '0.9rem' }}>This link may be invalid or expired.</div>
        </div>
      </div>
    );
  }

  return (
    <div style={pageStyle}>
      {/* Header */}
      <header style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '1.25rem 2rem',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        background: 'rgba(0,0,0,0.3)',
        backdropFilter: 'blur(10px)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div onClick={() => navigate('/')} style={{
            fontSize: '1.3rem', fontWeight: 800, cursor: 'pointer',
            background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>StartupOS</div>
          <span style={{ color: '#475569', fontSize: '0.8rem', paddingLeft: '0.5rem', borderLeft: '1px solid #334155' }}>
            Shared Report
          </span>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button onClick={() => navigate('/login')} style={{
            background: 'transparent', border: '1px solid #475569', color: '#cbd5e1',
            padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer',
            fontSize: '0.9rem'
          }}>Sign In / Sign Up</button>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '800px', margin: '4rem auto', padding: '0 2rem', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '1rem', color: '#f8fafc' }}>
          {project.title}
        </h1>
        
        <div style={{ 
          background: 'rgba(255,255,255,0.03)', 
          border: '1px solid rgba(255,255,255,0.1)', 
          padding: '2rem', 
          borderRadius: '1rem',
          marginBottom: '2rem',
          textAlign: 'left'
        }}>
          <h3 style={{ color: '#a78bfa', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem', marginTop: 0 }}>The Idea</h3>
          <p style={{ color: '#cbd5e1', fontSize: '1.1rem', lineHeight: 1.6, margin: '0 0 1.5rem 0' }}>
            {project.business_idea}
          </p>

          <div style={{ display: 'flex', gap: '2rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1.5rem' }}>
            <div>
              <div style={{ color: '#64748b', fontSize: '0.8rem', textTransform: 'uppercase' }}>Target Market</div>
              <div style={{ color: '#f1f5f9' }}>{project.target_market || 'Unspecified'}</div>
            </div>
            <div>
              <div style={{ color: '#64748b', fontSize: '0.8rem', textTransform: 'uppercase' }}>Budget Range</div>
              <div style={{ color: '#f1f5f9' }}>{project.budget_range || 'Unspecified'}</div>
            </div>
          </div>
        </div>

        {project.status === 'completed' && project.has_report ? (
          <div style={{ marginTop: '3rem' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>The Blueprint is Ready</h2>
            <p style={{ color: '#94a3b8', marginBottom: '2rem', maxWidth: '600px', margin: '0 auto 2rem' }}>
              A full multi-agent analysis has been completed for this idea, including market research, technical architecture, and financial projections.
            </p>
            <a 
              href={api.getSharedReportDownloadUrl(shareToken!)} 
              style={{...btnPrimary, display: 'inline-flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none', fontSize: '1.1rem', padding: '1rem 2rem'}}
            >
              <span style={{ fontSize: '1.3rem' }}>📄</span> Download Full PDF Blueprint
            </a>
          </div>
        ) : (
          <div style={{ 
            marginTop: '3rem', 
            padding: '2rem', 
            background: 'rgba(245, 158, 11, 0.05)', 
            border: '1px solid rgba(245, 158, 11, 0.2)',
            borderRadius: '1rem',
            color: '#fbbf24' 
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🚧</div>
            <h3 style={{ margin: '0 0 0.5rem 0' }}>Analysis in Progress</h3>
            <p style={{ margin: 0, opacity: 0.8 }}>The AI agents are currently generating the blueprint for this idea. Check back later.</p>
          </div>
        )}
        
        <div style={{ marginTop: '5rem', paddingTop: '2rem', borderTop: '1px solid rgba(255,255,255,0.1)', color: '#64748b', fontSize: '0.9rem' }}>
          Generated by <strong style={{ color: '#a78bfa' }}>StartupOS AI</strong> — The multi-agent startup accelerator.
        </div>
      </main>
    </div>
  );
}
