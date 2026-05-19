import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  AreaChart, Area, CartesianGrid, PieChart, Pie, Cell
} from 'recharts';
import * as api from '../services/api';

interface DashboardChartsProps {
  projects: api.Project[];
}

const COLORS = ['#7c3aed', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];
const STATUS_COLORS: Record<string, string> = {
  completed: '#10b981',
  running: '#f59e0b',
  error: '#ef4444',
  draft: '#64748b'
};

export default function DashboardCharts({ projects }: DashboardChartsProps) {
  const [stats, setStats] = useState<{
    totalCost: number;
    totalTokens: number;
    costData: any[];
  } | null>(null);

  useEffect(() => {
    let mounted = true;

    async function fetchStats() {
      if (projects.length === 0) return;
      
      const completedProjects = projects.filter(p => p.status === 'completed');
      let totalCost = 0;
      let totalTokens = 0;
      const costData: any[] = [];

      // Fetch results for completed projects to get their token/cost data
      await Promise.all(
        completedProjects.map(async (p, idx) => {
          try {
            const res = await api.getProjectResults(p.id);
            if (mounted) {
              totalCost += (res.total_cost || 0);
              totalTokens += (res.total_tokens || 0);
              costData.push({
                name: `P${idx + 1}`,
                title: p.title.substring(0, 15) + '...',
                cost: res.total_cost || 0,
                tokens: res.total_tokens || 0
              });
            }
          } catch (e) {
            // ignore
          }
        })
      );

      if (mounted) {
        setStats({ totalCost, totalTokens, costData });
      }
    }

    fetchStats();
    return () => { mounted = false; };
  }, [projects]);

  const statusData = [
    { name: 'Completed', value: projects.filter(p => p.status === 'completed').length, color: STATUS_COLORS.completed },
    { name: 'Running', value: projects.filter(p => p.status === 'running').length, color: STATUS_COLORS.running },
    { name: 'Draft/Error', value: projects.filter(p => p.status === 'draft' || p.status === 'error').length, color: STATUS_COLORS.draft }
  ].filter(d => d.value > 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2rem' }}>
      {/* Top Metrics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '1.5rem', borderRadius: '1rem', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Projects</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#f8fafc' }}>{projects.length}</div>
        </div>
        <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '1.5rem', borderRadius: '1rem', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Tokens Used</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#06b6d4' }}>{stats ? stats.totalTokens.toLocaleString() : '...'}</div>
        </div>
        <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '1.5rem', borderRadius: '1rem', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total API Cost</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#10b981' }}>${stats ? stats.totalCost.toFixed(3) : '...'}</div>
        </div>
      </div>

      {/* Charts Area */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem' }}>
        <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '1.5rem', borderRadius: '1rem', border: '1px solid rgba(255,255,255,0.05)' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', fontSize: '1rem', color: '#e2e8f0', fontWeight: 600 }}>API Cost per Blueprint ($)</h3>
          <div style={{ height: '200px', width: '100%' }}>
            {stats && stats.costData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats.costData}>
                  <defs>
                    <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#7c3aed" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val}`} width={40} />
                  <Tooltip 
                    contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '0.5rem', color: '#fff' }}
                    itemStyle={{ color: '#c4b5fd' }}
                  />
                  <Area type="monotone" dataKey="cost" name="Cost" stroke="#7c3aed" strokeWidth={3} fillOpacity={1} fill="url(#colorCost)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', fontSize: '0.9rem' }}>
                {projects.length === 0 ? 'No projects yet' : 'Gathering data...'}
              </div>
            )}
          </div>
        </div>

        <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '1.5rem', borderRadius: '1rem', border: '1px solid rgba(255,255,255,0.05)' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', fontSize: '1rem', color: '#e2e8f0', fontWeight: 600 }}>Status Distribution</h3>
          <div style={{ height: '200px', width: '100%' }}>
            {projects.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '0.5rem', color: '#fff' }}
                    itemStyle={{ color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
               <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', fontSize: '0.9rem' }}>
                 No data
               </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
