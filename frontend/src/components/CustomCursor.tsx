import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useMousePosition } from '../hooks/useMousePosition';

export default function CustomCursor() {
  const { x, y } = useMousePosition();

  return (
    <>
      <motion.div
        className="cursor-dot"
        animate={{ x, y }}
        transition={{ type: 'spring', stiffness: 500, damping: 28, mass: 0.5 }}
      />
      <motion.div
        className="cursor-ring"
        animate={{ x, y }}
        transition={{ type: 'spring', stiffness: 250, damping: 20, mass: 0.8 }}
      />
    </>
  );
}
