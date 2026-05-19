import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { fibonacciSphere } from '../utils/math';
import { AGENTS } from '../utils/constants';

/* ═══════════════════════════════════════════════════════════════
   NEURAL CORE — Subtle, elegant, readable
   
   Custom GLSL shaders but with CONTROLLED brightness.
   The 3D brain is a mood-setter, NOT a spotlight.
   ═══════════════════════════════════════════════════════════════ */

const PARTICLE_COUNT = 350;
const CORE_RADIUS = 2.0;
const AGENT_COLORS = AGENTS.map(a => new THREE.Color(a.color));

const vertexShader = /* glsl */`
uniform float uTime;
uniform float uScrollProgress;
uniform float uThermalProgress;
uniform float uPulseIntensity;

varying float vBrightness;
varying float vDistFromCenter;

void main() {
  vec3 pos = position;

  // Gentle breathing
  float breath = sin(uTime * 1.2 + pos.y * 3.0) * 0.02;
  pos *= 1.0 + breath;

  // Subtle wobble
  pos.x += sin(uTime * 0.6 + pos.y * 4.0) * 0.03;
  pos.z += cos(uTime * 0.5 + pos.x * 4.0) * 0.03;

  vDistFromCenter = length(position);
  vBrightness = 0.5 + 0.5 * sin(uTime * 1.5 + vDistFromCenter * 4.0);

  vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
  gl_Position = projectionMatrix * mvPosition;

  // Visible but not overwhelming point size
  float size = 2.8 + uPulseIntensity * 2.0;
  size += sin(uTime * 2.0 + vDistFromCenter * 6.0) * 1.0;
  gl_PointSize = size * (200.0 / -mvPosition.z);
}
`;

const fragmentShader = /* glsl */`
uniform float uTime;
uniform float uThermalProgress;
uniform vec3 uActiveColor;
uniform float uPulseIntensity;

varying float vBrightness;
varying float vDistFromCenter;

vec3 thermalColor(float lum) {
  if (lum < 0.25) return mix(vec3(0.0, 0.0, 0.2), vec3(0.0, 0.2, 0.8), lum / 0.25);
  if (lum < 0.5) return mix(vec3(0.0, 0.2, 0.8), vec3(0.0, 0.8, 0.4), (lum - 0.25) / 0.25);
  if (lum < 0.75) return mix(vec3(0.0, 0.8, 0.4), vec3(1.0, 0.8, 0.0), (lum - 0.5) / 0.25);
  return mix(vec3(1.0, 0.8, 0.0), vec3(1.0, 0.2, 0.0), (lum - 0.75) / 0.25);
}

void main() {
  vec2 center = gl_PointCoord - 0.5;
  float dist = length(center);
  if (dist > 0.5) discard;

  float glow = 1.0 - smoothstep(0.0, 0.5, dist);
  glow = pow(glow, 2.0); // Tighter, less bleeding glow

  // Base purple
  vec3 baseColor = vec3(0.486, 0.227, 0.929);

  // Agent color mixing
  float agentMix = uPulseIntensity * (0.4 + 0.4 * sin(uTime * 3.0 + vDistFromCenter * 8.0));
  vec3 color = mix(baseColor, uActiveColor, agentMix);

  // Core brightness — visible but doesn't wash out text
  float coreBright = 1.0 - smoothstep(0.0, 2.5, vDistFromCenter);
  color *= 0.4 + coreBright * 0.5; // Brighter core, elegant falloff

  // Thermal crossfade
  float luminance = dot(color, vec3(0.299, 0.587, 0.114));
  luminance = clamp(luminance + vBrightness * 0.2, 0.0, 1.0);
  vec3 thermal = thermalColor(luminance);
  vec3 finalColor = mix(color, thermal, uThermalProgress);

  // Visible particles that work with bloom
  float alpha = glow * (0.35 + uPulseIntensity * 0.2);
  alpha *= 0.7 + 0.3 * sin(uTime * 0.8 + vDistFromCenter * 4.0);

  gl_FragColor = vec4(finalColor, alpha);
}
`;

const lineVertexShader = /* glsl */`
uniform float uTime;
uniform float uPulseIntensity;
varying float vAlpha;
void main() {
  vAlpha = 0.05 + uPulseIntensity * 0.08;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const lineFragmentShader = /* glsl */`
uniform float uThermalProgress;
varying float vAlpha;
void main() {
  vec3 baseColor = vec3(0.486, 0.227, 0.929);
  vec3 thermalLine = vec3(0.0, 0.8, 0.6);
  gl_FragColor = vec4(mix(baseColor, thermalLine, uThermalProgress), vAlpha);
}
`;

interface NeuralCoreProps {
  scrollProgress: number;
  activeAgent: number;
  thermalProgress: number;
  mousePosition: { x: number; y: number };
}

export default function NeuralCore({ scrollProgress, activeAgent, thermalProgress, mousePosition }: NeuralCoreProps) {
  const pointsRef = useRef<THREE.Points>(null);
  const linesRef = useRef<THREE.LineSegments>(null);
  const groupRef = useRef<THREE.Group>(null);

  const { geometry, lineGeometry } = useMemo(() => {
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const spherePoints = fibonacciSphere(PARTICLE_COUNT);

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const [x, y, z] = spherePoints[i];
      const r = CORE_RADIUS * (0.8 + Math.random() * 0.4);
      positions[i * 3] = x * r;
      positions[i * 3 + 1] = y * r;
      positions[i * 3 + 2] = z * r;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    // Agent connection lines
    const agentPos: [number, number, number][] = [];
    for (let i = 0; i < AGENTS.length; i++) {
      const angle = (i / AGENTS.length) * Math.PI * 2;
      const y = ((i / (AGENTS.length - 1)) * 1.6 - 0.8) * CORE_RADIUS * 0.5;
      const r = CORE_RADIUS * 0.85;
      agentPos.push([Math.cos(angle) * r, y, Math.sin(angle) * r]);
    }

    const lineVerts: number[] = [];
    for (let i = 0; i < agentPos.length; i++) {
      for (let j = i + 1; j < agentPos.length; j++) {
        lineVerts.push(...agentPos[i], ...agentPos[j]);
      }
    }
    for (const ap of agentPos) lineVerts.push(0, 0, 0, ...ap);

    const lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(lineVerts, 3));

    return { geometry: geo, lineGeometry: lineGeo };
  }, []);

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uScrollProgress: { value: 0 },
    uThermalProgress: { value: 0 },
    uActiveColor: { value: new THREE.Color('#7c3aed') },
    uPulseIntensity: { value: 0 },
  }), []);

  const lineUniforms = useMemo(() => ({
    uTime: { value: 0 },
    uThermalProgress: { value: 0 },
    uPulseIntensity: { value: 0 },
  }), []);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    uniforms.uTime.value = t;
    uniforms.uScrollProgress.value = scrollProgress;
    uniforms.uThermalProgress.value = thermalProgress;
    uniforms.uPulseIntensity.value = activeAgent >= 0 ? 0.3 + activeAgent * 0.05 : 0;

    if (activeAgent >= 0 && activeAgent < AGENTS.length) {
      uniforms.uActiveColor.value.copy(AGENT_COLORS[activeAgent]);
    }

    lineUniforms.uTime.value = t;
    lineUniforms.uThermalProgress.value = thermalProgress;
    lineUniforms.uPulseIntensity.value = uniforms.uPulseIntensity.value;

    if (groupRef.current) {
      const targetRotY = t * 0.06 + scrollProgress * Math.PI * 0.4;
      const targetRotX = Math.sin(t * 0.02) * 0.1;
      groupRef.current.rotation.y += (targetRotY - groupRef.current.rotation.y) * 0.04;
      groupRef.current.rotation.x += (targetRotX - groupRef.current.rotation.x) * 0.04;
    }
  });

  return (
    <group ref={groupRef}>
      <points ref={pointsRef} geometry={geometry}>
        <shaderMaterial
          vertexShader={vertexShader}
          fragmentShader={fragmentShader}
          uniforms={uniforms}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </points>
      <lineSegments ref={linesRef} geometry={lineGeometry}>
        <shaderMaterial
          vertexShader={lineVertexShader}
          fragmentShader={lineFragmentShader}
          uniforms={lineUniforms}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>
      {/* Subtle central glow */}
      <mesh>
        <sphereGeometry args={[CORE_RADIUS * 0.2, 32, 32]} />
        <meshBasicMaterial color="#7c3aed" transparent opacity={0.02 + scrollProgress * 0.03} />
      </mesh>
    </group>
  );
}
