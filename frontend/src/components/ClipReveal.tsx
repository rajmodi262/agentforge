import React, { useRef, useEffect, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

/* ═══════════════════════════════════════════════════════════════
   CLIP-PATH REVEAL — The Oryzo "3D → 2D" Sleight-of-Hand
   
   How it works (exactly like the reference):
   Step A: The 3D Neural Core rotates to face camera dead-on
   Step B: An HTML <div> with the dashboard preview is positioned
           absolute, perfectly over the center of the screen
   Step C: This div has: clip-path: circle(0% at 50% 50%)
   Step D: The exact moment the 3D core "locks," GSAP animates
           clip-path to circle(75% at 50% 50%), masking over
           the 3D canvas — making it look like it transformed
   ═══════════════════════════════════════════════════════════════ */

interface ClipRevealProps {
  children: React.ReactNode;
  triggerSelector: string;
  startOffset?: string;
  endOffset?: string;
}

export default function ClipReveal({ children, triggerSelector, startOffset = 'top center', endOffset = 'bottom center' }: ClipRevealProps) {
  const revealRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = revealRef.current;
    if (!el) return;

    // Start fully clipped (invisible)
    gsap.set(el, { clipPath: 'circle(0% at 50% 50%)' });

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: triggerSelector,
        start: startOffset,
        end: endOffset,
        scrub: 0.5,
      },
    });

    tl.to(el, {
      clipPath: 'circle(75% at 50% 50%)',
      duration: 1,
      ease: 'power2.inOut',
    });

    return () => {
      tl.kill();
    };
  }, [triggerSelector, startOffset, endOffset]);

  return (
    <div
      ref={revealRef}
      className="clip-reveal"
      style={{
        position: 'sticky',
        top: 0,
        height: '100vh',
        width: '100%',
        zIndex: 5,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        clipPath: 'circle(0% at 50% 50%)',
        willChange: 'clip-path',
        overflow: 'hidden'
      }}
    >
      {children}
    </div>
  );
}

import { colors, typography, spacing, radii, gradients } from '../styles/tokens';

/* ─── Dashboard Preview (what gets revealed) ─── */
export function DashboardPreview() {
  return (
    <div style={{
      width: '100%',
      height: '100%',
      background: 'linear-gradient(180deg, #0f0d19 0%, #1a1625 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '60px',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '1100px',
        background: colors.bgCard,
        border: `1px solid ${colors.border}`,
        borderRadius: '16px',
        padding: '32px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
      }}>
        {/* Mock dashboard header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '32px', height: '32px', background: gradients.hero, borderRadius: radii.sm }} />
            <span style={{ fontFamily: typography.fontFamily, fontWeight: typography.bold, fontSize: '16px', color: colors.white }}>StartupOS Dashboard</span>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {['Overview', 'Agents', 'Blueprint', 'Export'].map((tab, i) => (
              <span key={i} style={{
                padding: '6px 14px',
                borderRadius: radii.sm,
                fontSize: typography.xs,
                fontFamily: typography.fontFamily,
                color: i === 0 ? colors.white : colors.textMuted,
                background: i === 0 ? colors.primaryGlow : 'transparent',
                border: i === 0 ? `1px solid ${colors.borderHover}` : '1px solid transparent',
              }}>{tab}</span>
            ))}
          </div>
        </div>

        {/* Mock pipeline progress */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: '8px',
        }}>
          {['CEO', 'Research', 'Marketing', 'Developer', 'Finance', 'Analytics', 'Ops'].map((name, i) => {
            const chartColors = [colors.primary, colors.cyan, colors.emerald, '#3b82f6', colors.amber, '#f97316', colors.text];
            const c = chartColors[i];
            return (
              <div key={i} style={{
                padding: '16px 8px',
                background: colors.bgCard,
                border: `1px solid ${c}30`,
                borderRadius: radii.sm,
                textAlign: 'center',
              }}>
                <div style={{ fontSize: '20px', marginBottom: '6px' }}>
                  {['🧠', '🔬', '📡', '⚡', '💎', '📊', '⚙️'][i]}
                </div>
                <div style={{
                  fontFamily: typography.fontFamily,
                  fontSize: '9px',
                  color: c,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                }}>{name}</div>
                <div style={{
                  height: '3px',
                  background: `${c}20`,
                  borderRadius: '2px',
                  marginTop: '8px',
                  overflow: 'hidden',
                }}>
                  <div style={{
                    height: '100%',
                    width: `${60 + i * 5}%`,
                    background: c,
                    borderRadius: '2px',
                  }} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Mock report output */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '2fr 1fr',
          gap: '16px',
        }}>
          <div style={{
            background: 'rgba(0,0,0,0.3)',
            border: `1px solid ${colors.border}`,
            borderRadius: radii.sm,
            padding: '20px',
            fontFamily: typography.fontFamily,
            fontSize: '11px',
            lineHeight: 1.8,
            color: colors.textMuted,
          }}>
            <div style={{ color: colors.emerald, marginBottom: '8px' }}>● Blueprint Generation — Complete</div>
            <div>[CEO] Market positioning: <span style={{ color: colors.primary }}>Premium B2B SaaS</span></div>
            <div>[Research] TAM: <span style={{ color: colors.cyan }}>$4.2B</span> | CAGR: <span style={{ color: colors.cyan }}>23%</span></div>
            <div>[Finance] Break-even: <span style={{ color: colors.amber }}>Month 14</span></div>
            <div>[Developer] Stack: <span style={{ color: '#3b82f6' }}>React + FastAPI + PostgreSQL</span></div>
            <div style={{ color: colors.emerald, marginTop: '8px' }}>42 pages generated in 1m 47s ✓</div>
          </div>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}>
            {[
              { label: 'Pages', value: '42', color: colors.primary },
              { label: 'Data Points', value: '10,247', color: colors.cyan },
              { label: 'Time', value: '1m 47s', color: colors.emerald },
            ].map((stat, i) => (
              <div key={i} style={{
                background: colors.bgCard,
                border: `1px solid ${colors.border}`,
                borderRadius: radii.sm,
                padding: '14px',
                textAlign: 'center',
              }}>
                <div style={{ fontFamily: typography.fontFamily, fontSize: '24px', fontWeight: typography.bold, color: stat.color }}>{stat.value}</div>
                <div style={{ fontFamily: typography.fontFamily, fontSize: '9px', color: colors.textMuted, letterSpacing: '0.1em', textTransform: 'uppercase' }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
