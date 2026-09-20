import { defineConfig } from '@playwright/test';

const baseURL = process.env.POTATO_COMPAT_BASE_URL || 'http://127.0.0.1:4173';

export default defineConfig({
  testDir: './tests/browser',
  timeout: 30_000,
  expect: { timeout: 8_000 },
  fullyParallel: false,
  retries: 0,
  reporter: 'line',
  use: {
    baseURL,
    ignoreHTTPSErrors: true,
    reducedMotion: 'reduce',
  },
  projects: [
    { name: 'chromium-desktop', use: { browserName: 'chromium', viewport: { width: 1440, height: 900 } } },
    { name: 'firefox-desktop', use: { browserName: 'firefox', viewport: { width: 1440, height: 900 } } },
    { name: 'webkit-desktop', use: { browserName: 'webkit', viewport: { width: 1440, height: 900 } } },
    { name: 'chromium-phone', use: { browserName: 'chromium', viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
    { name: 'webkit-tablet', use: { browserName: 'webkit', viewport: { width: 834, height: 1112 }, isMobile: true, hasTouch: true } },
  ],
});
