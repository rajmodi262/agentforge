/**
 * AgentForge AI — Report Page (A+ Edition)
 *
 * Fetches and displays actual agent outputs in a beautiful card layout.
 * Supports collapsible sections, PDF download, and live status polling.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import * as api from '../services/api';
import { useWorkflowSocket } from '../hooks/useWorkflowSocket';
import ThoughtStream from '../components/ThoughtStream';

const AGENT_META: Record<string, { icon: string; color: string }> = {
  ceo_output: { icon: '👔', color: '#7c3aed' },
  research_output: { icon: '🔍', color: '#06b6d4' },
  marketing_output: { icon: '📣', color: '#f59e0b' },
  developer_output: { icon: '💻', color: '#10b981' },
  finance_output: { icon: '💰', color: '#ef4444' },
  analytics_output: { icon: '📊', color: '#8b5cf6' },
  operations_output: { icon: '⚙️', color: '#f97316' },
};

const AGENT_ORDER = [
  'ceo_output', 'research_output', 'marketing_output',
  'developer_output', 'finance_output', 'analytics_output', 'operations_output',
];

export default function Report() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<api.Project | null>(null);
  const [results, setResults] = useState<api.ProjectResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  
  const workflow = useWorkflowSocket();

  useEffect(() => {
    if (!projectId) return;
    loadData();
  }, [projectId]);

  useEffect(() => {
    if (results?.status === 'running' && results.workflow_id && workflow.status === 'idle') {
      workflow.connect(results.workflow_id);
    }
  }, [results, workflow]);

  // If workflow completes, reload data
  useEffect(() => {
    if (workflow.status === 'completed') {
      loadData();
      workflow.disconnect();
    }
  }, [workflow.status]);

  const loadData = async () => {
    try {
      const [proj, res] = await Promise.all([
        api.getProject(projectId!),
        api.getProjectResults(projectId!),
      ]);
      setProject(proj);
      setResults(res);

      // Auto-expand the first agent
      const agents = Object.keys(res.agents);
      if (agents.length > 0) {
        setExpanded({ [agents[0]]: true });
      }
    } catch (err: any) {
      if (err?.status === 401) {
        navigate('/login');
        return;
      }
      setError(err?.detail || 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (key: string) => {
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const expandAll = () => {
    if (!results) return;
    const all: Record<string, boolean> = {};
    Object.keys(results.agents).forEach(k => all[k] = true);
    setExpanded(all);
  };

  const collapseAll = () => setExpanded({});

  const renderValue = (value: any, depth = 0): React.ReactNode => {
    if (value === null || value === undefined) return <span style={{ color: '#475569' }}>—</span>;
    if (typeof value === 'boolean') return <span style={{ color: '#7c3aed', fontWeight: 600 }}>{value ? '✓ Yes' : '✗ No'}</span>;
    if (typeof value === 'number') return <span style={{ color: '#7c3aed', fontWeight: 600 }}>{value.toLocaleString()}</span>;
    if (typeof value === 'string') {
      // Multi-line strings
      if (value.includes('\n')) {
        return <pre style={{ whiteSpace: 'pre-wrap', color: '#cbd5e1', margin: 0, fontFamily: 'inherit', fontSize: '0.85rem', lineHeight: 1.6 }}>{value}</pre>;
      }
      return <span style={{ color: '#cbd5e1' }}>{value}</span>;
    }

    if (Array.isArray(value)) {
      if (value.length === 0) return <span style={{ color: '#475569' }}>Empty list</span>;
      // Array of strings → bullet list
      if (value.every(v => typeof v === 'string')) {
        return (
          <ul style={{ margin: '0.25rem 0', paddingLeft: '1.25rem', listStyle: 'none' }}>
            {value.map((item, i) => (
              <li key={i} style={{ color: '#cbd5e1', fontSize: '0.85rem', padding: '0.2rem 0', position: 'relative' }}>
                <span style={{ color: '#7c3aed', marginRight: '0.5rem' }}>▸</span>{item}
              </li>
            ))}
          </ul>
        );
      }
      // Array of objects
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.25rem' }}>
          {value.map((item, i) => (
            <div key={i} style={{
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: '0.5rem',
              padding: '0.75rem',
            }}>
              {renderValue(item, depth + 1)}
            </div>
          ))}
        </div>
      );
    }

    if (typeof value === 'object') {
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: depth > 0 ? '0' : '0.25rem' }}>
          {Object.entries(value).map(([key, val]) => (
            <div key={key} style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
              <span style={{
                color: '#94a3b8',
                fontSize: '0.75rem',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}>
                {key.replace(/_/g, ' ')}
              </span>
              <div style={{ paddingLeft: depth < 2 ? '0.5rem' : '0' }}>
                {renderValue(val, depth + 1)}
              </div>
            </div>
          ))}
        </div>
      );
    }

    return <span>{String(value)}</span>;
  };

  const [isSharing, setIsSharing] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  const handleShare = async () => {
    if (!projectId) return;
    try {
      setIsSharing(true);
      const res = await api.shareProject(projectId);
      const fullUrl = `${window.location.origin}${res.share_url}`;
      setShareUrl(fullUrl);
      await navigator.clipboard.writeText(fullUrl);
      alert('Share link copied to clipboard!');
    } catch (err) {
      alert('Failed to generate share link');
    } finally {
      setIsSharing(false);
    }
  };

  if (loading) {
    return (
      <div style={pageStyle}>
        <div style={{ textAlign: 'center', padding: '6rem 2rem' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⏳</div>
          <div style={{ color: '#64748b' }}>Loading report...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={pageStyle}>
        <div style={{ textAlign: 'center', padding: '6rem 2rem' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>❌</div>
          <div style={{ color: '#fca5a5', marginBottom: '1rem' }}>{error}</div>
          <button onClick={() => navigate('/dashboard')} style={btnGhost}>← Back to Dashboard</button>
        </div>
      </div>
    );
  }

  const hasAgents = results && Object.keys(results.agents).length > 0;
  const sortedAgentKeys = hasAgents
    ? AGENT_ORDER.filter(k => k in results!.agents)
    : [];

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
          }}>AgentForge</div>
          <span style={{ color: '#475569', fontSize: '0.8rem' }}>/ <span style={{ cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>Dashboard</span> / Report</span>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          {results?.status === 'completed' && (
            <>
              <button 
                onClick={handleShare} 
                disabled={isSharing}
                style={{
                  ...btnGhost,
                  border: '1px solid rgba(124, 58, 237, 0.4)',
                  color: '#a78bfa',
                }}
              >
                {isSharing ? 'Generating...' : shareUrl ? '✓ Copied' : '🔗 Share'}
              </button>
              <a href={api.getReportDownloadUrl(projectId!)} style={{
                ...btnPrimary,
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.3rem',
              }}>📄 Download PDF</a>
            </>
          )}
          <button onClick={() => navigate('/dashboard')} style={btnGhost}>← Dashboard</button>
        </div>
      </header>

      {/* Report Content */}
      <main style={{ maxWidth: '900px', margin: '0 auto', padding: '2rem' }}>
        {/* Project Header */}
        <div style={{ marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, margin: '0 0 0.5rem 0', color: '#f1f5f9' }}>
            {project?.title || 'Startup Blueprint'}
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem', margin: '0 0 1rem 0' }}>
            {project?.business_idea}
          </p>

          {/* Stats Bar */}
          {results?.status === 'completed' && (
            <div style={{
              display: 'flex', gap: '1.5rem', padding: '1rem',
              background: 'rgba(124, 58, 237, 0.05)',
              border: '1px solid rgba(124, 58, 237, 0.15)',
              borderRadius: '0.75rem',
            }}>
              <StatBadge label="Agents" value={`${Object.keys(results.agents).length}/7`} />
              <StatBadge label="Tokens" value={(results.total_tokens || 0).toLocaleString()} />
              <StatBadge label="Cost" value={`$${(results.total_cost || 0).toFixed(4)}`} />
              <StatBadge label="Status" value="✓ Complete" color="#10b981" />
            </div>
          )}

          {results?.status === 'running' && (
            <div style={{ marginTop: '1.5rem' }}>
              <ThoughtStream events={workflow.events} />
            </div>
          )}
        </div>

        {/* Controls */}
        {hasAgents && (
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
            <button onClick={expandAll} style={btnGhost}>Expand All</button>
            <button onClick={collapseAll} style={btnGhost}>Collapse All</button>
          </div>
        )}

        {/* Agent Sections */}
        {!hasAgents ? (
          <div style={{
            textAlign: 'center', padding: '4rem 2rem',
            background: 'rgba(255,255,255,0.02)',
            border: '1px dashed rgba(255,255,255,0.1)',
            borderRadius: '1rem',
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
            <h3 style={{ color: '#e2e8f0', fontWeight: 600, margin: '0 0 0.5rem 0' }}>
              No results yet
            </h3>
            <p style={{ color: '#64748b', fontSize: '0.9rem', margin: '0 0 1.5rem 0' }}>
              {results?.status === 'no_workflow'
                ? 'Run the blueprint generator from the dashboard to see results here.'
                : 'The workflow is still processing...'}
            </p>
            <button onClick={() => navigate('/dashboard')} style={btnPrimary}>
              Go to Dashboard
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {sortedAgentKeys.map((key, i) => {
              const agent = results!.agents[key];
              const meta = AGENT_META[key] || { icon: '🤖', color: '#64748b' };
              const isOpen = expanded[key] || false;

              return (
                <div key={key} style={{
                  background: 'rgba(255,255,255,0.03)',
                  border: `1px solid ${isOpen ? meta.color + '40' : 'rgba(255,255,255,0.07)'}`,
                  borderRadius: '1rem',
                  overflow: 'hidden',
                  transition: 'border-color 0.2s',
                }}>
                  {/* Section Header */}
                  <button
                    onClick={() => toggleSection(key)}
                    style={{
                      width: '100%', display: 'flex', alignItems: 'center',
                      padding: '1rem 1.25rem', background: 'none', border: 'none',
                      cursor: 'pointer', gap: '0.75rem', textAlign: 'left',
                    }}
                  >
                    <span style={{ fontSize: '1.3rem' }}>{meta.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ color: '#e2e8f0', fontWeight: 600, fontSize: '0.95rem' }}>
                        {agent.name}
                      </div>
                      <div style={{ color: '#475569', fontSize: '0.75rem', marginTop: '0.1rem' }}>
                        {agent.status === 'completed' ? `${agent.tokens_used?.toLocaleString()} tokens · ${agent.execution_time?.toFixed(1)}s` : agent.status}
                      </div>
                    </div>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                      width: '1.5rem', height: '1.5rem', borderRadius: '50%',
                      background: agent.status === 'completed' ? `${meta.color}20` : 'rgba(239,68,68,0.1)',
                      color: agent.status === 'completed' ? meta.color : '#ef4444',
                      fontSize: '0.7rem', fontWeight: 700,
                    }}>
                      {agent.status === 'completed' ? `${i + 1}` : '!'}
                    </span>
                    <span style={{
                      color: '#475569', fontSize: '0.9rem',
                      transform: isOpen ? 'rotate(180deg)' : 'rotate(0)',
                      transition: 'transform 0.2s',
                    }}>▼</span>
                  </button>

                  {/* Section Body */}
                  {isOpen && agent.output && (
                    <div style={{
                      padding: '0 1.25rem 1.25rem 1.25rem',
                      borderTop: '1px solid rgba(255,255,255,0.05)',
                    }}>
                      <div style={{ paddingTop: '1rem' }}>
                        {renderValue(agent.output)}
                      </div>
                    </div>
                  )}

                  {isOpen && agent.status === 'failed' && (
                    <div style={{
                      padding: '1rem 1.25rem',
                      borderTop: '1px solid rgba(239,68,68,0.2)',
                      color: '#fca5a5', fontSize: '0.85rem',
                    }}>
                      ⚠️ This agent encountered an error. Other agents continued with available data.
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}

function StatBadge({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
      <span style={{ color: '#475569', fontSize: '0.7rem', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.05em' }}>{label}</span>
      <span style={{ color: color || '#e2e8f0', fontSize: '0.9rem', fontWeight: 600 }}>{value}</span>
    </div>
  );
}

const pageStyle: React.CSSProperties = {
  minHeight: '100vh',
  background: 'linear-gradient(135deg, #0a0a0f 0%, #12121f 50%, #0a0a0f 100%)',
  fontFamily: "'Inter', system-ui, sans-serif",
  color: '#f1f5f9',
};

const btnPrimary: React.CSSProperties = {
  padding: '0.6rem 1.2rem',
  background: 'linear-gradient(135deg, #7c3aed, #6d28d9)',
  color: '#fff', border: 'none', borderRadius: '0.6rem',
  fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer',
};

const btnGhost: React.CSSProperties = {
  padding: '0.4rem 0.8rem',
  background: 'rgba(255,255,255,0.05)',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '0.4rem', color: '#94a3b8',
  fontSize: '0.8rem', cursor: 'pointer',
};
