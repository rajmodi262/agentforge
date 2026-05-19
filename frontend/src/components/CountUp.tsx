import React, { useEffect, useState } from 'react';
import { useInView } from '../hooks/useInView';

interface CountUpProps {
  end: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  label: string;
}

export default function CountUp({ end, duration = 2000, prefix = '', suffix = '', label }: CountUpProps) {
  const [ref, isInView] = useInView();
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;

    let startTime: number;
    let rafId: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      // Ease out quart
      const eased = 1 - Math.pow(1 - progress, 4);
      setCount(Math.round(eased * end));

      if (progress < 1) {
        rafId = requestAnimationFrame(animate);
      }
    };

    rafId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafId);
  }, [isInView, end, duration]);

  return (
    <div className="stat-block" ref={ref}>
      <div className="stat-block__number">
        {prefix}{count.toLocaleString()}{suffix}
      </div>
      <div className="stat-block__label">{label}</div>
    </div>
  );
}
