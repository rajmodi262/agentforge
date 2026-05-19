import React from 'react';
import { motion } from 'framer-motion';

interface ScrollProgressProps {
  progress: number;
}

export default function ScrollProgress({ progress }: ScrollProgressProps) {
  return (
    <motion.div
      className="scroll-progress"
      style={{ transform: `scaleX(${progress})` }}
    />
  );
}
