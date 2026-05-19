import React, { useState, useRef, useEffect } from 'react';

/* ═══════════════════════════════════════════════════════════════
   HOVER SCRAMBLE — Cyberpunk cipher decoding on hover
   ═══════════════════════════════════════════════════════════════ */

interface HoverScrambleProps {
  text: string;
  className?: string;
  style?: React.CSSProperties;
}

const CHARS = '!<>-_\\\\/[]{}—=+*^?#________';

export default function HoverScramble({ text, className = '', style = {} }: HoverScrambleProps) {
  const [displayText, setDisplayText] = useState(text);
  const [isHovering, setIsHovering] = useState(false);
  const intervalRef = useRef<number | null>(null);

  const scramble = () => {
    let iteration = 0;
    if (intervalRef.current) clearInterval(intervalRef.current);

    intervalRef.current = window.setInterval(() => {
      setDisplayText((prev) =>
        text
          .split('')
          .map((letter, index) => {
            if (index < iteration) {
              return text[index];
            }
            return CHARS[Math.floor(Math.random() * CHARS.length)];
          })
          .join('')
      );

      if (iteration >= text.length) {
        if (intervalRef.current) clearInterval(intervalRef.current);
      }
      iteration += 1 / 2; // Speed of decoding
    }, 30);
  };

  const handleMouseEnter = () => {
    setIsHovering(true);
    scramble();
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
    if (intervalRef.current) clearInterval(intervalRef.current);
    setDisplayText(text); // Reset immediately
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  return (
    <span
      className={className}
      style={{ ...style, display: 'inline-block', cursor: 'none' }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {displayText}
    </span>
  );
}
