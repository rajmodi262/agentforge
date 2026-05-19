import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';

/* ═══════════════════════════════════════════════════════════════
   FLUID TEXT — Magnetic Displacement Typography
   Letters subtly attract to or repel from the mouse cursor.
   ═══════════════════════════════════════════════════════════════ */

interface FluidTextProps {
  text: string;
  className?: string;
  tag?: React.ElementType;
}

export default function FluidText({ text, className = '', tag = 'h1' }: FluidTextProps) {
  const Tag = tag as any;
  const containerRef = useRef<HTMLHeadingElement>(null);
  const [mousePos, setMousePos] = useState({ x: -1000, y: -1000 });

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (rect) {
      setMousePos({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    }
  };

  const handleMouseLeave = () => {
    setMousePos({ x: -1000, y: -1000 }); // Move off-screen
  };

  // Split into words, then characters
  const words = text.split(' ');

  return (
    <Tag
      ref={containerRef as any}
      className={className}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ position: 'relative', display: 'inline-block' }}
    >
      {words.map((word, i) => (
        <span key={i} style={{ display: 'inline-block', whiteSpace: 'nowrap', marginRight: '0.25em' }}>
          {word.split('').map((char, j) => {
            return (
              <FluidChar
                key={j}
                char={char}
                mouseX={mousePos.x}
                mouseY={mousePos.y}
                parentRef={containerRef}
              />
            );
          })}
        </span>
      ))}
    </Tag>
  );
}

function FluidChar({ char, mouseX, mouseY, parentRef }: { char: string, mouseX: number, mouseY: number, parentRef: any }) {
  const charRef = useRef<HTMLSpanElement>(null);
  
  let xOffset = 0;
  let yOffset = 0;
  let scale = 1;

  if (charRef.current && parentRef.current) {
    // Determine relative position of this character inside the container
    const charRect = charRef.current.getBoundingClientRect();
    const parentRect = parentRef.current.getBoundingClientRect();
    
    const charCenterX = charRect.left - parentRect.left + charRect.width / 2;
    const charCenterY = charRect.top - parentRect.top + charRect.height / 2;

    const dx = mouseX - charCenterX;
    const dy = mouseY - charCenterY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    // Magnetic repel effect
    const radius = 100; // Effect radius in px
    if (distance < radius) {
      const force = (radius - distance) / radius;
      xOffset = -(dx / distance) * force * 15; // Max 15px displacement
      yOffset = -(dy / distance) * force * 15;
      scale = 1 + force * 0.1; // Slightly enlarge
    }
  }

  return (
    <motion.span
      ref={charRef}
      style={{ display: 'inline-block', originX: 0.5, originY: 0.5 }}
      animate={{ x: xOffset, y: yOffset, scale }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      {char}
    </motion.span>
  );
}
