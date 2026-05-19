export function lerp(start: number, end: number, t: number): number {
  return start + (end - start) * t;
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function mapRange(value: number, inMin: number, inMax: number, outMin: number, outMax: number): number {
  return outMin + ((value - inMin) / (inMax - inMin)) * (outMax - outMin);
}

export function randomRange(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

export function fibonacciSphere(samples: number): Array<[number, number, number]> {
  const points: Array<[number, number, number]> = [];
  const phi = Math.PI * (Math.sqrt(5) - 1); // golden angle
  for (let i = 0; i < samples; i++) {
    const y = 1 - (i / (samples - 1)) * 2;
    const radius = Math.sqrt(1 - y * y);
    const theta = phi * i;
    points.push([Math.cos(theta) * radius, y, Math.sin(theta) * radius]);
  }
  return points;
}
