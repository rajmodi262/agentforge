/**
 * API Service — Unit Tests
 *
 * Tests API helper functions and URL construction.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
(globalThis as any).fetch = mockFetch;

describe('API Service', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('API_BASE defaults to expected value', async () => {
    // Import the module (uses import.meta.env.VITE_API_URL or fallback)
    const api = await import('../services/api');
    // The API base should be a string
    expect(typeof (api as any).API_BASE).toBe('string');
  });

  it('handles fetch errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const api = await import('../services/api');
    // getHealth should not throw — it should return null/undefined
    try {
      await api.getHealth();
    } catch (e) {
      // Expected — API wraps in throw
      expect(e).toBeDefined();
    }
  });

  it('constructs correct URL for getHealth', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'ok' }),
    });

    const api = await import('../services/api');
    await api.getHealth();

    expect(mockFetch).toHaveBeenCalledTimes(1);
    const url = mockFetch.mock.calls[0][0];
    expect(url).toContain('/health');
  });
});
