import React, { useState } from 'react';
import { motion, AnimatePresence, useScroll, useMotionValueEvent } from 'framer-motion';

/* ═══════════════════════════════════════════════════════════════
   DYNAMIC ISLAND — iOS-style sticky status pill
   Supports two modes:
   1. Scroll-based (default landing page behavior)
   2. Workflow-driven (live backend pipeline status)
   ═══════════════════════════════════════════════════════════════ */

type IslandState = 'ready' | 'pipeline' | 'processing' | 'complete' | 'error';

interface DynamicIslandProps {
  /** Override state from workflow hook */
  workflowStatus?: 'idle' | 'connecting' | 'running' | 'completed' | 'error' | 'reconnecting';
  /** Currently active agent name */
  currentAgent?: string;
  /** Number of completed agents (0-7) */
  completedCount?: number;
}

export default function DynamicIsland({ workflowStatus, currentAgent, completedCount = 0 }: DynamicIslandProps) {
  const [scrollState, setScrollState] = useState<IslandState>('ready');
  const { scrollYProgress } = useScroll();

  useMotionValueEvent(scrollYProgress, "change", (latest) => {
    // Only use scroll-based state if no workflow is active
    if (workflowStatus && workflowStatus !== 'idle') return;
    if (latest < 0.15) {
      setScrollState('ready');
    } else if (latest < 0.65) {
      setScrollState('pipeline');
    } else {
      setScrollState('complete');
    }
  });

  // Determine actual state: workflow overrides scroll
  let state: IslandState = scrollState;
  if (workflowStatus === 'connecting') state = 'pipeline';
  else if (workflowStatus === 'running') state = 'processing';
  else if (workflowStatus === 'completed') state = 'complete';
  else if (workflowStatus === 'error') state = 'error';

  const agentLabel = currentAgent
    ? currentAgent.replace(' Agent', '')
    : '';

  const config: Record<IslandState, { text: string; icon: string; color: string; width: number }> = {
    ready:      { text: 'System Ready',                                icon: '🟢', color: '#10b981', width: 140 },
    pipeline:   { text: 'Neural Pipeline Active',                      icon: '🧠', color: '#7c3aed', width: 200 },
    processing: { text: agentLabel ? `${agentLabel} Agent (${completedCount}/7)` : `Processing (${completedCount}/7)`, icon: '⚡', color: '#f59e0b', width: 230 },
    complete:   { text: 'Blueprint Generated ✓',                       icon: '🎯', color: '#06b6d4', width: 200 },
    error:      { text: 'Pipeline Error',                              icon: '⚠️', color: '#ef4444', width: 160 },
  };

  const current = config[state];

  return (
    <div style={{
      position: 'fixed',
      top: '24px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 9999,
      pointerEvents: 'none',
    }}>
      <motion.div
        layout
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0, width: current.width }}
        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
        style={{
          background: 'rgba(10, 10, 15, 0.75)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: `1px solid ${current.color}40`,
          boxShadow: `0 4px 20px ${current.color}20`,
          borderRadius: '999px',
          height: '36px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          overflow: 'hidden',
          padding: '0 16px',
        }}
      >
        <AnimatePresence mode="popLayout">
          <motion.div
            key={state + agentLabel}
            initial={{ opacity: 0, y: 10, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.8 }}
            transition={{ duration: 0.2 }}
            style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            {/* Spinner for processing state */}
            {state === 'processing' && (
              <motion.span
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                style={{ fontSize: '12px', display: 'inline-block' }}
              >⚡</motion.span>
            )}
            {state !== 'processing' && (
              <span style={{ fontSize: '12px' }}>{current.icon}</span>
            )}
            <span style={{ 
              fontFamily: "'JetBrains Mono', monospace", 
              fontSize: '11px', 
              fontWeight: 600, 
              color: current.color,
              letterSpacing: '0.05em',
              whiteSpace: 'nowrap'
            }}>
              {current.text}
            </span>
          </motion.div>
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
