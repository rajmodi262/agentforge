/**
 * StartupOS AI — Design Tokens
 *
 * Single source of truth for all colors, typography, spacing, and
 * component styles. Change once here → updates everywhere.
 */

// ─────────── Colors ───────────
export const colors = {
  // Brand
  primary: '#7c3aed',
  primaryDark: '#6d28d9',
  primaryGlow: 'rgba(124, 58, 237, 0.15)',
  secondary: '#06b6d4',
  accent: '#f59e0b',

  // Accent
  cyan: '#06b6d4',
  emerald: '#10b981',
  amber: '#f59e0b',
  rose: '#ef4444',
  error: '#ef4444',

  // Neutrals
  white: '#ffffff',
  text: '#e2e8f0',
  textMuted: '#94a3b8',
  textDim: '#64748b',
  textDark: '#475569',

  // Surfaces
  bg: '#0a0a0f',
  bgPage: '#0a0a0f',
  bgCard: 'rgba(255,255,255,0.03)',
  bgCardHover: 'rgba(255,255,255,0.06)',
  bgInput: 'rgba(255,255,255,0.05)',
  border: 'rgba(255,255,255,0.07)',
  borderLight: 'rgba(255,255,255,0.1)',
  borderHover: 'rgba(255,255,255,0.15)',

  // Status
  successBg: 'rgba(16,185,129,0.15)',
  successText: '#10b981',
  errorBg: 'rgba(239,68,68,0.15)',
  errorText: '#ef4444',
  warningBg: 'rgba(245,158,11,0.15)',
  warningText: '#f59e0b',
} as const;

// ─────────── Gradients ───────────
export const gradients = {
  primary: 'linear-gradient(135deg, #7c3aed, #6d28d9)',
  hero: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
  bar: 'linear-gradient(90deg, #7c3aed, #06b6d4)',
  glass: 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
  background: 'linear-gradient(180deg, #0a0a0f 0%, #0f0a1a 100%)',
} as const;

// ─────────── Typography ───────────
export const typography = {
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
  fontFamilyMono: "'JetBrains Mono', 'Fira Code', monospace",

  // Sizes
  h1: '1.6rem',
  h2: '1.2rem',
  h3: '0.95rem',
  body: '0.85rem',
  small: '0.8rem',
  sm: '0.8rem', // Alias for small
  xs: '0.75rem',
  xxs: '0.7rem',

  // Weights
  bold: 700,
  semibold: 600,
  medium: 500,
  regular: 400,
  normal: 400,
} as const;

// ─────────── Spacing ───────────
export const spacing = {
  xs: '0.25rem',
  sm: '0.5rem',
  md: '0.75rem',
  lg: '1rem',
  xl: '1.25rem',
  xxl: '2rem',
  page: '2rem 2.5rem',
} as const;

// ─────────── Radii ───────────
export const radii = {
  sm: '0.4rem',
  md: '0.75rem',
  lg: '1rem',
  pill: '1rem',
  full: '50%',
} as const;

// ─────────── Component Styles ───────────

export const cardStyle: React.CSSProperties = {
  background: colors.bgCard,
  border: `1px solid ${colors.border}`,
  borderRadius: radii.lg,
  padding: spacing.xl,
};

export const metricStyle: React.CSSProperties = {
  fontSize: '1.8rem',
  fontWeight: typography.bold,
  margin: '0.5rem 0 0.2rem',
};

export const labelStyle: React.CSSProperties = {
  color: colors.textDim,
  fontSize: typography.xs,
  textTransform: 'uppercase' as const,
  letterSpacing: '0.05em',
};

export const selectStyle: React.CSSProperties = {
  padding: '0.4rem 0.6rem',
  background: colors.bgInput,
  border: `1px solid ${colors.borderLight}`,
  borderRadius: radii.sm,
  color: colors.text,
  fontSize: typography.small,
};

export const buttonPrimary: React.CSSProperties = {
  padding: '0.4rem 0.8rem',
  background: gradients.primary,
  border: 'none',
  borderRadius: radii.sm,
  color: colors.white,
  fontSize: typography.small,
  fontWeight: typography.semibold,
  cursor: 'pointer',
};

export const buttonGhost: React.CSSProperties = {
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  fontSize: '0.9rem',
  padding: '0 0.2rem',
};

export const tableHeaderStyle: React.CSSProperties = {
  padding: spacing.md,
  textAlign: 'left' as const,
  color: colors.textDim,
  fontWeight: typography.medium,
  fontSize: typography.xs,
  textTransform: 'uppercase' as const,
};

export const tableCellStyle: React.CSSProperties = {
  padding: '0.6rem 0.75rem',
};

export const statusBadge = (status: string): React.CSSProperties => ({
  padding: '0.15rem 0.5rem',
  borderRadius: radii.pill,
  fontSize: typography.xxs,
  fontWeight: typography.semibold,
  background: status === 'success' ? colors.successBg
    : status === 'error' ? colors.errorBg
    : colors.warningBg,
  color: status === 'success' ? colors.successText
    : status === 'error' ? colors.errorText
    : colors.warningText,
});

export const pageHeader: React.CSSProperties = {
  fontSize: typography.h1,
  fontWeight: typography.bold,
  margin: '0 0 0.3rem',
};

export const pageSubtitle: React.CSSProperties = {
  color: colors.textDim,
  fontSize: typography.body,
  margin: '0 0 2rem',
};
