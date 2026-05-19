import React, { useRef, useEffect, useCallback } from 'react';

/* ═══════════════════════════════════════════════════════════════
   PARTICLE TRAIL CURSOR — Glowing particle trail
   
   Spawns tiny particles that follow the cursor and fade out.
   Creates an ethereal, magical trailing effect.
   ═══════════════════════════════════════════════════════════════ */

interface Particle {
  x: number;
  y: number;
  alpha: number;
  size: number;
  vx: number;
  vy: number;
  color: string;
}

const COLORS = ['#7c3aed', '#06b6d4', '#a78bfa', '#818cf8', '#34d399'];

export default function ParticleTrail() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particles = useRef<Particle[]>([]);
  const mouse = useRef({ x: -100, y: -100 });
  const animFrame = useRef(0);

  const spawnParticle = useCallback((x: number, y: number) => {
    for (let i = 0; i < 2; i++) {
      particles.current.push({
        x,
        y,
        alpha: 0.6 + Math.random() * 0.4,
        size: 2 + Math.random() * 3,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5 - 0.5,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
      });
    }
    // Cap at 80 particles
    if (particles.current.length > 80) {
      particles.current = particles.current.slice(-80);
    }
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    let lastX = -100, lastY = -100;
    const mouseHandler = (e: MouseEvent) => {
      mouse.current = { x: e.clientX, y: e.clientY };
      // Only spawn if mouse has moved enough
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      if (dx * dx + dy * dy > 16) {
        spawnParticle(e.clientX, e.clientY);
        lastX = e.clientX;
        lastY = e.clientY;
      }
    };
    window.addEventListener('mousemove', mouseHandler);

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.current = particles.current.filter(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.alpha -= 0.015;
        p.size *= 0.98;

        if (p.alpha <= 0) return false;

        ctx.save();
        ctx.globalAlpha = p.alpha;
        ctx.fillStyle = p.color;
        ctx.shadowBlur = 8;
        ctx.shadowColor = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
        return true;
      });

      animFrame.current = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(animFrame.current);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', mouseHandler);
    };
  }, [spawnParticle]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 99997,
        pointerEvents: 'none',
      }}
    />
  );
}
