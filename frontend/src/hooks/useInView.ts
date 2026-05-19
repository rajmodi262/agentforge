import { useState, useEffect, useRef, RefObject } from 'react';

export function useInView(options?: IntersectionObserverInit): [RefObject<HTMLDivElement | null>, boolean] {
  const ref = useRef<HTMLDivElement>(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.unobserve(el); // trigger once
        }
      },
      { threshold: 0.2, ...options }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return [ref, isInView];
}
