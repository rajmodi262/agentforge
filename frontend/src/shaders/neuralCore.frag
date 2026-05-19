/* ═══════════════════════════════════════════════════════════════
   Neural Core — Custom GLSL Fragment Shader
   Handles: thermal vision, agent glow, particle rendering
   ═══════════════════════════════════════════════════════════════ */

uniform float uTime;
uniform float uThermalProgress;
uniform vec3 uActiveColor;
uniform float uPulseIntensity;
uniform float uScrollProgress;

varying float vBrightness;
varying float vDistFromCenter;
varying vec3 vWorldPosition;

// === THERMAL VISION COLOR RAMP ===
// Maps brightness (0→1) to thermal colors: Blue → Cyan → Green → Yellow → Red → White
vec3 thermalColor(float luminance) {
  if (luminance < 0.2) return mix(vec3(0.0, 0.0, 0.3), vec3(0.0, 0.2, 1.0), luminance / 0.2);
  if (luminance < 0.4) return mix(vec3(0.0, 0.2, 1.0), vec3(0.0, 1.0, 0.5), (luminance - 0.2) / 0.2);
  if (luminance < 0.6) return mix(vec3(0.0, 1.0, 0.5), vec3(1.0, 1.0, 0.0), (luminance - 0.4) / 0.2);
  if (luminance < 0.8) return mix(vec3(1.0, 1.0, 0.0), vec3(1.0, 0.3, 0.0), (luminance - 0.6) / 0.2);
  return mix(vec3(1.0, 0.3, 0.0), vec3(1.0, 1.0, 1.0), (luminance - 0.8) / 0.2);
}

void main() {
  // === CIRCULAR PARTICLE SHAPE ===
  vec2 center = gl_PointCoord - 0.5;
  float dist = length(center);
  if (dist > 0.5) discard; // Discard pixels outside circle
  
  // === SOFT GLOW FALLOFF ===
  float glow = 1.0 - smoothstep(0.0, 0.5, dist);
  glow = pow(glow, 1.5); // Sharpen the glow
  
  // === BASE COLOR (Neural Purple) ===
  vec3 baseColor = vec3(0.486, 0.227, 0.929); // #7c3aed
  
  // === AGENT COLOR MIXING ===
  float agentMix = uPulseIntensity * (0.5 + 0.5 * sin(uTime * 4.0 + vDistFromCenter * 10.0));
  vec3 agentGlow = mix(baseColor, uActiveColor, agentMix);
  
  // === DISTANCE-BASED BRIGHTNESS ===
  float coreBrightness = 1.0 - smoothstep(0.0, 2.5, vDistFromCenter);
  agentGlow *= 0.6 + coreBrightness * 0.8;
  
  // === PULSE WAVE ===
  float wave = sin(uTime * 2.0 - vDistFromCenter * 4.0) * 0.5 + 0.5;
  agentGlow += wave * uPulseIntensity * 0.3;
  
  // === THERMAL VISION CROSSFADE ===
  // Uses the Oryzo technique: uniform uThermalProgress (0→1) drives crossfade
  float luminance = dot(agentGlow, vec3(0.299, 0.587, 0.114));
  luminance += wave * 0.3; // Add animation to thermal
  vec3 thermal = thermalColor(clamp(luminance + vBrightness * 0.3, 0.0, 1.0));
  thermal *= 1.2; // Boost thermal brightness
  
  // Crossfade between normal and thermal
  vec3 finalColor = mix(agentGlow, thermal, uThermalProgress);
  
  // === FINAL OUTPUT ===
  float alpha = glow * (0.4 + uPulseIntensity * 0.5);
  alpha *= 0.8 + 0.2 * sin(uTime + vDistFromCenter * 6.0); // Subtle flicker
  
  gl_FragColor = vec4(finalColor, alpha);
}
