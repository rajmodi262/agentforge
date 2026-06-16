/**
 * AgentForge AI — Admin Panel Page
 * 
 * System stats, user RBAC management, audit log viewer.
 */

import { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import * as api from '../services/api';
import { colors, typography, spacing, radii } from '../styles/tokens';

const CARD = { background: colors.bgCard, border: `1px solid ${colors.border}`, borderRadius: radii.lg, padding: spacing.lg } as const;

const ROLES = ['viewer', 'editor', 'admin', 'owner'];
const ROLE_COLORS: Record<string, string> = { owner: colors.amber, admin: colors.error, editor: colors.cyan, viewer: colors.textMuted };

export default function AdminPage() {
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [auditTotal, setAuditTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'overview' | 'users' | 'audit'>('overview');

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    try {
      const [s, u, a] = await Promise.all([
        api.getSystemStats().catch(() => null),
        api.listUsers().catch(() => []),
        api.getAuditLogs({ limit: 30 }).catch(() => ({ total: 0, logs: [] })),
      ]);
      setStats(s);
      setUsers(u);
      setAuditLogs(a.logs);
      setAuditTotal(a.total);
    } finally { setLoading(false); }
  };

  const handleRoleChange = async (userId: string, role: string) => {
    await api.updateUserRole(userId, role).catch(() => {});
    setUsers(prev => prev.map(u => u.id === userId ? { ...u, role } : u));
  };

  if (loading) return <DashboardLayout><div style={{ padding: '4rem', textAlign: 'center', color: colors.textMuted }}>Loading admin panel...</div></DashboardLayout>;

  return (
    <DashboardLayout>
      <div style={{ padding: '2rem 2.5rem', maxWidth: '1100px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: typography.bold, margin: '0 0 0.3rem' }}>⚙️ Admin</h1>
        <p style={{ color: colors.textMuted, fontSize: typography.sm, margin: '0 0 1.5rem' }}>System management, RBAC, and audit trail</p>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: spacing.sm, marginBottom: spacing.xl }}>
          {(['overview', 'users', 'audit'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                padding: '0.5rem 1rem', borderRadius: radii.md, border: 'none', fontSize: typography.sm, fontWeight: typography.semibold, cursor: 'pointer',
                color: tab === t ? colors.white : colors.textMuted, textTransform: 'capitalize',
                background: tab === t ? colors.primaryGlow : 'transparent',
              }}
            >{t}</button>
          ))}
        </div>

        {/* ── Overview Tab ── */}
        {tab === 'overview' && stats && (
          <div>
            <div style={{ display: 'flex', gap: spacing.md, flexWrap: 'wrap', marginBottom: spacing.xl }}>
              {[
                { label: 'Users', value: stats.total_users, color: colors.primary },
                { label: 'Projects', value: stats.total_projects, color: colors.cyan },
                { label: 'Workflows', value: stats.total_workflows, color: colors.emerald },
                { label: 'Total Tokens', value: (stats.total_tokens || 0).toLocaleString(), color: colors.amber },
                { label: 'Total Cost', value: `$${(stats.total_cost || 0).toFixed(2)}`, color: colors.error },
              ].map(c => (
                <div key={c.label} style={{ ...CARD, flex: 1, minWidth: '150px', textAlign: 'center' }}>
                  <div style={{ color: colors.textMuted, fontSize: typography.xs, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{c.label}</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: typography.bold, color: c.color, marginTop: '0.3rem' }}>{c.value}</div>
                </div>
              ))}
            </div>

            {/* Quick Info */}
            <div style={{ ...CARD }}>
              <h3 style={{ fontSize: typography.sm, fontWeight: typography.semibold, margin: '0 0 0.75rem' }}>System Info</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.sm, fontSize: typography.sm }}>
                {[
                  ['Mock Mode', stats.mock_mode ? '✅ On' : '❌ Off'],
                  ['AI Provider', stats.ai_provider || 'auto'],
                  ['Orchestration', 'LangGraph'],
                  ['RAG Pipeline', stats.rag_status || 'Active'],
                  ['n8n Integration', stats.n8n_enabled ? '✅ Connected' : '⚠️ Not configured'],
                  ['Audit Logs', `${auditTotal} entries`],
                ].map(([k, v]) => (
                  <div key={k as string} style={{ padding: '0.5rem', borderRadius: radii.sm, background: 'rgba(255,255,255,0.02)', display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: colors.textMuted }}>{k}</span>
                    <span style={{ color: colors.white, fontWeight: typography.medium }}>{v}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── Users Tab ── */}
        {tab === 'users' && (
          <div style={{ ...CARD, padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: typography.sm }}>
              <thead>
                <tr style={{ borderBottom: `1px solid ${colors.border}` }}>
                  {['Email', 'Name', 'Role', 'Joined', 'Actions'].map(h => (
                    <th key={h} style={{ padding: '0.75rem', textAlign: 'left', color: colors.textMuted, fontWeight: typography.medium, fontSize: typography.xs, textTransform: 'uppercase' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} style={{ borderBottom: `1px solid ${colors.borderHover}` }}>
                    <td style={{ padding: '0.6rem 0.75rem', color: colors.white }}>{u.email}</td>
                    <td style={{ padding: '0.6rem 0.75rem', color: colors.textMuted }}>{u.name || '—'}</td>
                    <td style={{ padding: '0.6rem 0.75rem' }}>
                      <span style={{
                        padding: '0.15rem 0.5rem', borderRadius: '1rem', fontSize: '0.7rem', fontWeight: typography.semibold,
                        background: `${ROLE_COLORS[u.role] || colors.textMuted}20`,
                        color: ROLE_COLORS[u.role] || colors.textMuted,
                      }}>{u.role}</span>
                    </td>
                    <td style={{ padding: '0.6rem 0.75rem', color: colors.textMuted }}>{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
                    <td style={{ padding: '0.6rem 0.75rem' }}>
                      <select
                        value={u.role}
                        onChange={e => handleRoleChange(u.id, e.target.value)}
                        style={{
                          padding: '0.25rem 0.4rem', background: 'rgba(255,255,255,0.05)',
                          border: `1px solid ${colors.border}`, borderRadius: '0.3rem',
                          color: colors.white, fontSize: typography.xs,
                        }}
                      >
                        {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ── Audit Tab ── */}
        {tab === 'audit' && (
          <div>
            <div style={{ fontSize: typography.sm, color: colors.textMuted, marginBottom: '0.75rem' }}>
              {auditTotal} audit entries recorded
            </div>
            <div style={{ ...CARD, padding: 0, overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: typography.sm }}>
                <thead>
                  <tr style={{ borderBottom: `1px solid ${colors.border}` }}>
                    {['Time', 'Action', 'Path', 'User', 'Status'].map(h => (
                      <th key={h} style={{ padding: '0.75rem', textAlign: 'left', color: colors.textMuted, fontWeight: typography.medium, fontSize: typography.xs, textTransform: 'uppercase' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.length === 0 ? (
                    <tr><td colSpan={5} style={{ padding: spacing.xl, textAlign: 'center', color: colors.textMuted }}>No audit logs yet.</td></tr>
                  ) : auditLogs.map((log, i) => (
                    <tr key={i} style={{ borderBottom: `1px solid ${colors.borderHover}` }}>
                      <td style={{ padding: '0.6rem 0.75rem', color: colors.textMuted, fontSize: typography.xs }}>
                        {log.timestamp ? new Date(log.timestamp).toLocaleString() : '—'}
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>
                        <span style={{
                          padding: '0.15rem 0.4rem', borderRadius: '0.25rem', fontSize: '0.7rem', fontWeight: typography.semibold,
                          background: log.method === 'POST' ? 'rgba(16,185,129,0.15)' : log.method === 'DELETE' ? 'rgba(239,68,68,0.15)' : 'rgba(245,158,11,0.15)',
                          color: log.method === 'POST' ? colors.emerald : log.method === 'DELETE' ? colors.error : colors.amber,
                        }}>{log.method}</span>
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem', color: colors.textMuted, fontFamily: typography.fontFamilyMono, fontSize: typography.xs }}>{log.path}</td>
                      <td style={{ padding: '0.6rem 0.75rem', color: colors.textMuted }}>{log.user_id || 'anonymous'}</td>
                      <td style={{ padding: '0.6rem 0.75rem', color: (log.status_code || 200) < 400 ? colors.emerald : colors.error }}>{log.status_code || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
