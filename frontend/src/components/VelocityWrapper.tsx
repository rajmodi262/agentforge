import React from 'react';
import { motion, useScroll, useVelocity, useSpring, useTransform } from 'framer-motion';

/* ═══════════════════════════════════════════════════════════════
   VELOCITY WRAPPER — Scroll Velocity Skewing
   ═══════════════════════════════════════════════════════════════ */

export default function VelocityWrapper({ children }: { children: React.ReactNode }) {
  const { scrollY } = useScroll();
  const scrollVelocity = useVelocity(scrollY);
  
  const smoothVelocity = useSpring(scrollVelocity, {
    damping: 50,
    stiffness: 400
  });

  // Skew up to 3 degrees max
  const skew = useTransform(smoothVelocity, [-1000, 1000], [-3, 3], { clamp: true });

  return (
    <motion.div style={{ skewY: skew }}>
      {children}
    </motion.div>
  );
}
