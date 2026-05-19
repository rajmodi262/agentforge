import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Preloader({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(0);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const steps = [
      { target: 30, delay: 200 },
      { target: 60, delay: 600 },
      { target: 85, delay: 1000 },
      { target: 100, delay: 1500 },
    ];

    steps.forEach(({ target, delay }) => {
      setTimeout(() => setProgress(target), delay);
    });

    setTimeout(() => setIsExiting(true), 2200);
    setTimeout(() => onComplete(), 2800);
  }, [onComplete]);

  return (
    <AnimatePresence>
      {!isExiting && (
        <motion.div
          className="preloader"
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <motion.div
            className="preloader__text"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            Initializing Neural Cores...
          </motion.div>

          <div className="preloader__bar-track">
            <div
              className="preloader__bar-fill"
              style={{ transform: `scaleX(${progress / 100})` }}
            />
          </div>

          <motion.div
            style={{ fontFamily: 'JetBrains Mono', fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.1em' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            transition={{ delay: 0.5 }}
          >
            {progress}%
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
