/**
 * Design Tokens — Unit Tests
 *
 * Verifies token exports exist and have correct types.
 * This is the "canary" test that catches broken imports.
 */
import { describe, it, expect } from 'vitest';
import {
  colors, gradients, typography, spacing, radii,
  cardStyle, metricStyle, labelStyle, selectStyle,
  buttonPrimary, buttonGhost, statusBadge, pageHeader,
} from '../styles/tokens';

describe('Design Tokens', () => {
  it('exports all color tokens', () => {
    expect(colors.primary).toBe('#7c3aed');
    expect(colors.bgPage).toBe('#0a0a0f');
    expect(colors.text).toBe('#e2e8f0');
  });

  it('exports gradient strings', () => {
    expect(gradients.primary).toContain('linear-gradient');
    expect(gradients.hero).toContain('#06b6d4');
  });

  it('exports typography with correct font family', () => {
    expect(typography.fontFamily).toContain('Inter');
    expect(typography.bold).toBe(700);
  });

  it('exports spacing tokens', () => {
    expect(spacing.sm).toBe('0.5rem');
    expect(spacing.xl).toBe('1.25rem');
  });

  it('exports border radii', () => {
    expect(radii.full).toBe('50%');
  });

  it('cardStyle has correct structure', () => {
    expect(cardStyle.borderRadius).toBe(radii.lg);
    expect(cardStyle.padding).toBe(spacing.xl);
  });

  it('statusBadge returns correct colors', () => {
    const success = statusBadge('success');
    expect(success.color).toBe(colors.successText);

    const error = statusBadge('error');
    expect(error.color).toBe(colors.errorText);
  });
});
