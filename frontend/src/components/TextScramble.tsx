import React, { useRef, useEffect, useState } from 'react';

/* ═══════════════════════════════════════════════════════════════
   TEXT SCRAMBLE — Cipher Decode Effect
   
   Text characters cycle through random glyphs before resolving
   to the final text. Like a hacker terminal decoding a message.
   
   Usage: <TextScramble text="Hello World" trigger={isInView} />
   ═══════════════════════════════════════════════════════════════ */

const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&*!?<>{}[]|/\\~^';

interface TextScrambleProps {
  text: string;
  trigger?: boolean;
  speed?: number;
  className?: string;
  style?: React.CSSProperties;
  tag?: 'h1' | 'h2' | 'h3' | 'h4' | 'span' | 'div' | 'p';
}

export default function TextScramble({
  text,
  trigger = true,
  speed = 30,
  className = '',
  style,
  tag: Tag = 'span',
}: TextScrambleProps) {
  const [display, setDisplay] = useState('');
  const frameRef = useRef(0);
  const hasTriggered = useRef(false);

  useEffect(() => {
    if (!trigger || hasTriggered.current) return;
    hasTriggered.current = true;

    let iteration = 0;
    const totalFrames = text.length * 3;

    const animate = () => {
      const progress = iteration / totalFrames;
      const resolvedCount = Math.floor(progress * text.length);

      let result = '';
      for (let i = 0; i < text.length; i++) {
        if (text[i] === ' ') {
          result += ' ';
        } else if (i < resolvedCount) {
          result += text[i];
        } else {
          result += CHARS[Math.floor(Math.random() * CHARS.length)];
        }
      }

      setDisplay(result);
      iteration++;

      if (iteration <= totalFrames) {
        frameRef.current = window.setTimeout(animate, speed);
      } else {
        setDisplay(text);
      }
    };

    animate();
    return () => clearTimeout(frameRef.current);
  }, [trigger, text, speed]);

  return (
    <Tag className={className} style={{ ...style, fontVariantNumeric: 'tabular-nums' }}>
      {display || (trigger ? '' : text)}
    </Tag>
  );
}
