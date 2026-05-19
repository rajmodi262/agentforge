/* ═══════════════════════════════════════════════════════════════
   Neural Core — Custom GLSL Vertex Shader
   Handles: particle breathing, scroll-driven explosion, agent activation
   ═══════════════════════════════════════════════════════════════ */

// Uniforms passed from JavaScript
uniform float uTime;
uniform float uScrollProgress;
uniform float uThermalProgress;    // 0.0 = normal → 1.0 = thermal vision
uniform float uExplosionProgress;  // 0.0 = sphere → 1.0 = exploded
uniform vec3 uActiveColor;         // Agent color to pulse
uniform float uPulseIntensity;     // Glow pulse strength

// Varyings → Fragment shader
varying float vBrightness;
varying float vDistFromCenter;
varying vec3 vWorldPosition;

void main() {
  vec3 pos = position;
  
  // === BREATHING EFFECT ===
  float breath = sin(uTime * 1.5 + pos.y * 3.0) * 0.02;
  pos *= 1.0 + breath;
  
  // === SCROLL-DRIVEN EXPLOSION ===
  // As uExplosionProgress increases, particles push outward
  vec3 explosionDir = normalize(pos);
  float explosionNoise = sin(pos.x * 10.0 + uTime) * cos(pos.z * 10.0 + uTime) * 0.5 + 0.5;
  pos += explosionDir * uExplosionProgress * 2.0 * (1.0 + explosionNoise);
  
  // === ORBIT ROTATION ===
  float angle = uTime * 0.3 + uScrollProgress * 3.14159;
  mat3 rotY = mat3(
    cos(angle), 0.0, sin(angle),
    0.0,        1.0, 0.0,
    -sin(angle), 0.0, cos(angle)
  );
  pos = rotY * pos;
  
  // === VARYINGS ===
  vDistFromCenter = length(position); // Original distance
  vBrightness = 0.5 + 0.5 * sin(uTime * 2.0 + length(position) * 5.0);
  vWorldPosition = pos;
  
  // === SIZE ATTENUATION ===
  vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
  gl_Position = projectionMatrix * mvPosition;
  
  // Point size with distance attenuation
  float size = 3.0 + uPulseIntensity * 2.0;
  size += sin(uTime * 3.0 + length(position) * 8.0) * 1.0;
  gl_PointSize = size * (200.0 / -mvPosition.z);
}
