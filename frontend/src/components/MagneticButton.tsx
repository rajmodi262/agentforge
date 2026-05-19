import React, { useRef, useCallback } from 'react';
import gsap from 'gsap';

interface MagneticButtonProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  variant?: 'primary' | 'outline';
  disabled?: boolean;
}

export default function MagneticButton({ children, className = '', onClick, variant = 'primary', disabled = false }: MagneticButtonProps) {
  const btnRef = useRef<HTMLButtonElement>(null);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const btn = btnRef.current;
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const dx = (e.clientX - rect.left - rect.width / 2) * 0.25;
    const dy = (e.clientY - rect.top - rect.height / 2) * 0.25;
    gsap.to(btn, { x: dx, y: dy, duration: 0.3, ease: 'power2.out' });
  }, []);

  const handleMouseLeave = useCallback(() => {
    const btn = btnRef.current;
    if (!btn) return;
    gsap.to(btn, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1, 0.3)' });
  }, []);

  const variantClass = variant === 'outline' ? 'magnetic-btn--outline' : '';

  return (
    <button
      ref={btnRef}
      className={`magnetic-btn ${variantClass} ${className}`}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      disabled={disabled}
      style={disabled ? { opacity: 0.5, pointerEvents: 'none' } : undefined}
    >
      {children}
    </button>
  );
}
