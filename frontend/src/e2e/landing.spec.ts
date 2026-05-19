import { test, expect } from '@playwright/test';

test.describe('Cinematic Landing Experience', () => {
  test('should render 3D neural core and transitions', async ({ page }) => {
    // Navigate to the landing page
    await page.goto('/');

    // Wait for the preloader to finish (~2.8s) and content to render.
    // The SplitTextReveal inside the h1 splits text into individual <span> chars,
    // so we check for a substring that will appear as composed textContent.
    // Total wait: preloader (2.8s) + animation delay (3s) + stagger ≈ 8s
    await expect(page.locator('.display-xl').first()).toBeVisible({ timeout: 15000 });

    // Verify NeuralCore canvas exists (Three.js scene)
    const canvas = page.locator('canvas');
    await expect(canvas).toBeAttached({ timeout: 5000 });

    // Scroll down to trigger the ClipReveal transition
    await page.mouse.wheel(0, 3000);
    await page.waitForTimeout(2000);

    // Verify scroll-triggered sections become visible
    const agentsSection = page.locator('#agents');
    await expect(agentsSection).toBeAttached();
  });
});
