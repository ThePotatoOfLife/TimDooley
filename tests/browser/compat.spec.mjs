import { test, expect } from '@playwright/test';

const standardPages = [
  ['home', '/'],
  ['great-book', '/great-book/'],
  ['longform', '/politics/'],
  ['timeline', '/timeline/'],
];

for (const [name, path] of standardPages) {
  test(`${name} loads without page errors and stays inside the viewport`, async ({ page }) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));

    await page.goto(path, { waitUntil: 'domcontentloaded' });
    await expect(page.locator('body')).toBeVisible();
    await page.waitForTimeout(250);

    const overflow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));

    expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 2);
    expect(errors, `uncaught page errors on ${path}`).toEqual([]);
  });
}

test('standalone TTS exposes usable controls without requiring clipboard support', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.addInitScript(() => {
    try { Object.defineProperty(navigator, 'clipboard', { configurable: true, value: undefined }); } catch (_) {}
  });

  await page.goto('/tools/tts/', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#follow')).toBeVisible();
  await expect(page.locator('#play')).toBeVisible();
  await page.locator('#follow').click();
  expect(errors).toEqual([]);
});

test('world map reaches a stable shell even when advanced map resources are delayed', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));

  await page.goto('/world-map/', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#atlasApp')).toBeVisible();
  await expect(page.locator('#search')).toBeVisible();
  await expect(page.locator('#panelToggle')).toBeVisible();
  await page.waitForTimeout(500);

  expect(errors, 'world map shell should not throw before/while progressive map boot occurs').toEqual([]);
});
