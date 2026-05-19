import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

/* ═══════════════════════════════════════════════════════════════
   SPLIT TEXT REVEAL — Character-by-character animation
   
   Each character animates in individually with staggered delay,
   bouncing up from below with spring physics.
   ═══════════════════════════════════════════════════════════════ */

interface SplitTextRevealProps {
  text: string;
  className?: string;
  style?: React.CSSProperties;
  tag?: 'h1' | 'h2' | 'h3' | 'h4' | 'p' | 'span';
  delay?: number;
  staggerDelay?: number;
  highlightWords?: string[];
}

export default function SplitTextReveal({
  text,
  className = '',
  style,
  tag: Tag = 'h2',
  delay = 0,
  staggerDelay = 0.03,
  highlightWords = [],
}: SplitTextRevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setIsVisible(true); obs.disconnect(); } },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const words = text.split(' ');
  let charIndex = 0;

  return (
    <div ref={ref}>
      <Tag className={className} style={{ ...style, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0.3em' }}>
        {words.map((word, wi) => {
          const isHighlight = highlightWords.includes(word);
          const chars = word.split('');
          const wordEl = (
            <span key={wi} style={{ display: 'inline-flex', overflow: 'hidden' }}>
              {chars.map((char, ci) => {
                const i = charIndex++;
                return (
                  <motion.span
                    key={ci}
                    initial={{ y: '110%', opacity: 0, rotateX: -90 }}
                    animate={isVisible ? { y: '0%', opacity: 1, rotateX: 0 } : {}}
                    transition={{
                      delay: delay + i * staggerDelay,
                      duration: 0.5,
                      ease: [0.25, 1, 0.5, 1],
                    }}
                    style={{
                      display: 'inline-block',
                      transformOrigin: 'bottom',
                    }}
                    className={isHighlight ? 'text-gradient' : ''}
                  >
                    {char}
                  </motion.span>
                );
              })}
            </span>
          );
          charIndex++; // space
          return wordEl;
        })}
      </Tag>
    </div>
  );
}
