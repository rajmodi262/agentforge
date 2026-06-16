import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { colors, typography, spacing, radii } from '../styles/tokens';

/* ═══════════════════════════════════════════════════════════════
   CODE PREVIEW — Dual Pane Agent Output
   Supports two modes:
   1. Static: pre-defined lines with delays (demo mode)
   2. Live:   streaming lines from WebSocket (real mode)
   ═══════════════════════════════════════════════════════════════ */

interface LogLine {
  text: string;
  type: string;
  delay?: number;
}

interface CodePreviewProps {
  /** Static lines with delays (demo mode) */
  lines?: LogLine[];
  /** Live-streamed lines (real mode — overrides static lines) */
  liveLines?: LogLine[];
  /** Whether the component is visible */
  isInView: boolean;
  /** Title for the left pane */
  title?: string;
}

export default function CodePreview({ lines, liveLines, isInView, title }: CodePreviewProps) {
  const [visibleLines, setVisibleLines] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Choose source: live lines override static lines
  const activeLines = liveLines && liveLines.length > 0 ? liveLines : (lines || []);
  const isLive = !!(liveLines && liveLines.length > 0);

  // Static mode: stagger line appearance using delay
  useEffect(() => {
    if (isLive) return; // Live mode handles its own lines
    if (!isInView) {
      setVisibleLines(0);
      return;
    }
    
    const timers: ReturnType<typeof setTimeout>[] = [];
    
    activeLines.forEach((line, i) => {
      const timer = setTimeout(() => {
        setVisibleLines((prev) => Math.max(prev, i + 1));
      }, line.delay || i * 200);
      timers.push(timer);
    });

    return () => timers.forEach(clearTimeout);
  }, [isInView, isLive, activeLines]);

  // Live mode: show all lines, auto-scroll to bottom
  useEffect(() => {
    if (isLive && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [isLive, activeLines.length]);

  const displayLines = isLive ? activeLines : activeLines.slice(0, visibleLines);
  const progress = activeLines.length > 0 
    ? (isLive ? displayLines.length / Math.max(activeLines.length, 1) : visibleLines / activeLines.length)
    : 0;

  // Map terminal line types to CSS colors
  const lineColor = (type: string) => {
    switch (type) {
      case 'command': return colors.primary;
      case 'success': return colors.emerald;
      case 'error':   return colors.error;
      case 'info':    return colors.textMuted;
      case 'output':  return colors.text;
      case 'agent':   return colors.primary;
      case 'highlight': return colors.cyan;
      case 'system':  return colors.textMuted;
      default:        return colors.text;
    }
  };

  const panelTitle = title || (isLive ? '● LIVE — Agent Pipeline' : '● LIVE — Developer Agent Output');

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: spacing.md,
      maxWidth: '1200px',
      width: '100%',
      margin: '0 auto',
    }}>
      
      {/* Left Pane: Terminal / Code */}
      <motion.div 
        className="terminal"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        style={{ height: '350px', display: 'flex', flexDirection: 'column' }}
      >
        <div className="mono-label" style={{ marginBottom: spacing.md, color: isLive ? colors.emerald : colors.primary }}>
          {panelTitle}
        </div>
        <div 
          ref={scrollRef}
          style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}
        >
          {displayLines.map((line, i) => (
            <motion.div 
              key={`${i}-${line.text.slice(0, 20)}`}
              className="terminal__line"
              initial={{ opacity: 0, x: -10 }} 
              animate={{ opacity: 1, x: 0 }} 
              transition={{ duration: 0.15 }}
              style={{ 
                fontFamily: typography.fontFamilyMono,
                fontSize: '11px',
                lineHeight: 1.6,
                color: lineColor(line.type),
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {line.text}
            </motion.div>
          ))}
          {/* Blinking cursor */}
          {((isLive && progress < 1) || (!isLive && visibleLines < activeLines.length)) && (
            <motion.div
              animate={{ opacity: [1, 0, 1] }}
              transition={{ repeat: Infinity, duration: 0.8 }}
              style={{ width: '8px', height: '14px', background: colors.primary, marginTop: '4px' }}
            />
          )}
        </div>
      </motion.div>

      {/* Right Pane: Visual Render Preview */}
      <motion.div
        className="glass-card"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        style={{ 
          height: '350px', 
          display: 'flex', 
          flexDirection: 'column',
          padding: 0,
          overflow: 'hidden',
          background: colors.bg,
          border: `1px solid ${colors.borderHover}`
        }}
      >
        {/* Mock Browser Topbar */}
        <div style={{ 
          height: '32px', 
          borderBottom: `1px solid ${colors.border}`,
          display: 'flex',
          alignItems: 'center',
          padding: '0 12px',
          gap: '6px',
          background: 'rgba(255,255,255,0.02)'
        }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ff5f56' }} />
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ffbd2e' }} />
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#27c93f' }} />
          <span style={{ marginLeft: '8px', fontFamily: typography.fontFamilyMono, fontSize: '10px', color: colors.textMuted }}>
            {isLive ? 'agentforge.ai/blueprint' : 'preview.agentforge.ai'}
          </span>
        </div>

        {/* Render Canvas */}
        <div style={{ padding: '24px', flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <AnimatePresence>
            {progress > 0.1 && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                style={{ height: '32px', width: '40%', background: colors.primaryGlow, borderRadius: '4px' }}
              />
            )}
            {progress > 0.3 && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
                style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}
              >
                <div style={{ height: '80px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', border: `1px solid ${colors.borderHover}` }} />
                <div style={{ height: '80px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', border: `1px solid ${colors.borderHover}` }} />
              </motion.div>
            )}
            {progress > 0.6 && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                style={{ flex: 1, background: 'rgba(6, 182, 212, 0.1)', borderRadius: '8px', border: `1px solid ${colors.cyan}30` }}
              />
            )}
            {progress >= 1 && isLive && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                style={{
                  position: 'absolute',
                  bottom: '24px',
                  right: '24px',
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: `1px solid ${colors.emerald}50`,
                  borderRadius: '8px',
                  padding: '8px 16px',
                  fontFamily: typography.fontFamilyMono,
                  fontSize: '11px',
                  color: colors.emerald,
                }}
              >
                ✓ Blueprint Ready
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

    </div>
  );
}
