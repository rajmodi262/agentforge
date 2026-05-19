import React, { useRef, useState } from 'react';

/* ═══════════════════════════════════════════════════════════════
   TILT CARD — 3D Perspective Mouse-Tracking Card
   
   Card rotates toward mouse position on hover, creating a
   3D perspective effect. Like Apple product cards.
   
   Usage: <TiltCard><h3>Title</h3></TiltCard>
   ═══════════════════════════════════════════════════════════════ */

interface TiltCardProps {
  children: React.ReactNode;
  backContent?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  maxTilt?: number;
  glareOpacity?: number;
}

export default function TiltCard({
  children,
  backContent,
  className = '',
  style,
  maxTilt = 12,
  glareOpacity = 0.15,
}: TiltCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState('perspective(800px) rotateX(0deg) rotateY(0deg)');
  const [glarePos, setGlarePos] = useState({ x: 50, y: 50 });
  const [isHovered, setIsHovered] = useState(false);
  const [isFlipped, setIsFlipped] = useState(false);

  const handleMouseMove = (e: React.MouseEvent) => {
    const card = cardRef.current;
    if (!card) return;

    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    const rotateX = (0.5 - y) * maxTilt;
    const rotateY = (x - 0.5) * maxTilt;
    const baseRotY = isFlipped ? 180 : 0;

    setTransform(`perspective(800px) rotateX(${rotateX}deg) rotateY(${baseRotY + rotateY}deg) scale3d(1.02, 1.02, 1.02)`);
    setGlarePos({ x: x * 100, y: y * 100 });
  };

  const handleMouseLeave = () => {
    setTransform(`perspective(800px) rotateX(0deg) rotateY(${isFlipped ? 180 : 0}deg) scale3d(1, 1, 1)`);
    setIsHovered(false);
  };

  const handleClick = () => {
    if (backContent) {
      setIsFlipped(!isFlipped);
      // Immediately reset rotation to center flip
      setTransform(`perspective(800px) rotateX(0deg) rotateY(${!isFlipped ? 180 : 0}deg) scale3d(1, 1, 1)`);
    }
  };

  return (
    <div
      ref={cardRef}
      className={`glass-card tilt-card ${className}`}
      style={{
        ...style,
        transform,
        transition: isHovered ? 'none' : 'transform 0.6s cubic-bezier(0.25, 1, 0.5, 1)',
        transformStyle: 'preserve-3d',
        willChange: 'transform',
        position: 'relative',
        overflow: 'hidden',
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
    >
      {/* Glare overlay (front only) */}
      <div style={{
        position: 'absolute',
        inset: 0,
        background: `radial-gradient(circle at ${glarePos.x}% ${glarePos.y}%, rgba(255,255,255,${isHovered && !isFlipped ? glareOpacity : 0}) 0%, transparent 60%)`,
        transition: isHovered ? 'none' : 'opacity 0.4s',
        pointerEvents: 'none',
        zIndex: 3,
        borderRadius: 'inherit',
      }} />
      
      {/* Front Content */}
      <div style={{ 
        position: 'relative', 
        zIndex: 2, 
        backfaceVisibility: 'hidden',
      }}>
        {children}
      </div>

      {/* Back Content */}
      {backContent && (
        <div style={{ 
          position: 'absolute', 
          inset: 0, 
          zIndex: 1, 
          backfaceVisibility: 'hidden',
          transform: 'rotateY(180deg)',
          padding: 'var(--space-xl)',
          display: 'flex',
          flexDirection: 'column',
          background: 'var(--glass-fill-hover)',
          borderRadius: 'inherit',
        }}>
          {backContent}
        </div>
      )}
    </div>
  );
}
