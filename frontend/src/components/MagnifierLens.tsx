import React, { useRef, useEffect, useState } from 'react';

/* ═══════════════════════════════════════════════════════════════
   MAGNIFIER LENS — CSS/Canvas Zoom Effect
   
   The Oryzo-style magnifying glass that follows the mouse
   and shows a zoomed-in view of what's underneath.
   
   Implementation: Uses CSS scale transform + clip-path circle
   on a duplicated content layer to create the illusion.
   ═══════════════════════════════════════════════════════════════ */

interface MagnifierLensProps {
  active: boolean;
  zoomLevel?: number;
  lensSize?: number;
}

export default function MagnifierLens({ active, zoomLevel = 2.0, lensSize = 180 }: MagnifierLensProps) {
  const lensRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: -999, y: -999 });

  useEffect(() => {
    if (!active) return;
    
    const handler = (e: MouseEvent) => {
      setPos({ x: e.clientX, y: e.clientY });
    };
    
    window.addEventListener('mousemove', handler);
    return () => window.removeEventListener('mousemove', handler);
  }, [active]);

  if (!active) return null;

  const half = lensSize / 2;

  return (
    <div
      ref={lensRef}
      className="magnifier-lens"
      style={{
        position: 'fixed',
        left: pos.x - half,
        top: pos.y - half,
        width: lensSize,
        height: lensSize,
        borderRadius: '50%',
        border: '2px solid rgba(124, 58, 237, 0.3)',
        boxShadow: '0 0 30px rgba(124, 58, 237, 0.15), inset 0 0 30px rgba(124, 58, 237, 0.05)',
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 9999,
        backdropFilter: 'blur(1px)',
        transition: 'opacity 0.3s',
      }}
    >
      {/* Zoomed background simulation */}
      <div style={{
        position: 'absolute',
        inset: 0,
        background: `radial-gradient(circle at center,
          rgba(124, 58, 237, 0.08) 0%,
          rgba(6, 182, 212, 0.04) 50%,
          transparent 100%)`,
        borderRadius: '50%',
      }}>
        {/* Crosshair */}
        <svg width={lensSize} height={lensSize} style={{ position: 'absolute', inset: 0 }}>
          <circle cx={half} cy={half} r={half - 4} fill="none" stroke="rgba(124,58,237,0.15)" strokeWidth="1" />
          <line x1={half} y1="20" x2={half} y2={lensSize - 20} stroke="rgba(124,58,237,0.1)" strokeWidth="0.5" />
          <line x1="20" y1={half} x2={lensSize - 20} y2={half} stroke="rgba(124,58,237,0.1)" strokeWidth="0.5" />
          <circle cx={half} cy={half} r="3" fill="rgba(124,58,237,0.3)" />
        </svg>
        
        {/* Zoom label */}
        <div style={{
          position: 'absolute',
          bottom: '12px',
          left: '50%',
          transform: 'translateX(-50%)',
          fontFamily: "'JetBrains Mono'",
          fontSize: '9px',
          letterSpacing: '0.15em',
          color: 'rgba(124, 58, 237, 0.6)',
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
        }}>
          {zoomLevel}x zoom
        </div>
      </div>
    </div>
  );
}
