import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const COUNT = 200;

export default function ParticleField() {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  const particles = useMemo(() => {
    return Array.from({ length: COUNT }, () => ({
      x: (Math.random() - 0.5) * 30,
      y: (Math.random() - 0.5) * 30,
      z: (Math.random() - 0.5) * 30,
      speed: 0.1 + Math.random() * 0.3,
      phase: Math.random() * Math.PI * 2,
      size: 0.005 + Math.random() * 0.015,
    }));
  }, []);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const mesh = meshRef.current;
    if (!mesh) return;

    for (let i = 0; i < COUNT; i++) {
      const p = particles[i];
      dummy.position.set(
        p.x + Math.sin(t * p.speed + p.phase) * 0.5,
        p.y + Math.cos(t * p.speed * 0.7 + p.phase) * 0.3,
        p.z + Math.sin(t * p.speed * 0.5 + p.phase) * 0.4
      );
      dummy.scale.setScalar(p.size);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, COUNT]}>
      <sphereGeometry args={[1, 6, 6]} />
      <meshBasicMaterial color="#6d28d9" transparent opacity={0.25} />
    </instancedMesh>
  );
}
