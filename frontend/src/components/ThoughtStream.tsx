import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { WorkflowEvent } from '../hooks/useWorkflowSocket';

interface ThoughtStreamProps {
  events: WorkflowEvent[];
}

export default function ThoughtStream({ events }: ThoughtStreamProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [events]);

  const getAgentColor = (agent: string) => {
    if (!agent) return '#64748b';
    const lower = agent.toLowerCase();
    if (lower.includes('ceo')) return '#8b5cf6'; // Violet
    if (lower.includes('research')) return '#06b6d4'; // Cyan
    if (lower.includes('marketing')) return '#ec4899'; // Pink
    if (lower.includes('developer')) return '#10b981'; // Emerald
    if (lower.includes('finance')) return '#f59e0b'; // Amber
    if (lower.includes('board')) return '#ef4444'; // Red
    return '#64748b'; // Slate
  };

  const getAgentIcon = (agent: string) => {
    if (!agent) return '🤖';
    const lower = agent.toLowerCase();
    if (lower.includes('ceo')) return '🧠';
    if (lower.includes('research')) return '🔍';
    if (lower.includes('marketing')) return '📈';
    if (lower.includes('developer')) return '💻';
    if (lower.includes('finance')) return '💰';
    if (lower.includes('board')) return '⚖️';
    return '🤖';
  };

  return (
    <div 
      ref={containerRef}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        padding: '1.5rem',
        background: 'rgba(15, 23, 42, 0.4)',
        border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: '1rem',
        maxHeight: '600px',
        overflowY: 'auto',
        fontFamily: "'Inter', sans-serif",
        boxShadow: 'inset 0 2px 20px rgba(0,0,0,0.2)'
      }}
    >
      <AnimatePresence initial={false}>
        {events.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ color: '#94a3b8', textAlign: 'center', padding: '2rem 0', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}
          >
            <div className="spinner" style={{
              width: '24px', height: '24px',
              border: '3px solid rgba(124, 58, 237, 0.3)',
              borderTopColor: '#7c3aed',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            Initializing neural pathways...
          </motion.div>
        )}
        
        {events.map((ev, i) => {
          let agent = '';
          let title = '';
          let content = '';

          if (ev.type === 'agent_reasoning_step') {
            agent = ev.agent;
            title = `Step ${ev.step}/${ev.total_steps} — ${ev.label}`;
            content = ev.content;
          } else if (ev.type === 'agent_thinking') {
            agent = ev.agent;
            title = 'Thinking...';
            content = ev.content;
          } else if (ev.type === 'agent_tool_call') {
            agent = ev.agent;
            title = `Tool Call: ${ev.tool}`;
            content = ev.query;
          } else if (ev.type === 'board_meeting_round') {
            agent = 'Board Meeting';
            title = `Round ${ev.round}: ${ev.challenger} -> ${ev.target}`;
            content = ev.content;
          } else {
            // Ignore other events for the thought stream
            return null;
          }

          if (!content) return null;

          const color = getAgentColor(agent);
          const icon = getAgentIcon(agent);

          return (
            <motion.div
              key={`${ev.type}-${i}`}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              style={{
                display: 'flex',
                gap: '1rem',
                background: 'rgba(30, 41, 59, 0.5)',
                borderLeft: `3px solid ${color}`,
                padding: '1rem',
                borderRadius: '0.5rem',
              }}
            >
              <div style={{ fontSize: '1.5rem', flexShrink: 0 }}>{icon}</div>
              <div style={{ flex: 1, overflow: 'hidden' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                  <span style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.9rem' }}>{agent}</span>
                  <span style={{ color: color, fontSize: '0.75rem', fontWeight: 500, padding: '0.1rem 0.4rem', background: `${color}15`, borderRadius: '1rem', whiteSpace: 'nowrap' }}>
                    {title}
                  </span>
                </div>
                <div style={{ 
                  color: '#cbd5e1', 
                  fontSize: '0.85rem', 
                  lineHeight: 1.6,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {content}
                </div>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
