/**
 * StartupOS AI — Observability Page
 * 
 * LLMOps dashboard: metrics cards, per-agent breakdown, log table, feedback.
 */

import { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import * as api from '../services/api';
import {
  cardStyle, metricStyle, labelStyle, colors, typography, spacing, radii,
  selectStyle, tableHeaderStyle, tableCellStyle, statusBadge, pageHeader,
  pageSubtitle,
} from '../styles/tokens';

const CARD_STYLE: React.CSSProperties = { ...cardStyle, flex: 1, minWidth: '160px' };
const METRIC_STYLE = metricStyle;

export default function ObservabilityPage() {
  const [metrics, setMetrics] = useState<Record<string, any> | null>(null);
  const [agentMetrics, setAgentMetrics] = useState<any[]>([]);
  const [logs, setLogs] = useState<api.ObservabilityLog[]>([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ agent_name: '', status: '' });

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    try {
      const [m, a, l] = await Promise.all([
        api.getMetrics(30).catch(() => null),
        api.getMetricsByAgent().catch(() => []),
        api.getObservabilityLogs({ limit: 20 }).catch(() => ({ total: 0, logs: [] })),
      ]);
      setMetrics(m);
      setAgentMetrics(a);
      setLogs(l.logs);
      setTotalLogs(l.total);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (logId: string, score: number) => {
    await api.submitFeedback(logId, score).catch(() => {});
    setLogs(prev => prev.map(l => l.id === logId ? { ...l, feedback_score: score } : l));
  };

  const loadFiltered = async () => {
    const data = await api.getObservabilityLogs({ ...filter, limit: 20 }).catch(() => ({ total: 0, logs: [] }));
    setLogs(data.logs);
    setTotalLogs(data.total);
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div style={{ padding: '4rem', textAlign: 'center', color: colors.textMuted }}>Loading observability data...</div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div style={{ padding: '2rem 2.5rem', maxWidth: '1200px' }}>
        <h1 style={{ ...pageHeader, margin: '0 0 0.3rem' }}>📊 Observability</h1>
        <p style={{ ...pageSubtitle, margin: '0 0 2rem' }}>LLMOps metrics, agent logs, and cost analysis</p>

        {/* ── Metric Cards ── */}
        <div style={{ display: 'flex', gap: spacing.md, flexWrap: 'wrap', marginBottom: spacing.xl }}>
          <div style={CARD_STYLE}>
            <div style={{ color: colors.textMuted, fontSize: typography.xs, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Calls</div>
            <div style={{ ...METRIC_STYLE, color: colors.primary }}>{metrics?.total_calls ?? 0}</div>
          </div>
          <div style={CARD_STYLE}>
            <div style={{ color: colors.textMuted, fontSize: typography.xs, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Tokens</div>
            <div style={{ ...METRIC_STYLE, color: colors.cyan }}>{(metrics?.total_tokens ?? 0).toLocaleString()}</div>
          </div>
          <div style={CARD_STYLE}>
            <div style={{ color: colors.textMuted, fontSize: typography.xs, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Cost</div>
            <div style={{ ...METRIC_STYLE, color: colors.emerald }}>${(metrics?.total_cost_usd ?? 0).toFixed(4)}</div>
          </div>
          <div style={CARD_STYLE}>
            <div style={{ color: colors.textMuted, fontSize: typography.xs, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Avg Latency</div>
            <div style={{ ...METRIC_STYLE, color: colors.amber }}>{metrics?.avg_latency_ms ?? 0}ms</div>
          </div>
          <div style={CARD_STYLE}>
            <div style={{ color: colors.textMuted, fontSize: typography.xs, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Success Rate</div>
            <div style={{ ...METRIC_STYLE, color: colors.emerald }}>{((metrics?.success_rate ?? 1) * 100).toFixed(1)}%</div>
          </div>
        </div>

        {/* ── Per-Agent Breakdown ── */}
        {agentMetrics.length > 0 && (
          <div style={{ ...CARD_STYLE, marginBottom: spacing.xl, minWidth: '100%' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: typography.semibold, margin: '0 0 1rem' }}>Per-Agent Performance</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {agentMetrics.map(a => {
                const maxTokens = Math.max(...agentMetrics.map(x => x.total_tokens || 1));
                const pct = ((a.total_tokens || 0) / maxTokens) * 100;
                return (
                  <div key={a.agent_name} style={{ display: 'flex', alignItems: 'center', gap: spacing.md }}>
                    <span style={{ width: '100px', fontSize: typography.sm, color: colors.textMuted, textTransform: 'capitalize' }}>{a.agent_name}</span>
                    <div style={{ flex: 1, height: '20px', background: 'rgba(255,255,255,0.05)', borderRadius: radii.sm, overflow: 'hidden' }}>
                      <div style={{ width: `${pct}%`, height: '100%', background: 'linear-gradient(90deg, #7c3aed, #06b6d4)', borderRadius: radii.sm, transition: 'width 0.5s' }} />
                    </div>
                    <span style={{ fontSize: typography.xs, color: colors.textMuted, width: '80px', textAlign: 'right' }}>{(a.total_tokens || 0).toLocaleString()} tok</span>
                    <span style={{ fontSize: typography.xs, color: colors.emerald, width: '60px', textAlign: 'right' }}>${(a.total_cost_usd || 0).toFixed(4)}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── Log Filters ── */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: spacing.md, alignItems: 'center' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: typography.semibold, margin: 0, flex: 1 }}>
            Agent Logs <span style={{ color: colors.textMuted, fontWeight: typography.regular }}>({totalLogs})</span>
          </h3>
          <select
            value={filter.status}
            onChange={e => { setFilter(f => ({ ...f, status: e.target.value })); }}
            style={selectStyle}
          >
            <option value="">All Status</option>
            <option value="success">Success</option>
            <option value="error">Error</option>
            <option value="fallback">Fallback</option>
          </select>
          <button onClick={loadFiltered} style={btnStyle}>Filter</button>
        </div>

        {/* ── Log Table ── */}
        <div style={{ ...CARD_STYLE, minWidth: '100%', padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: typography.sm }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${colors.border}` }}>
                {['Agent', 'Provider', 'Tokens', 'Cost', 'Latency', 'Status', 'Feedback'].map(h => (
                  <th key={h} style={tableHeaderStyle}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr><td colSpan={7} style={{ padding: spacing.xl, textAlign: 'center', color: colors.textMuted }}>No logs yet. Run a workflow to generate agent logs.</td></tr>
              ) : logs.map(log => (
                <tr key={log.id} style={{ borderBottom: `1px solid ${colors.borderHover}` }}>
                  <td style={{ ...tableCellStyle, textTransform: 'capitalize', color: colors.white }}>{log.agent_name}</td>
                  <td style={{ ...tableCellStyle, color: colors.textMuted }}>{log.model_provider}</td>
                  <td style={{ ...tableCellStyle, color: colors.cyan }}>{(log.total_tokens || 0).toLocaleString()}</td>
                  <td style={{ ...tableCellStyle, color: colors.emerald }}>${(log.cost_usd || 0).toFixed(4)}</td>
                  <td style={{ ...tableCellStyle, color: colors.amber }}>{log.latency_ms}ms</td>
                  <td style={tableCellStyle}>
                    <span style={{
                      ...statusBadge,
                      background: log.status === 'success' ? 'rgba(16,185,129,0.15)' : log.status === 'error' ? 'rgba(239,68,68,0.15)' : 'rgba(245,158,11,0.15)',
                      color: log.status === 'success' ? colors.emerald : log.status === 'error' ? colors.error : colors.amber,
                    }}>{log.status}</span>
                  </td>
                  <td style={tableCellStyle}>
                    <button onClick={() => handleFeedback(log.id, 1)} style={{ ...fbBtn, color: log.feedback_score === 1 ? colors.emerald : colors.textMuted }}>👍</button>
                    <button onClick={() => handleFeedback(log.id, -1)} style={{ ...fbBtn, color: log.feedback_score === -1 ? colors.error : colors.textMuted }}>👎</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </DashboardLayout>
  );
}

const btnStyle: React.CSSProperties = {
  padding: '0.4rem 0.8rem', background: 'linear-gradient(135deg, #7c3aed, #6d28d9)', border: 'none',
  borderRadius: radii.sm, color: colors.white, fontSize: typography.sm, fontWeight: typography.semibold, cursor: 'pointer',
};
const fbBtn: React.CSSProperties = {
  background: 'none', border: 'none', cursor: 'pointer', fontSize: typography.sm, padding: '0 0.2rem',
};
