import React from 'react';
import { motion } from 'framer-motion';
import { colors } from '../styles/tokens';

/* ═══════════════════════════════════════════════════════════════
   DATA FLOW LINES — SVG Network connections between Bento Grid
   ═══════════════════════════════════════════════════════════════ */

export default function DataFlowLines() {
  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      pointerEvents: 'none',
      zIndex: 0,
    }}>
      <svg width="100%" height="100%" style={{ overflow: 'visible' }}>
        <defs>
          <linearGradient id="flow-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={colors.primary} stopOpacity="0.8" />
            <stop offset="50%" stopColor={colors.secondary} stopOpacity="0.8" />
            <stop offset="100%" stopColor={colors.accent} stopOpacity="0" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* Path 1: From Market Analysis to Go-To-Market */}
        <motion.path
          d="M 200 150 L 500 150 L 550 200"
          fill="none"
          stroke="url(#flow-gradient)"
          strokeWidth="2"
          filter="url(#glow)"
          initial={{ pathLength: 0, opacity: 0 }}
          whileInView={{ pathLength: 1, opacity: 0.6 }}
          viewport={{ once: true }}
          transition={{ duration: 1.5, ease: "easeInOut" }}
        />

        {/* Path 2: Financial Model to Tech Architecture */}
        <motion.path
          d="M 800 150 L 800 300 L 600 350"
          fill="none"
          stroke="url(#flow-gradient)"
          strokeWidth="2"
          filter="url(#glow)"
          initial={{ pathLength: 0, opacity: 0 }}
          whileInView={{ pathLength: 1, opacity: 0.6 }}
          viewport={{ once: true }}
          transition={{ duration: 2, ease: "easeInOut", delay: 0.5 }}
        />

        {/* Path 3: Connecting Operations down */}
        <motion.path
          d="M 300 400 L 300 500 L 700 500"
          fill="none"
          stroke="url(#flow-gradient)"
          strokeWidth="2"
          filter="url(#glow)"
          initial={{ pathLength: 0, opacity: 0 }}
          whileInView={{ pathLength: 1, opacity: 0.6 }}
          viewport={{ once: true }}
          transition={{ duration: 1.8, ease: "easeInOut", delay: 1 }}
        />
        
        {/* Animated moving dot on Path 1 */}
        <motion.circle
          r="4"
          fill="#ffffff"
          filter="url(#glow)"
          initial={{ offsetDistance: "0%" } as any}
          animate={{ offsetDistance: "100%" } as any}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "linear"
          }}
          style={{
            offsetPath: "path('M 200 150 L 500 150 L 550 200')",
          } as any}
        />
      </svg>
    </div>
  );
}
