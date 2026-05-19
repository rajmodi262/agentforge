import React from 'react';

/* ═══════════════════════════════════════════════════════════════
   INFINITE MARQUEE — Non-stop scrolling ticker
   
   CSS-only infinite horizontal scroll. No JS needed.
   Items duplicate to create seamless loop illusion.
   
   Usage: <InfiniteMarquee items={['React', 'Three.js']} />
   ═══════════════════════════════════════════════════════════════ */

interface InfiniteMarqueeProps {
  items: Array<{ text: string; icon?: string }>;
  speed?: number;
  direction?: 'left' | 'right';
  separator?: string;
}

export default function InfiniteMarquee({
  items,
  speed = 30,
  direction = 'left',
  separator = '✦',
}: InfiniteMarqueeProps) {
  // Duplicate items 4x for seamless loop
  const allItems = [...items, ...items, ...items, ...items];

  return (
    <div className="marquee-container" style={{
      overflow: 'hidden',
      width: '100%',
      padding: '20px 0',
      position: 'relative',
    }}>
      {/* Fade edges */}
      <div style={{
        position: 'absolute', inset: 0, zIndex: 2,
        background: 'linear-gradient(90deg, var(--void) 0%, transparent 10%, transparent 90%, var(--void) 100%)',
        pointerEvents: 'none',
      }} />
      
      <div style={{
        display: 'flex',
        width: 'max-content',
        animation: `marquee-scroll ${speed}s linear infinite`,
        animationDirection: direction === 'right' ? 'reverse' : 'normal',
      }}>
        {allItems.map((item, i) => (
          <React.Fragment key={i}>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '0 24px',
              fontFamily: "'Space Grotesk', sans-serif",
              fontSize: '16px',
              fontWeight: 500,
              color: 'var(--text-secondary)',
              whiteSpace: 'nowrap',
              letterSpacing: '0.02em',
            }}>
              {item.icon && <span style={{ fontSize: '20px' }}>{item.icon}</span>}
              {item.text}
            </span>
            <span style={{
              color: 'var(--primary)',
              opacity: 0.3,
              padding: '0 8px',
              fontSize: '10px',
            }}>{separator}</span>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
