/**
 * StartupOS AI — Prompt IDE Page
 * 
 * Agent selector, prompt versioning, editor, and activation.
 */

import { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import * as api from '../services/api';
import { colors, spacing, typography, radii } from '../styles/tokens';

const CARD = { background: colors.bgCard, border: `1px solid ${colors.border}`, borderRadius: radii.lg, padding: spacing.lg } as const;

export default function PromptsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [selected, setSelected] = useState<string>('');
  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadAgents(); }, []);

  const loadAgents = async () => {
    try {
      const data = await api.listPromptAgents();
      setAgents(data);
      if (data.length > 0) { setSelected(data[0].key); loadVersions(data[0].key); }
    } catch { }
    setLoading(false);
  };

  const loadVersions = async (agentName: string) => {
    try {
      const data = await api.getPromptVersions(agentName);
      setVersions(data);
    } catch { setVersions([]); }
  };

  const handleSelect = (key: string) => {
    setSelected(key);
    loadVersions(key);
  };

  const handleActivate = async (versionId: string) => {
    await api.activatePromptVersion(selected, versionId).catch(() => {});
    loadVersions(selected);
  };

  if (loading) return <DashboardLayout><div style={{ padding: '4rem', textAlign: 'center', color: colors.textMuted }}>Loading...</div></DashboardLayout>;

  const activeAgent = agents.find(a => a.key === selected);

  return (
    <DashboardLayout>
      <div style={{ padding: '2rem 2.5rem', maxWidth: '1100px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: typography.bold, margin: '0 0 0.3rem' }}>✏️ Prompt IDE</h1>
        <p style={{ color: colors.textMuted, fontSize: typography.sm, margin: `0 0 ${spacing.xl}` }}>Version, test, and manage agent system prompts</p>

        <div style={{ display: 'flex', gap: '1.5rem' }}>
          {/* ── Agent Selector ── */}
          <div style={{ width: '200px', flexShrink: 0 }}>
            <div style={{ fontSize: typography.xs, color: colors.textMuted, textTransform: 'uppercase', marginBottom: spacing.sm, letterSpacing: '0.05em' }}>Agents</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {agents.map(a => (
                <button
                  key={a.key}
                  onClick={() => handleSelect(a.key)}
                  style={{
                    padding: '0.6rem 0.75rem', borderRadius: radii.md, border: 'none',
                    textAlign: 'left', cursor: 'pointer', fontSize: typography.sm,
                    fontWeight: selected === a.key ? typography.semibold : typography.regular,
                    color: selected === a.key ? colors.white : colors.textMuted,
                    background: selected === a.key ? 'rgba(124,58,237,0.15)' : 'transparent',
                    textTransform: 'capitalize',
                  }}
                >
                  {a.name || a.key}
                </button>
              ))}
            </div>
          </div>

          {/* ── Version Timeline + Editor ── */}
          <div style={{ flex: 1 }}>
            {activeAgent && (
              <>
                {/* Agent Meta */}
                <div style={{ ...CARD, marginBottom: spacing.md }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <span style={{ fontSize: '1.1rem', fontWeight: typography.bold, textTransform: 'capitalize', color: colors.white }}>{activeAgent.name || selected}</span>
                      <div style={{ fontSize: typography.xs, color: colors.textMuted, marginTop: '0.2rem' }}>
                        Context keys: {(activeAgent.context_keys || []).join(', ') || 'none'}
                      </div>
                    </div>
                    <span style={{
                      padding: '0.25rem 0.6rem', borderRadius: '1rem', fontSize: '0.7rem',
                      background: 'rgba(6,182,212,0.1)', color: colors.cyan, fontWeight: typography.semibold,
                    }}>
                      {versions.length} version{versions.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                </div>

                {/* Versions */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
                  {versions.map(v => (
                    <div key={v.id} style={{
                      ...CARD,
                      borderColor: v.is_active ? 'rgba(16,185,129,0.4)' : 'rgba(255,255,255,0.07)',
                      background: v.is_active ? 'rgba(16,185,129,0.05)' : 'rgba(255,255,255,0.03)',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: spacing.sm }}>
                        <span style={{ fontSize: typography.sm, fontWeight: typography.semibold, color: colors.white }}>
                          v{v.version}
                        </span>
                        {v.is_active && (
                          <span style={{ padding: '0.15rem 0.5rem', borderRadius: '1rem', fontSize: '0.65rem', fontWeight: typography.bold, background: 'rgba(16,185,129,0.2)', color: colors.emerald }}>
                            ACTIVE
                          </span>
                        )}
                        {v.notes && <span style={{ fontSize: typography.xs, color: colors.textMuted }}>— {v.notes}</span>}
                        <div style={{ marginLeft: 'auto', display: 'flex', gap: spacing.sm }}>
                          {v.score != null && <span style={{ fontSize: '0.7rem', color: colors.amber }}>★ {v.score}</span>}
                          {!v.is_active && (
                            <button onClick={() => handleActivate(v.id)} style={{
                              padding: '0.2rem 0.6rem', background: 'rgba(124,58,237,0.15)',
                              border: '1px solid rgba(124,58,237,0.3)', borderRadius: '0.3rem',
                              color: '#a78bfa', fontSize: '0.7rem', fontWeight: typography.semibold, cursor: 'pointer',
                            }}>
                              Activate
                            </button>
                          )}
                        </div>
                      </div>
                      {/* Prompt Preview */}
                      <pre style={{
                        background: 'rgba(0,0,0,0.3)', borderRadius: radii.md, padding: '0.75rem',
                        fontSize: '0.72rem', color: colors.textMuted, overflow: 'auto', maxHeight: '150px',
                        fontFamily: typography.fontFamilyMono, margin: 0,
                        whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                      }}>
                        {v.system_prompt?.slice(0, 500)}{v.system_prompt?.length > 500 ? '...' : ''}
                      </pre>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
