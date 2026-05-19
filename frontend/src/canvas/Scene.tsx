import React, { Suspense } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';
import NeuralCore from './NeuralCore';
import ParticleField from './ParticleField';

/* ═══════════════════════════════════════════════════════════════
   SCENE — Controlled bloom + vignette for cinematic feel
   Bloom is SUBTLE — just enough to make particles glow
   ═══════════════════════════════════════════════════════════════ */

interface SceneProps {
  scrollProgress: number;
  activeAgent: number;
  thermalProgress: number;
  mousePosition: { x: number; y: number };
  visible: boolean;
}

export default function Scene({ scrollProgress, activeAgent, thermalProgress, mousePosition, visible }: SceneProps) {
  if (!visible) return null;

  return (
    <div className="canvas-wrapper">
      <Canvas
        camera={{ position: [0, 0, 7], fov: 50 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        style={{ background: 'transparent' }}
      >
        <Suspense fallback={null}>
          <CameraChoreographer scrollProgress={scrollProgress} mousePosition={mousePosition} />

          <ambientLight intensity={0.15} />
          <pointLight position={[5, 5, 5]} intensity={0.4} color="#7c3aed" distance={15} />
          <pointLight position={[-5, -3, 3]} intensity={0.25} color="#06b6d4" distance={15} />

          <NeuralCore
            scrollProgress={scrollProgress}
            activeAgent={activeAgent}
            thermalProgress={thermalProgress}
            mousePosition={mousePosition}
          />
          <ParticleField />

          {/* Controlled bloom — subtle glow without washing out text */}
          <EffectComposer>
            <Bloom
              intensity={0.8}
              luminanceThreshold={0.25}
              luminanceSmoothing={0.4}
              radius={0.5}
              mipmapBlur
            />
            <Vignette
              offset={0.3}
              darkness={0.7}
              blendFunction={BlendFunction.NORMAL}
            />
          </EffectComposer>
        </Suspense>
      </Canvas>
    </div>
  );
}

/* Camera choreography — cinematic dolly/orbit driven by scroll */
function CameraChoreographer({ scrollProgress, mousePosition }: { scrollProgress: number; mousePosition: { x: number; y: number } }) {
  const { camera } = useThree();

  useFrame(() => {
    const p = scrollProgress;
    let targetX = 0, targetY = 0, targetZ = 7;

    if (p < 0.15) {
      // Hero — straight on, slowly dolly in
      const t = p / 0.15;
      targetZ = 7 - t * 0.5;
    } else if (p < 0.3) {
      // Agents — orbit right
      const t = (p - 0.15) / 0.15;
      targetZ = 6.5 - t * 1.0;
      targetX = Math.sin(t * Math.PI * 0.5) * 1.0;
      targetY = t * 0.3;
    } else if (p < 0.5) {
      // Thermal — zoom in, slight tilt
      const t = (p - 0.3) / 0.2;
      targetZ = 5.5 + Math.cos(t * Math.PI) * 0.3;
      targetX = Math.sin(t * Math.PI * 0.5) * 0.8;
      targetY = 0.3 + t * 0.4;
    } else if (p < 0.7) {
      // Agent dive — pull back
      const t = (p - 0.5) / 0.2;
      targetZ = 5.5 + t * 2.5;
      targetY = 0.7 + t * 0.8;
      targetX = 0.8 * (1 - t);
    } else {
      // Output/Proof/CTA — far back, centered
      const t = (p - 0.7) / 0.3;
      targetZ = 8 + t * 1;
      targetY = 1.5 - t * 1.5;
    }

    // Mouse parallax
    const mx = 0.0004;
    targetX += (mousePosition.x - (typeof window !== 'undefined' ? window.innerWidth / 2 : 0)) * mx;
    targetY += -(mousePosition.y - (typeof window !== 'undefined' ? window.innerHeight / 2 : 0)) * mx * 0.3;

    camera.position.x += (targetX - camera.position.x) * 0.025;
    camera.position.y += (targetY - camera.position.y) * 0.025;
    camera.position.z += (targetZ - camera.position.z) * 0.025;
    camera.lookAt(0, 0, 0);
  });

  return null;
}
